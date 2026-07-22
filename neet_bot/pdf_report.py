import html
import re
import unicodedata
from io import BytesIO
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT

DARK_BLUE = colors.HexColor('#1e3a8a')
LIGHT_BLUE = colors.HexColor('#eff6ff')
TEXT_DARK = colors.HexColor('#1f2937')
TEXT_MUTED = colors.HexColor('#6b7280')
ACCENT_GREEN = colors.HexColor('#16a34a')
ACCENT_RED = colors.HexColor('#dc2626')
ACCENT_ORANGE = colors.HexColor('#d97706')
LIGHT_GRAY = colors.HexColor('#f9fafb')
MED_GRAY = colors.HexColor('#e5e7eb')

UNICODE_MAP = {
    'α': 'alpha', 'β': 'beta', 'γ': 'gamma', 'δ': 'delta',
    'ε': 'epsilon', 'θ': 'theta', 'λ': 'lambda', 'π': 'pi',
    'σ': 'sigma', 'τ': 'tau', 'ω': 'omega', 'Δ': 'Delta',
    '→': '->', '←': '<-', '↔': '<->', '⇒': '=>',
    '–': '-', '—': '-', '…': '...', '’': "'", '‘': "'",
    '“': '"', '”': '"', '•': '*', 'µ': 'μ'
}

def _sanitize_text(text):
    if not text:
        return ""
    text = html.unescape(str(text))
    text = re.sub(r'^Q\d+:\s*', '', text)
    text = re.sub(r'<math[^>]*>(.*?)</math>', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'<(?!\/?(b|i|sub|sup|font))[^>]+>', '', text)

    text = text.replace('^circ', '°').replace('^\\circ', '°').replace('\\circ', '°')
    text = re.sub(r'\\+frac\{([^}]+)\}\{([^}]+)\}', r'(\1/\2)', text)
    text = re.sub(r'\\+text\{([^}]+)\}', r'\1', text)

    for k, v in UNICODE_MAP.items():
        text = text.replace(k, v)

    text = text.replace('\\mathbf{A}', '<b>A</b>').replace('\\mathbf{R}', '<b>R</b>')
    text = text.replace('\\mathbf', '').replace('\\', '')

    text = re.sub(r'_\{([^}]+)\}|_([0-9a-zA-Z+\-=()])', r'<sub>\1\2</sub>', text)
    text = re.sub(r'\^\{([^}]+)\}|\^([0-9a-zA-Z+\-=()])', r'<sup>\1\2</sup>', text)

    text = text.replace('$$', '').replace('$', '')
    text = text.replace('\u00a0', ' ').replace('\u200b', '')
    return text.strip()

def _render_analysis(text, body_style, heading_style, sub_style):
    lines = text.split('\n')
    elements = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line:
            continue
        if line.startswith('## '):
            heading = _sanitize_text(line[3:].strip())
            elements.append(Paragraph(heading, heading_style))
            elements.append(Spacer(1, 2*mm))
            continue
        if line.startswith('### ') or line.startswith('# '):
            heading = _sanitize_text(line.lstrip('#').strip())
            elements.append(Paragraph(heading, sub_style))
            elements.append(Spacer(1, 1*mm))
            continue

        if line.startswith('- ') or line.startswith('* '):
            content = _sanitize_text(line[2:].strip())
            content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', content)
            elements.append(Paragraph(f"  •  {content}", body_style))
            continue

        line_san = _sanitize_text(line)
        line_san = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line_san)
        elements.append(Paragraph(line_san, body_style))

    return elements

