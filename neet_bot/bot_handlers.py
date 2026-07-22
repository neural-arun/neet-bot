import json
import html
import re
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes
)

from config import TELEGRAM_BOT_TOKEN
import questions as qs
import db
import ai_analyzer
from pdf_report import generate_report

CHUNK = 8
COUNT_OPTIONS = [10, 15, 25, 45]
TIMER_PER_QUESTION = 1  # minutes per question

_sessions = {}
_jobs = {}  # sid -> job
_user_multi_select = {}  # user_id -> set of selected chapter names

MULTI_COUNT_OPTIONS = [10, 15, 25, 45]

SUBJECT_NAMES = {
    'biology': 'Biology',
    'physics': 'Physics',
    'chemistry': 'Chemistry'
}

SUBJECT_ICONS = {
    'biology': '🧬',
    'physics': '⚡',
    'chemistry': '🧪'
}

def _get_user_selected(user_id):
    if user_id not in _user_multi_select:
        _user_multi_select[user_id] = set()
    return _user_multi_select[user_id]

def _build_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton('🎲 Full Random Test (All Chapters)', callback_data='mode_all_random')],
        [InlineKeyboardButton('📘 Single Chapter Test', callback_data='mode_single')],
        [InlineKeyboardButton('🔀 Custom Multi-Chapter Test', callback_data='mode_multi')],
    ]
    return InlineKeyboardMarkup(keyboard)

def _build_chapter_keyboard(subject='biology', page=0):
    chapters = qs.get_chapter_list(subject)
    total_pages = (len(chapters) + CHUNK - 1) // CHUNK
    start = page * CHUNK
    end = min(start + CHUNK, len(chapters))
    keyboard = []
    for ch in chapters[start:end]:
        keyboard.append([InlineKeyboardButton(ch, callback_data=f'ch_{ch}')])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton('◀ Prev', callback_data=f'pp_{page-1}'))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton('Next ▶', callback_data=f'pp_{page+1}'))
    if nav:
        keyboard.append(nav)
    keyboard.append([InlineKeyboardButton('◀ Main Menu', callback_data='bc')])
    return InlineKeyboardMarkup(keyboard)

def _build_multi_chapter_keyboard(user_id, subject='biology', page=0):
    chapters = qs.get_chapter_list(subject)
    selected = _get_user_selected(user_id)
    total_pages = (len(chapters) + CHUNK - 1) // CHUNK
    start = page * CHUNK
    end = min(start + CHUNK, len(chapters))

    keyboard = []
    for idx in range(start, end):
        ch = chapters[idx]
        is_sel = ch in selected
        icon = '✅' if is_sel else '⬜'
        keyboard.append([InlineKeyboardButton(f"{icon} {ch}", callback_data=f'mct_{idx}_{page}')])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton('◀ Prev', callback_data=f'mcp_{page-1}'))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton('Next ▶', callback_data=f'mcp_{page+1}'))
    if nav:
        keyboard.append(nav)

    keyboard.append([
        InlineKeyboardButton('🗳 Select All (Page)', callback_data=f'mca_{page}'),
        InlineKeyboardButton('🧹 Clear All', callback_data=f'mcc_{page}')
    ])

    count = len(selected)
    btn_text = f"🚀 Start Test ({count} Selected)" if count > 0 else "🚀 Start Test (0 Selected)"
    keyboard.append([InlineKeyboardButton(btn_text, callback_data='mcs_done')])
    keyboard.append([InlineKeyboardButton('◀ Main Menu', callback_data='bc')])

    return InlineKeyboardMarkup(keyboard)

def _get_multi_count_keyboard():
    keyboard = []
    row = []
    for i, c in enumerate(MULTI_COUNT_OPTIONS):
        row.append(InlineKeyboardButton(f"{c} Qs", callback_data=f'mctcnt_{c}'))
        if (i + 1) % 2 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton('◀ Back to Chapter Selection', callback_data='mode_multi')])
    return InlineKeyboardMarkup(keyboard)

