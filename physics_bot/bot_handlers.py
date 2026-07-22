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

CHUNK = 8
COUNT_OPTIONS = [10, 15, 25, 45]
TIMER_PER_QUESTION = 1  # minutes per question

CHAPTERS = qs.get_chapter_list()

_sessions = {}
_jobs = {}  # sid -> job
_user_multi_select = {}  # user_id -> set of selected chapter names

MULTI_COUNT_OPTIONS = [10, 15, 25, 45, 90]

def _get_user_selected(user_id):
    if user_id not in _user_multi_select:
        _user_multi_select[user_id] = set()
    return _user_multi_select[user_id]

def _build_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton('📘 Single Chapter Test', callback_data='mode_single')],
        [InlineKeyboardButton('🔀 Custom Multi-Chapter Test', callback_data='mode_multi')],
    ]
    return InlineKeyboardMarkup(keyboard)

def _build_chapter_keyboard(page=0):
    chapters = qs.get_chapter_list()
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

def _build_multi_chapter_keyboard(user_id, page=0):
    chapters = qs.get_chapter_list()
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
        if (i + 1) % 3 == 0:
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


def _clean_option_text(s):
    s = s.replace('$\\mathbf{A}$', '**A**').replace('$\\mathbf{R}$', '**R**')
    s = s.replace('$\\mathbf{A}', '**A**').replace('$\\mathbf{R}', '**R**')
    s = re.sub(r'\$\\mathbf\{([^}]+)\}', r'**\1**', s)
    s = s.replace('$$', '').replace('$', '')
    return s

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

    body = ''
    if '\\begin{array}' in text:
        body = _format_column_question(text)
    elif 'Assertion A' in text or 'Assertion' in text:
        body = _format_assertion_question(text)
    elif 'Statement I' in text or 'Statement II' in text:
        body = _format_statement_question(text)
    else:
        body = html.escape(text)

    body += '\n\n' + _format_options_text(opts)

    return header + body


def _format_column_question(text):
    import re

    def _strip_latex(s):
        s = re.sub(r'\\text\s*\{([^}]*)\}', r'\1', s)
        s = re.sub(r'\\hline\s*', '', s)
        s = re.sub(r'\\begin\{array\}\[?[^\]]*\]?\{[^}]*\}', '', s)
        s = re.sub(r'\\end\{array\}', '', s)
        s = re.sub(r'\\begin\{array\}\{.*?\}', '', s)
        s = re.sub(r'&\s*', ' ', s)
        s = re.sub(r'\\\\\s*', ' ', s)
        s = re.sub(r'\{[clr|]+\}', ' ', s)
        s = re.sub(r'\s+', ' ', s)
        return s.strip()

    def _simple_text(s):
        s = _strip_latex(s)
        s = re.sub(r'\\\(|\\\)', '', s)
        s = re.sub(r'\\text\{([^}]*)\}', r'\1', s)
        return re.sub(r'\s+', ' ', s).strip()

    parts = text.split(r'\begin{array}')
    before = _simple_text(parts[0])
    result = html.escape(before) + '\n'

    if len(parts) > 1:
        array_part = parts[1].split(r'\end{array}')[0]

        rows = re.findall(
            r'([A-D])\.\s*&\s*(.*?)\s*&\s*(I{1,3}V?|IV)\.\s*&\s*(.*?)\s*(?=\\\\|\\Z)',
            array_part, re.DOTALL
        )
        if not rows:
            rows = re.findall(
                r'\(?([a-d])\)?\s*&\s*(.*?)\s*&\s*\(?(i{1,3}v?|iv)\)?\s*&\s*(.*?)\s*(?=\\\\|\\Z)',
                array_part, re.DOTALL
            )

        if rows:
            for letter, left, roman, right in rows:
                left_clean = _strip_latex(left)
                right_clean = _strip_latex(right)
                result += f"  <b>{letter.upper()}.</b> {html.escape(left_clean)}\n"
                result += f"  <b>{roman.upper()}.</b> {html.escape(right_clean)}\n"
            result += '\n'
        else:
            raw = _strip_latex(array_part)
            if raw:
                result += html.escape(raw) + '\n\n'

        after_text = parts[1].split(r'\end{array}')[1] if r'\end{array}' in parts[1] else ''
        if after_text:
            result += html.escape(_simple_text(after_text))

    return result


def _format_statement_question(text):
    lines = text.split('\n')
    result_parts = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            result_parts.append('')
        elif stripped.startswith('Statement II'):
            result_parts.append(f"✅ <b>Statement II:</b> {html.escape(stripped.split(':', 1)[1].strip())}")
        elif stripped.startswith('Statement I'):
            result_parts.append(f"✅ <b>Statement I:</b> {html.escape(stripped.split(':', 1)[1].strip())}")
        else:
            result_parts.append(html.escape(stripped))
    return '\n'.join(result_parts)