def _build_question_table(i, q, user_ans, correct_letter, opts, styles):
    is_correct = user_ans == correct_letter if user_ans else False
    is_attempted = bool(user_ans)

    if is_correct:
        q_score = '+4'
        badge = '✅ Correct'
        badge_color = ACCENT_GREEN
    elif is_attempted:
        q_score = '-1'
        badge = '❌ Wrong'
        badge_color = ACCENT_RED
    else:
        q_score = '0'
        badge = '⭕ Unattempted'
        badge_color = ACCENT_ORANGE

    q_style, opt_style, badg_style, score_style = styles

    q_text = _sanitize_text(q['question'])
    q_ch = _sanitize_text(q.get('chapter', ''))
    ch_badge = f"<font color='{DARK_BLUE.hexval()}'><b>[{html.escape(q_ch)}]</b></font> " if q_ch else ""
    header = [
        Paragraph(f"<b>Q{i+1}.</b>  {ch_badge}{q_text}", q_style),
        Paragraph(f"<font color='{badge_color.hexval()}'><b>{badge}</b></font>", badg_style),
    ]
    rows = [header]

    for letter, text in opts.items():
        text = _sanitize_text(text)
        lu = letter.lower()
        is_selected = lu == user_ans.lower() if user_ans else False
        is_correct_opt = letter.upper() == correct_letter.upper()

        if is_selected and is_correct_opt:
            line = f"[✔]  <b>{letter.upper()}.</b>  {text}   <b>(Your Answer - Correct)</b>"
            ostyle = opt_style['green']
        elif is_selected:
            line = f"[X]  <b>{letter.upper()}.</b>  {text}   <b>(Your Answer - Wrong)</b>"
            ostyle = opt_style['red']
        elif is_correct_opt:
            line = f"[ ]  <b>{letter.upper()}.</b>  {text}   <b>(Correct Answer)</b>"
            ostyle = opt_style['green']
        else:
            line = f"[ ]  <b>{letter.upper()}.</b>  {text}"
            ostyle = opt_style['normal']

        rows.append([Paragraph(line, ostyle), Paragraph('', badg_style)])

    score_row = [
        Paragraph(f"<b>Marks:</b> {q_score}", score_style),
        Paragraph('', badg_style),
    ]
    rows.append(score_row)

    col_w = [140*mm, 24*mm]
    t = Table(rows, colWidths=col_w)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), LIGHT_BLUE),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 0.5, MED_GRAY),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, MED_GRAY),
        ('LINEABOVE', (0, -1), (-1, -1), 0.5, MED_GRAY),
        ('BACKGROUND', (0, -1), (-1, -1), LIGHT_GRAY),
    ]))
    return t