def _get_count_keyboard(chapter):
    keyboard = []
    row = []
    for i, c in enumerate(COUNT_OPTIONS):
        row.append(InlineKeyboardButton(str(c), callback_data=f'ct_{chapter}_{c}'))
        if (i + 1) % 2 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton('◀ Back to Chapters', callback_data='mode_single')])
    return InlineKeyboardMarkup(keyboard)

def _get_question_keyboard(session, q_index):
    total = session['total_q']
    keyboard = []
    labels = ['A', 'B', 'C', 'D']
    answer = session['answers'].get(q_index)
    for label in labels:
        marker = '●' if answer == label else '○'
        keyboard.append([InlineKeyboardButton(
            f"{marker} {label}",
            callback_data=f'a_{session["session_id"]}_{q_index}_{label}'
        )])
    nav_row = []
    if q_index > 0:
        nav_row.append(InlineKeyboardButton('◀ Prev', callback_data=f'n_{session["session_id"]}_{q_index-1}'))
    else:
        nav_row.append(InlineKeyboardButton(' ', callback_data='noop'))
    nav_row.append(InlineKeyboardButton('Submit', callback_data=f's_{session["session_id"]}'))
    if q_index < total - 1:
        nav_row.append(InlineKeyboardButton('Next ▶', callback_data=f'n_{session["session_id"]}_{q_index+1}'))
    else:
        nav_row.append(InlineKeyboardButton(' ', callback_data='noop'))
    keyboard.append(nav_row)
    return InlineKeyboardMarkup(keyboard)

LATEX_UNICODE = {
    '\\alpha': 'α', '\\beta': 'β', '\\gamma': 'γ', '\\delta': 'δ',
    '\\epsilon': 'ε', '\\varepsilon': 'ε', '\\theta': 'θ', '\\lambda': 'λ',
    '\\mu': 'μ', '\\pi': 'π', '\\rho': 'ρ', '\\sigma': 'σ', '\\tau': 'τ',
    '\\phi': 'ϕ', '\\omega': 'ω', '\\Delta': 'Δ', '\\Omega': 'Ω',
    '\\propto': '∝', '\\ge': '≥', '\\le': '≤', '\\neq': '≠', '\\approx': '≈',
    '\\times': '×', '\\div': '÷', '\\cdot': '·', '\\infty': '∞',
    '\\pm': '±', '\\sqrt': '√'
}

SUBSCRIPTS = {
    '0':'₀','1':'₁','2':'₂','3':'₃','4':'₄','5':'₅','6':'₆','7':'₇','8':'₈','9':'₉',
    '+':'₊','-':'₋','=':'₌','(':'₍',')':'₎',
    'a':'ₐ','e':'ₑ','h':'ₕ','i':'ᵢ','j':'ⱼ','k':'ₖ','l':'ₗ','m':'ₘ','n':'ₙ','o':'ₒ','p':'ₚ','r':'ᵣ','s':'ₛ','t':'ₜ','u':'ᵤ','v':'ᵥ','x':'ₓ'
}

SUPERSCRIPTS = {
    '0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹',
    '+':'⁺','-':'⁻','=':'⁼','(':'⁽',')':'⁾',
    'a':'ᵃ','b':'ᵇ','c':'ᶜ','d':'ᵈ','e':'ᵉ','f':'ᶠ','g':'ᵍ','h':'ʰ','i':'ⁱ','j':'ʲ','k':'ᵏ','l':'ˡ','m':'ᵐ','n':'ⁿ','o':'ᵒ','p':'ᵖ','r':'ʳ','s':'ˢ','t':'ᵗ','u':'ᵘ','v':'ᵛ','w':'ʷ','x':'ˣ','y':'ʸ','z':'ᶻ'
}