def _format_assertion_question(text):
    lines = text.split('\n')
    result_parts = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            result_parts.append('')
        elif stripped.startswith('Assertion A'):
            result_parts.append(f"🧪 <b>Assertion (A):</b> {html.escape(stripped.split(':', 1)[1].strip())}")
        elif stripped.startswith('Assertion'):
            result_parts.append(f"🧪 <b>Assertion:</b> {html.escape(stripped.split(':', 1)[1].strip())}")
        elif stripped.startswith('Reason R'):
            result_parts.append(f"🔬 <b>Reason (R):</b> {html.escape(stripped.split(':', 1)[1].strip())}")
        elif stripped.startswith('Reason'):
            result_parts.append(f"🔬 <b>Reason:</b> {html.escape(stripped.split(':', 1)[1].strip())}")
        else:
            result_parts.append(html.escape(stripped))
    return '\n'.join(result_parts)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.upsert_user(user.id, user.username or user.first_name)
    await update.message.reply_text(
        f"🧬 <b>Welcome {html.escape(user.first_name or 'Future Doctor')} to GPT Biology Bot!</b>\n"
        "<i>Practice. Analyze. Improve. • By NeuralArun</i>\n\n"
        "Your ultimate companion to master <b>NCERT Biology</b> with <b>8,000+ authentic MCQs</b> across all 32 chapters — built specifically for NEET CBT aspirants.\n\n"
        "🌟 <b>Key Features:</b>\n"
        "• <b>Dual Test Modes:</b> Single Chapter OR Custom Multi-Chapter Mocks\n"
        "• <b>Real Exam Marking:</b> +4 for Correct | -1 for Wrong\n"
        "• <b>Instant PDF Reports:</b> Detailed answer keys + AI Weak Area Evaluation\n"
        "• <b>Class 11 & Class 12:</b> Complete coverage of latest NEET syllabus\n\n"
        "📖 <b>Quick 4-Step Guide:</b>\n"
        "1️⃣ Pick a Practice Mode below\n"
        "2️⃣ Choose Chapter(s) & Question Count\n"
        "3️⃣ Tap A / B / C / D to answer\n"
        "4️⃣ Get your instant PDF Report Card!\n\n"
        "👇 <b>Select a mode to launch your practice test:</b>",
        parse_mode='HTML',
        reply_markup=_build_main_menu_keyboard()
    )