def generate_report(chapter, correct, total, questions, answers, ai_analysis, wrong=0, unanswered=0, title="GPT BIOLOGY BOT"):
    marks = correct * 4 - wrong * 1
    max_marks = total * 4
    pct = marks / max_marks * 100 if max_marks else 0

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=16*mm, rightMargin=16*mm,
                            topMargin=14*mm, bottomMargin=14*mm)

    title_style = ParagraphStyle('T1', fontSize=16, spaceAfter=2,
                                  alignment=TA_CENTER, textColor=DARK_BLUE,
                                  fontName='Helvetica-Bold')
    chapter_style = ParagraphStyle('T2', fontSize=13, spaceAfter=2,
                                    alignment=TA_CENTER, textColor=TEXT_DARK,
                                    fontName='Helvetica')
    date_style = ParagraphStyle('T3', fontSize=8, alignment=TA_CENTER,
                                 textColor=TEXT_MUTED, spaceAfter=4)
    section_style = ParagraphStyle('Sec', fontName='Helvetica-Bold',
                                    fontSize=13, spaceBefore=8, spaceAfter=4,
                                    textColor=DARK_BLUE)
    ai_head_style = ParagraphStyle('AiH', fontName='Helvetica-Bold',
                                    fontSize=12, spaceBefore=4, spaceAfter=2,
                                    textColor=ACCENT_GREEN)
    ai_sub_style = ParagraphStyle('AiSub', fontName='Helvetica-Bold',
                                   fontSize=10, spaceBefore=3, spaceAfter=1,
                                   textColor=DARK_BLUE)
    body_style = ParagraphStyle('Body', fontSize=10, leading=15,
                                 alignment=TA_JUSTIFY, spaceAfter=3,
                                 textColor=TEXT_DARK)
    q_style = ParagraphStyle('QS', fontSize=10, leading=15, textColor=TEXT_DARK)
    badg_style = ParagraphStyle('Badge', fontSize=8, leading=14,
                                 alignment=TA_RIGHT, textColor=TEXT_DARK)
    opt_normal = ParagraphStyle('ON', fontSize=9, leading=13,
                                 leftIndent=4, textColor=TEXT_DARK)
    opt_green = ParagraphStyle('OG', fontSize=9, leading=13,
                                leftIndent=4, textColor=ACCENT_GREEN)
    opt_red = ParagraphStyle('OR', fontSize=9, leading=13,
                              leftIndent=4, textColor=ACCENT_RED)
    opt_styles = {'normal': opt_normal, 'green': opt_green, 'red': opt_red}
    score_style = ParagraphStyle('Sc', fontSize=9, leading=13,
                                  textColor=TEXT_DARK, fontName='Helvetica-Bold')
    footer_style = ParagraphStyle('Ft', fontSize=8, alignment=TA_CENTER,
                                   textColor=colors.HexColor('#aaaaaa'))

    q_styles = (q_style, opt_styles, badg_style, score_style)
    elements = []

    # ── 1. Header ──
    elements.append(Paragraph(title, title_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=DARK_BLUE,
                                spaceBefore=2, spaceAfter=4))
    elements.append(Paragraph(f"<b>{_sanitize_text(chapter)}</b>", chapter_style))
    elements.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y - %H:%M')}", date_style))
    elements.append(Spacer(1, 3*mm))

    # ── 2. Performance Summary Card ──
    stat_data = [
        [
            Paragraph("<b>SCORE</b>", ParagraphStyle('S1', fontSize=8, alignment=TA_CENTER, textColor=TEXT_MUTED)),
            Paragraph("<b>ACCURACY</b>", ParagraphStyle('S2', fontSize=8, alignment=TA_CENTER, textColor=TEXT_MUTED)),
            Paragraph("<b>CORRECT</b>", ParagraphStyle('S3', fontSize=8, alignment=TA_CENTER, textColor=TEXT_MUTED)),
            Paragraph("<b>WRONG</b>", ParagraphStyle('S4', fontSize=8, alignment=TA_CENTER, textColor=TEXT_MUTED)),
            Paragraph("<b>UNATTEMPTED</b>", ParagraphStyle('S5', fontSize=8, alignment=TA_CENTER, textColor=TEXT_MUTED)),
        ],
        [
            Paragraph(f"<b>{marks}/{max_marks}</b>", ParagraphStyle('V1', fontSize=12, alignment=TA_CENTER, textColor=DARK_BLUE, fontName='Helvetica-Bold')),
            Paragraph(f"<b>{pct:.0f}%</b>", ParagraphStyle('V2', fontSize=12, alignment=TA_CENTER, textColor=DARK_BLUE, fontName='Helvetica-Bold')),
            Paragraph(f"<b>{correct}</b>", ParagraphStyle('V3', fontSize=12, alignment=TA_CENTER, textColor=ACCENT_GREEN, fontName='Helvetica-Bold')),
            Paragraph(f"<b>{wrong}</b>", ParagraphStyle('V4', fontSize=12, alignment=TA_CENTER, textColor=ACCENT_RED, fontName='Helvetica-Bold')),
            Paragraph(f"<b>{unanswered}</b>", ParagraphStyle('V5', fontSize=12, alignment=TA_CENTER, textColor=ACCENT_ORANGE, fontName='Helvetica-Bold')),
        ]
    ]

    stat_table = Table(stat_data, colWidths=[32*mm, 32*mm, 32*mm, 32*mm, 36*mm])
    stat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BLUE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BOX', (0, 0), (-1, -1), 1, DARK_BLUE),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, MED_GRAY),
    ]))
    elements.append(stat_table)
    elements.append(Spacer(1, 6*mm))

    # ── 3. FULL TEST PAPER & ANSWER KEY (FIRST) ──
    elements.append(HRFlowable(width="100%", thickness=1, color=DARK_BLUE,
                                spaceBefore=2, spaceAfter=2))
    elements.append(Paragraph("1. FULL TEST PAPER & ANSWER KEY", section_style))
    elements.append(Spacer(1, 2*mm))

    for i, q in enumerate(questions):
        user_ans = answers.get(i, '')
        correct_letter = q['answer']
        opts = q['options']
        elements.append(_build_question_table(i, q, user_ans, correct_letter, opts, q_styles))
        elements.append(Spacer(1, 3*mm))

    elements.append(Spacer(1, 6*mm))

    # ── 4. AI WEAK AREA DIAGNOSTIC & FOCUS PLAN (AT THE LAST) ──
    elements.append(HRFlowable(width="100%", thickness=1, color=ACCENT_GREEN,
                                spaceBefore=4, spaceAfter=2))
    elements.append(Paragraph("2. AI WEAK AREA DIAGNOSTIC & FOCUS PLAN", section_style))
    elements.append(Spacer(1, 2*mm))

    if ai_analysis:
        analysis_elems = _render_analysis(ai_analysis, body_style, ai_head_style, ai_sub_style)
        analysis_data = [[analysis_elems]]
        analysis_table = Table(analysis_data, colWidths=[164*mm])
        analysis_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BLUE),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 1, ACCENT_GREEN),
        ]))
        elements.append(analysis_table)
    else:
        elements.append(Paragraph("No weak area analysis available.", body_style))

    # ── 5. Footer ──
    elements.append(Spacer(1, 8*mm))
    elements.append(HRFlowable(width="40%", thickness=0.5, color=MED_GRAY,
                                spaceBefore=0, spaceAfter=3))
    elements.append(Paragraph(f"Generated by {title} — NeuralArun", footer_style))

    doc.build(elements)
    return buf.getvalue()