def _clean_option_text(s):
    if not s:
        return ""
    s = html.unescape(str(s))
    s = re.sub(r'^Q\d+:\s*', '', s)
    s = re.sub(r'<math[^>]*>(.*?)</math>', r'\1', s, flags=re.DOTALL)
    s = re.sub(r'<[^>]+>', '', s)

    s = s.replace('^circ', '°').replace('^\\circ', '°').replace('\\circ', '°')
    s = re.sub(r'\\+frac\{([^}]+)\}\{([^}]+)\}', r'(\1/\2)', s)
    s = re.sub(r'\\+text\{([^}]+)\}', r'\1', s)

    for k, v in LATEX_UNICODE.items():
        s = s.replace(k, v)

    def sub_repl(m):
        content = m.group(1) or m.group(2)
        return ''.join(SUBSCRIPTS.get(c, c) for c in content)

    def super_repl(m):
        content = m.group(1) or m.group(2)
        return ''.join(SUPERSCRIPTS.get(c, c) for c in content)

    s = re.sub(r'_\{([^}]+)\}|_([0-9a-z+\-=()])', sub_repl, s)
    s = re.sub(r'\^\{([^}]+)\}|\^([0-9a-z+\-=()])', super_repl, s)

    s = s.replace('$$', '').replace('$', '')
    s = s.replace('\\mathbf{A}', 'A').replace('\\mathbf{R}', 'R')
    s = s.replace('\\mathbf', '').replace('\\', '')
    s = s.replace('\u00a0', ' ').replace('\u200b', '')

    return s.strip()

def _format_options_text(opts):
    labels = ['A', 'B', 'C', 'D']
    lines = []
    for label in labels:
        val = opts.get(label) or opts.get(label.lower()) or ''
        val = _clean_option_text(val)
        lines.append(f"<b>{label}.</b> {html.escape(val)}")
    return '\n'.join(lines)

def _format_question_text(session, q_index):
    q = session['questions'][q_index]
    total = session['total_q']
    text = q['question']
    opts = q['options']
    chapter = q.get('chapter', session['chapter'])

    remaining = ''
    end = session.get('end_time')
    if end:
        diff = datetime.fromisoformat(end) - datetime.now()
        if diff.total_seconds() > 0:
            m, s = divmod(int(diff.total_seconds()), 60)
            remaining = f'  ⏱ {m}:{s:02d}'
        else:
            remaining = '  ⏱ 0:00'

    header = f"<b>Q.{q_index + 1}/{total}</b>  |  {html.escape(chapter)}{remaining}\n\n"
    body = html.escape(_clean_option_text(text)) + '\n\n' + _format_options_text(opts)

    return header + body

BOT_DESCRIPTIONS = {
    'biology': (
        "🧬 NEET Biology CBT Exam Master\n\n"
        "🚀 Practice 7,700+ NCERT line-by-line MCQs across 32 Biology chapters!\n"
        "📊 Get instant PDF Report Cards with AI Weak Area Diagnostics.\n"
        "🎲 Full Syllabus Random & Chapter Tests designed for NEET 2027."
    ),
    'physics': (
        "⚡ NEET Physics Numerical & Concept Master\n\n"
        "🚀 Solve 5,000+ NCERT & PYQ-based Physics MCQs across 20 chapters!\n"
        "📊 Get instant PDF Report Cards with AI Weak Area Diagnostics & clean formulas.\n"
        "🎲 Full Syllabus Random & Chapter Tests designed for NEET 2027."
    ),
    'chemistry': (
        "🧪 NEET Chemistry Reaction & Concept Master\n\n"
        "🚀 Practice 5,000+ NCERT MCQs for Organic, Inorganic & Physical Chemistry!\n"
        "📊 Get instant PDF Report Cards with AI Weak Area Diagnostics & chemical formulas.\n"
        "🎲 Full Syllabus Random & Chapter Tests designed for NEET 2027."
    )
}