async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = update.effective_user.id

    if data == 'mode_single':
        await query.edit_message_text(
            "📚 <b>Single Chapter Test</b>\n\n"
            "👇 Tap any chapter to start practicing:",
            parse_mode='HTML',
            reply_markup=_build_chapter_keyboard(0)
        )
        return

    if data == 'mode_multi':
        await query.edit_message_text(
            "🔀 <b>Custom Multi-Chapter Test</b>\n\n"
            "Select the chapters you want to include in your practice test below.\n"
            "Tap chapters to toggle them (✅/⬜), then tap <b>Start Test</b>.",
            parse_mode='HTML',
            reply_markup=_build_multi_chapter_keyboard(user_id, 0)
        )
        return

    if data.startswith('mct_'):
        parts = data.split('_')
        idx = int(parts[1])
        page = int(parts[2])
        ch = CHAPTERS[idx]
        selected = _get_user_selected(user_id)
        if ch in selected:
            selected.remove(ch)
        else:
            selected.add(ch)
        await query.edit_message_reply_markup(
            reply_markup=_build_multi_chapter_keyboard(user_id, page)
        )
        return

    if data.startswith('mcp_'):
        page = int(data.split('_')[1])
        pages = (len(CHAPTERS) + CHUNK - 1) // CHUNK
        await query.edit_message_text(
            f"🔀 <b>Custom Multi-Chapter Test</b> (page {page + 1}/{pages})\n\n"
            "Tap chapters to toggle them (✅/⬜), then tap <b>Start Test</b>.",
            parse_mode='HTML',
            reply_markup=_build_multi_chapter_keyboard(user_id, page)
        )
        return

    if data.startswith('mca_'):
        page = int(data.split('_')[1])
        start_idx = page * CHUNK
        end_idx = min(start_idx + CHUNK, len(CHAPTERS))
        selected = _get_user_selected(user_id)
        for i in range(start_idx, end_idx):
            selected.add(CHAPTERS[i])
        await query.edit_message_reply_markup(
            reply_markup=_build_multi_chapter_keyboard(user_id, page)
        )
        return

    if data.startswith('mcc_'):
        page = int(data.split('_')[1])
        selected = _get_user_selected(user_id)
        selected.clear()
        await query.edit_message_reply_markup(
            reply_markup=_build_multi_chapter_keyboard(user_id, page)
        )
        return

    if data == 'mcs_done':
        selected = _get_user_selected(user_id)
        if not selected:
            await query.answer("⚠️ Please select at least 1 chapter!", show_alert=True)
            return

        ch_list_str = "\n".join([f"• {ch}" for ch in sorted(list(selected))[:10]])
        if len(selected) > 10:
            ch_list_str += f"\n... and {len(selected) - 10} more"

        await query.edit_message_text(
            f"🎯 <b>Custom Multi-Chapter Test</b>\n\n"
            f"<b>{len(selected)} Chapters Selected:</b>\n"
            f"{ch_list_str}\n\n"
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

        questions = qs.get_random_questions_multi(selected, count)
        if not questions:
            await query.edit_message_text("No questions available for selected chapters.")
            return

        ch_summary = f"Custom Test ({len(selected)} Chapters)"
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
        pages = (len(CHAPTERS) + CHUNK - 1) // CHUNK
        await query.edit_message_text(
            f"📚 <b>Select a chapter</b> (page {page + 1}/{pages})\n\n"
            "👇 Tap any chapter to start practicing:",
            parse_mode='HTML',
            reply_markup=_build_chapter_keyboard(page)
        )
        return

    if data == 'bc':
        await query.edit_message_text(
            "🧬 <b>NEET Biology Practice Bot</b>\n\n"
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

        questions = qs.get_random_questions(chapter, count)
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
    answered = len(state['answers'])
    total = state['total_q']
    btn = InlineKeyboardMarkup([
        [InlineKeyboardButton('✅ Yes, Submit', callback_data=f'cf_{sid}')],
        [InlineKeyboardButton('🔍 Review my answers', callback_data=f'rev_{sid}')],
    ])
    await query.edit_message_text(
        f"📋 <b>Confirm Submission</b>\n\n"
        f"Answered: <b>{answered}/{total}</b>\n"
        f"Unanswered: <b>{total - answered}</b>\n\n"
        "Tap <b>Review</b> to go back and check your answers before submitting.",
        parse_mode='HTML',
        reply_markup=btn
    )

async def _timer_submit(context: ContextTypes.DEFAULT_TYPE):
    sid = context.job.data
    state = _sessions.get(sid)
    if not state:
        return
    chat_id = state.get('chat_id')
    if not chat_id:
        return
    await context.bot.send_message(
        chat_id,
        "⏰ <b>Time's up!</b> Submitting your test now...",
        parse_mode='HTML'
    )
    await _finalize_submit(context.bot, chat_id, sid)

async def _finalize_submit(bot, chat_id, sid):
    state = _sessions.get(sid)
    if not state:
        return

    if sid in _jobs:
        _jobs[sid].schedule_removal()
        del _jobs[sid]

    await bot.send_message(
        chat_id,
        "⏳ <b>Your report is being generated...</b>\n\n"
        "Analysing your answers and preparing AI-powered insights. "
        "You will receive your PDF report shortly!",
        parse_mode='HTML'
    )

    total = state['total_q']
    correct = 0
    wrong = 0
    unanswered = 0
    wrong_answers = []

    for i, q in enumerate(state['questions']):
        user_ans = state['answers'].get(i, '')
        correct_letter = q['answer']
        opts = q['options']
        q_ch = q.get('chapter', state['chapter'])
        if user_ans == correct_letter:
            correct += 1
        elif user_ans:
            wrong += 1
            wrong_answers.append({
                'question': f"[{q_ch}] {q['question']}",
                'user_answer': f"{user_ans}. {opts.get(user_ans, '')}",
                'correct_answer': f"{correct_letter}. {opts.get(correct_letter, '')}"
            })
        else:
            unanswered += 1
            wrong_answers.append({
                'question': f"[{q_ch}] {q['question']}",
                'user_answer': 'Not answered',
                'correct_answer': f"{correct_letter}. {opts.get(correct_letter, '')}"
            })

    marks = correct * 4 - wrong * 1
    max_marks = total * 4
    pct = marks / max_marks * 100 if max_marks else 0

    db.finish_session(sid)
    db.update_session_score(sid, total, correct)

    from ai_analyzer import analyze_performance
    analysis = analyze_performance(state['chapter'], correct, total, wrong_answers)

    from pdf_report import generate_report
    pdf_buf = generate_report(state['chapter'], correct, total, state['questions'], state['answers'], analysis,
                               wrong=wrong, unanswered=unanswered)

    emoji = '🎉' if pct >= 80 else '👍' if pct >= 60 else '💪'
    result_text = (
        f"{emoji} <b>Test Complete!</b>\n\n"
        f"📘 <b>{state['chapter']}</b>\n"
        f"{'─'*28}\n"
        f"📊  Score:    <b>{marks}/{max_marks}</b>  ({pct:.0f}%)\n"
        f"✅  Correct:  <b>{correct}</b>\n"
        f"❌  Wrong:    <b>{wrong}</b>\n"
        f"⭕  Unattempted: <b>{unanswered}</b>\n"
        f"{'─'*28}\n\n"
        "📄 Your <b>PDF report</b> is below:\n"
        "• Every wrong question with the correct answer\n"
        "• AI-powered analysis of your weak areas\n"
        "• A personalized revision plan\n\n"
        "Type <b>/start</b> anytime to practice another chapter!"
    )
    await bot.send_message(chat_id, result_text, parse_mode='HTML')

    await bot.send_document(
        chat_id,
        document=pdf_buf,
        filename=f"NEET_Report_{state['chapter'].replace(' ', '_')}.pdf",
        caption=f"NEET Biology — {state['chapter']} — {marks}/{max_marks} — AI Analysis Report"
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

def build_app():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_error_handler(error_handler)
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    return app