BOT_SHORT_DESCRIPTIONS = {
    'biology': "🧬 Practice 7,700+ NCERT Biology MCQs with AI PDF Report Cards!",
    'physics': "⚡ Solve 5,000+ NEET Physics MCQs with AI PDF Report Cards!",
    'chemistry': "🧪 Master 5,000+ NEET Chemistry MCQs with AI PDF Report Cards!"
}

WELCOME_TEXTS = {
    'biology': (
        "🧬 <b>Welcome to NEET Biology Master Bot!</b> 🎓\n\n"
        "Targeting 360/360 in NEET Biology? You're in the right place!\n\n"
        "🔥 <b>What you get with this bot:</b>\n"
        "• <b>7,700+ NCERT Line-by-Line MCQs</b> across 32 chapters\n"
        "• <b>Instant PDF Report Card</b> sent to your chat after every test\n"
        "• <b>AI Diagnostic Evaluation</b> identifying your weak NCERT topics\n\n"
        "🎯 <b>Select a Practice Mode to Begin:</b>\n"
        "• <b>🎲 Full Random Test</b> — Sample across all 32 chapters\n"
        "• <b>📘 Single Chapter Test</b> — Target 1 specific chapter\n"
        "• <b>🔀 Custom Test</b> — Pick your custom chapter mix\n\n"
        "👇 <i>Tap an option below to start practicing!</i>"
    ),
    'physics': (
        "⚡ <b>Welcome to NEET Physics Master Bot!</b> 🎓\n\n"
        "Master numericals, formulas, and concepts to conquer NEET Physics!\n\n"
        "🔥 <b>What you get with this bot:</b>\n"
        "• <b>5,000+ Formula & PYQ MCQs</b> across 20 Physics chapters\n"
        "• <b>Clean Unicode Math & Formulas</b> (no ugly markup!)\n"
        "• <b>Instant PDF Report Card</b> with AI Weak Area Diagnostics\n\n"
        "🎯 <b>Select a Practice Mode to Begin:</b>\n"
        "• <b>🎲 Full Random Test</b> — Sample across all 20 Physics chapters\n"
        "• <b>📘 Single Chapter Test</b> — Focus on Mechanics, Optics, AC, etc.\n"
        "• <b>🔀 Custom Test</b> — Select custom chapter topics\n\n"
        "👇 <i>Tap an option below to start practicing!</i>"
    ),
    'chemistry': (
        "🧪 <b>Welcome to NEET Chemistry Master Bot!</b> 🎓\n\n"
        "Master Organic Reactions, Bonding, Thermodynamics & Equilibrium for NEET!\n\n"
        "🔥 <b>What you get with this bot:</b>\n"
        "• <b>5,000+ NCERT MCQs</b> across Organic, Inorganic & Physical Chemistry\n"
        "• <b>Clean Chemical Notation</b> (e.g. H₂SO₄, CH₃-CH=CH₂, sp³d²)\n"
        "• <b>Instant PDF Report Card</b> with AI Weak Area Diagnostics\n\n"
        "🎯 <b>Select a Practice Mode to Begin:</b>\n"
        "• <b>🎲 Full Random Test</b> — Sample across all 20 Chemistry chapters\n"
        "• <b>📘 Single Chapter Test</b> — Practice Reactions, Kinetics, Bonding, etc.\n"
        "• <b>🔀 Custom Test</b> — Build your custom chapter mix\n\n"
        "👇 <i>Tap an option below to start practicing!</i>"
    )
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.upsert_user(user.id, user.username or user.first_name)
    subject = context.bot_data.get('subject', 'biology')
    welcome_text = WELCOME_TEXTS.get(subject, WELCOME_TEXTS['biology'])

    await update.message.reply_html(
        welcome_text,
        reply_markup=_build_main_menu_keyboard()
    )

async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    subject = context.bot_data.get('subject', 'biology')
    subj_name = SUBJECT_NAMES.get(subject, 'Biology')

    if data == 'mode_all_random':
        all_ch = list(qs.get_chapter_list(subject))
        _user_multi_select[user_id] = set(all_ch)
        await query.edit_message_text(
            f"🎲 <b>Full Random {subj_name} Test</b>\n\n"
            f"Randomly samples questions across <b>all {len(all_ch)} chapters</b> of {subj_name} syllabus!\n\n"
            "How many questions would you like in this random test?",
            parse_mode='HTML',
            reply_markup=_get_multi_count_keyboard()
        )
        return

    if data == 'mode_single':
        pages = (len(qs.get_chapter_list(subject)) + CHUNK - 1) // CHUNK
        await query.edit_message_text(
            f"📚 <b>Select a chapter</b> (page 1/{pages})\n\n"
            "👇 Tap any chapter to start practicing:",
            parse_mode='HTML',
            reply_markup=_build_chapter_keyboard(subject, page=0)
        )
        return

    if data == 'mode_multi':
        pages = (len(qs.get_chapter_list(subject)) + CHUNK - 1) // CHUNK
        await query.edit_message_text(
            f"🔀 <b>Custom Multi-Chapter Test</b> (page 1/{pages})\n\n"
            "Tap chapters to toggle selection (✅ = selected), then tap <b>Start Test</b> below!",
            parse_mode='HTML',
            reply_markup=_build_multi_chapter_keyboard(user_id, subject, page=0)
        )
        return

    if data.startswith('mct_'):
        parts = data.split('_')
        idx = int(parts[1])
        page = int(parts[2])
        chapters = qs.get_chapter_list(subject)
        if 0 <= idx < len(chapters):
            ch = chapters[idx]
            selected = _get_user_selected(user_id)
            if ch in selected:
                selected.remove(ch)
            else:
                selected.add(ch)
        await query.edit_message_reply_markup(
            reply_markup=_build_multi_chapter_keyboard(user_id, subject, page)
        )
        return

    if data.startswith('mcp_'):
        page = int(data.split('_')[1])
        pages = (len(qs.get_chapter_list(subject)) + CHUNK - 1) // CHUNK
        await query.edit_message_text(
            f"🔀 <b>Custom Multi-Chapter Test</b> (page {page + 1}/{pages})\n\n"
            "Tap chapters to toggle selection, then tap <b>Start Test</b> below!",
            parse_mode='HTML',
            reply_markup=_build_multi_chapter_keyboard(user_id, subject, page)
        )
        return

    if data.startswith('mca_'):
        page = int(data.split('_')[1])
        chapters = qs.get_chapter_list(subject)
        start_idx = page * CHUNK
        end_idx = min(start_idx + CHUNK, len(chapters))
        selected = _get_user_selected(user_id)
        for ch in chapters[start_idx:end_idx]:
            selected.add(ch)
        await query.edit_message_reply_markup(
            reply_markup=_build_multi_chapter_keyboard(user_id, subject, page)
        )
        return

    if data.startswith('mcc_'):
        page = int(data.split('_')[1])
        _user_multi_select[user_id] = set()
        await query.edit_message_reply_markup(
            reply_markup=_build_multi_chapter_keyboard(user_id, subject, page)
        )
        return

    if data == 'mcs_done':
        selected = _get_user_selected(user_id)
        if not selected:
            await query.answer("Please select at least 1 chapter!", show_alert=True)
            return
        await query.edit_message_text(
            f"🔀 <b>Custom Test ({len(selected)} Chapters)</b>\n\n"
            "How many questions would you like in this test?",
            parse_mode='HTML',
            reply_markup=_get_multi_count_keyboard()
        )
        return

    if data.startswith('mctcnt_'):
        count = int(data.split('_')[1])
        selected = list(_get_user_selected(user_id))
        if not selected:
            await query.edit_message_text("No chapters selected. Start over with /start")
            return

        questions = qs.get_random_questions_multi(selected, count, subject)
        if not questions:
            await query.edit_message_text("No questions available for selected chapters.")
            return

        ch_summary = f"Custom {subj_name} Test ({len(selected)} Chapters)"
        sid = db.create_session(user_id, ch_summary, count)
        end_time = datetime.now() + timedelta(minutes=count * TIMER_PER_QUESTION)

        state = {
            'session_id': sid,
            'chapter': ch_summary,
            'selected_chapters': selected,
            'total_q': count,
            'questions': questions,
            'answers': {},
            'current_q': 0,
            'end_time': end_time.isoformat(),
            'chat_id': query.message.chat_id,
            'subject': subject
        }
        _sessions[sid] = state

        if context.job_queue:
            job = context.job_queue.run_once(
                _timer_submit,
                end_time,
                data=sid,
                name=f'submit_{sid}'
            )
            _jobs[sid] = job

        text = _format_question_text(state, 0)
        await query.edit_message_text(
            text, parse_mode='HTML',
            reply_markup=_get_question_keyboard(state, 0)
        )
        return

    if data.startswith('pp_'):
        page = int(data.split('_')[1])
        pages = (len(qs.get_chapter_list(subject)) + CHUNK - 1) // CHUNK
        await query.edit_message_text(
            f"📚 <b>Select a chapter</b> (page {page + 1}/{pages})\n\n"
            "👇 Tap any chapter to start practicing:",
            parse_mode='HTML',
            reply_markup=_build_chapter_keyboard(subject, page)
        )
        return

    if data == 'bc':
        await query.edit_message_text(
            f"<b>GPT {subj_name} Bot</b>\n\n"
            "🎯 <b>Choose your practice mode:</b>\n"
            "1️⃣ <b>Single Chapter Test</b> — Focus on one specific chapter.\n"
            "2️⃣ <b>Custom Multi-Chapter Test</b> — Pick multiple chapters for a custom test!\n\n"
            "👇 <b>Select a mode to begin:</b>",
            parse_mode='HTML',
            reply_markup=_build_main_menu_keyboard()
        )
        return

    if data.startswith('ch_'):
        chapter = data[3:]
        await query.edit_message_text(
            f"📘 <b>{html.escape(chapter)}</b>\n\n"
            "How many questions will you crush today?\n"
            "💪 <i>Every question you solve brings you one step closer to that MBBS seat.</i>",
            parse_mode='HTML',
            reply_markup=_get_count_keyboard(chapter)
        )
        return

    if data.startswith('ct_'):
        parts = data.split('_', 2)
        chapter = parts[1]
        count = int(parts[2])

        questions = qs.get_random_questions(chapter, count, subject)
        if not questions:
            await query.edit_message_text("No questions available for this chapter.")
            return

        sid = db.create_session(user_id, chapter, count)
        end_time = datetime.now() + timedelta(minutes=count * TIMER_PER_QUESTION)

        state = {
            'session_id': sid,
            'chapter': chapter,
            'total_q': count,
            'questions': questions,
            'answers': {},
            'current_q': 0,
            'end_time': end_time.isoformat(),
            'chat_id': query.message.chat_id,
            'subject': subject
        }
        _sessions[sid] = state

        if context.job_queue:
            job = context.job_queue.run_once(
                _timer_submit,
                end_time,
                data=sid,
                name=f'submit_{sid}'
            )
            _jobs[sid] = job

        text = _format_question_text(state, 0)
        await query.edit_message_text(
            text, parse_mode='HTML',
            reply_markup=_get_question_keyboard(state, 0)
        )
        return

    await query.edit_message_text("Unknown option.")

async def answer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'noop':
        return

    parts = data.split('_')
    action = parts[0]

    if action == 'a':
        sid = int(parts[1])
        q_idx = int(parts[2])
        label = parts[3]
        state = _sessions.get(sid)
        if not state:
            await query.edit_message_text("Session expired. Start a new test with /start")
            return
        state['answers'][q_idx] = label

        q_data = state['questions'][q_idx]
        correct_letter = q_data['answer']
        is_correct = 1 if label == correct_letter else 0
        opts_json = json.dumps(q_data['options'])

        db.save_answer(
            sid, q_idx, q_data['question'],
            label, correct_letter, opts_json, is_correct
        )

        if is_correct:
            await query.answer('✅ Correct!', show_alert=False)
        else:
            opts = q_data['options']
            correct_text = opts.get(correct_letter, '')
            await query.answer(f'❌ Wrong! Correct: {correct_letter}. {correct_text[:80]}', show_alert=False)

        next_q = q_idx + 1
        if next_q < state['total_q']:
            state['current_q'] = next_q
            await query.edit_message_text(
                _format_question_text(state, next_q),
                parse_mode='HTML',
                reply_markup=_get_question_keyboard(state, next_q)
            )
        else:
            await _show_submit_prompt(query, sid)

    elif action == 'n':
        sid = int(parts[1])
        q_idx = int(parts[2])
        state = _sessions.get(sid)
        if not state:
            await query.edit_message_text("Session expired. Start a new test with /start")
            return
        state['current_q'] = q_idx
        await query.edit_message_text(
            _format_question_text(state, q_idx),
            parse_mode='HTML',
            reply_markup=_get_question_keyboard(state, q_idx)
        )

    elif action == 's':
        sid = int(parts[1])
        await _show_submit_prompt(query, sid)

    elif action == 'cf':
        sid = int(parts[1])
        await _finalize_submit(context.bot, query.message.chat_id, sid)

    elif action == 'rev':
        sid = int(parts[1])
        state = _sessions.get(sid)
        if not state:
            await query.edit_message_text("Session expired.")
            return
        unanswered = [i for i in range(state['total_q']) if i not in state['answers']]
        go_to = unanswered[0] if unanswered else 0
        state['current_q'] = go_to
        await query.edit_message_text(
            _format_question_text(state, go_to),
            parse_mode='HTML',
            reply_markup=_get_question_keyboard(state, go_to)
        )

async def _show_submit_prompt(query, sid):
    state = _sessions.get(sid)
    if not state:
        await query.edit_message_text("Session expired.")
        return

    ans_count = len(state['answers'])
    total = state['total_q']
    unans_count = total - ans_count

    msg = f"📋 <b>Test Summary</b> — {html.escape(state['chapter'])}\n\n"
    msg += f"✅ Answered: <b>{ans_count}/{total}</b>\n"
    if unans_count > 0:
        msg += f"⚠️ Unanswered: <b>{unans_count}</b>\n\n"
        msg += "Are you sure you want to submit now?"
    else:
        msg += "\n🎉 All questions answered! Ready to submit?"

    keyboard = [
        [InlineKeyboardButton("✅ Confirm & Submit", callback_data=f'cf_{sid}')],
    ]
    if unans_count > 0:
        keyboard.append([InlineKeyboardButton("🔍 Review Unanswered", callback_data=f'rev_{sid}')])
    keyboard.append([InlineKeyboardButton("◀ Back to Questions", callback_data=f'n_{sid}_{state["current_q"]}')])

    await query.edit_message_text(msg, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

async def _timer_submit(context: ContextTypes.DEFAULT_TYPE):
    sid = context.job.data
    state = _sessions.get(sid)
    if not state:
        return
    bot = context.bot
    chat_id = state['chat_id']
    await bot.send_message(chat_id, "⏰ <b>Time's up!</b> Auto-submitting your test...", parse_mode='HTML')
    await _finalize_submit(bot, chat_id, sid)

async def _finalize_submit(bot, chat_id, sid):
    job = _jobs.pop(sid, None)
    if job:
        job.schedule_removal()

    state = _sessions.get(sid)
    if not state:
        return

    chapter = state['chapter']
    total = state['total_q']
    questions = state['questions']
    answers_map = state['answers']
    subject = state.get('subject', 'biology')

    correct = 0
    wrong = 0
    unanswered = 0
    wrong_answers_list = []

    for i, q in enumerate(questions):
        user_ans = answers_map.get(i)
        correct_ans = q['answer'].upper()

        if user_ans is None:
            unanswered += 1
            opts = q['options']
            c_val = opts.get(correct_ans) or opts.get(correct_ans.lower()) or ''
            wrong_answers_list.append({
                'question': q['question'],
                'user_answer': 'Not answered',
                'correct_answer': f"{correct_ans}. {c_val}"
            })
        elif user_ans.upper() == correct_ans:
            correct += 1
        else:
            wrong += 1
            opts = q['options']
            u_val = opts.get(user_ans) or opts.get(user_ans.lower()) or ''
            c_val = opts.get(correct_ans) or opts.get(correct_ans.lower()) or ''
            wrong_answers_list.append({
                'question': q['question'],
                'user_answer': f"{user_ans}. {u_val}",
                'correct_answer': f"{correct_ans}. {c_val}"
            })

    db.finish_session(sid)
    db.update_session_score(sid, len(answers_map), correct)

    status_msg = await bot.send_message(
        chat_id,
        "🔄 <i>Analyzing your test results & generating AI evaluation... Please wait (~10s)</i>",
        parse_mode='HTML'
    )

    ai_text = await ai_analyzer.analyze_performance_async(
        chapter, correct, total, wrong_answers_list, subject=subject
    )

    bot_title = f"GPT {subject.upper()} BOT"
    pdf_bytes = generate_report(
        chapter=chapter,
        correct=correct,
        total=total,
        questions=questions,
        answers=answers_map,
        ai_analysis=ai_text,
        wrong=wrong,
        unanswered=unanswered,
        title=bot_title
    )

    await bot.delete_message(chat_id, status_msg.message_id)

    marks = correct * 4 - wrong * 1
    max_marks = total * 4
    pct = (marks / max_marks * 100) if max_marks else 0

    score_msg = (
        f"🎯 <b>Test Completed!</b> — <i>{html.escape(chapter)}</i>\n\n"
        f"📊 <b>Score:</b> <code>{marks}/{max_marks}</code> ({pct:.0f}%)\n"
        f"✅ Correct: <b>{correct}</b> (+4)\n"
        f"❌ Wrong: <b>{wrong}</b> (-1)\n"
        f"⭕ Unanswered: <b>{unanswered}</b>\n\n"
        "📄 <i>Your detailed report card PDF with AI weak area diagnostics is attached below!</i>"
    )

    filename = f"{subject}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    await bot.send_document(
        chat_id,
        document=pdf_bytes,
        filename=filename,
        caption=score_msg,
        parse_mode='HTML'
    )

    _sessions.pop(sid, None)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data
    if data.startswith(('a_', 'n_', 's_', 'cf_', 'rev_', 'noop')):
        await answer_callback(update, context)
    else:
        await start_callback(update, context)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    import logging
    logging.warning(f"Telegram handler caught error: {context.error}")

async def post_init(application: Application):
    subject = application.bot_data.get('subject', 'biology')
    bot = application.bot
    desc = BOT_DESCRIPTIONS.get(subject, BOT_DESCRIPTIONS['biology'])
    short_desc = BOT_SHORT_DESCRIPTIONS.get(subject, BOT_SHORT_DESCRIPTIONS['biology'])

    try:
        await bot.set_my_description(desc)
        await bot.set_my_short_description(short_desc)
    except Exception as e:
        import logging
        logging.warning(f"Could not set Telegram bot description for {subject}: {e}")

def build_app(token=None, subject='biology'):
    bot_token = token or TELEGRAM_BOT_TOKEN
    app = Application.builder().token(bot_token).post_init(post_init).build()
    app.bot_data['subject'] = subject
    app.add_error_handler(error_handler)
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    return app
