import re
import html
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from io import BytesIO
from datetime import datetime


import unicodedata

DARK_BLUE = colors.HexColor('#1a237e')
LIGHT_BLUE = colors.HexColor('#e8eaf6')
SOFT_BG = colors.HexColor('#fafafa')
ACCENT_GREEN = colors.HexColor('#2e7d32')
ACCENT_RED = colors.HexColor('#c62828')
ACCENT_ORANGE = colors.HexColor('#e65100')
LIGHT_GRAY = colors.HexColor('#f5f5f5')
MED_GRAY = colors.HexColor('#e0e0e0')
TEXT_DARK = colors.HexColor('#333333')
TEXT_MUTED = colors.HexColor('#666666')
WHITE = colors.white
ANALYSIS_BG = colors.HexColor('#f8f9fc')

UNICODE_MAP = {
    '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4',
    '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9',
    '₊': '+', '₋': '-', '₌': '=', '₍': '(', '₎': ')',
    '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
    '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9',
    '⁺': '+', '⁻': '-', '⁼': '=', '⁽': '(', '⁾': ')',
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
    for k, v in UNICODE_MAP.items():
        text = text.replace(k, v)
    text = unicodedata.normalize('NFKD', text)
    return text

def _render_analysis(text, body_style, heading_style, sub_style):
    text = _sanitize_text(text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    lines = text.split('\n')
    elements = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line:
            continue

        if re.match(r'^#{1,3}\s+', line):
            label = re.sub(r'^#{1,3}\s+', '', line)
            elements.append(Spacer(1, 3*mm))
            elements.append(Paragraph(label, heading_style))
            elements.append(Spacer(1, 1*mm))
            continue

        if line.startswith('**') and line.endswith('**') and len(line) > 6:
            elements.append(Spacer(1, 2*mm))
            elements.append(Paragraph(line.strip('*').strip(), sub_style))
            continue

        if line.startswith('- ') or line.startswith('* '):
            content = line[2:].strip()
            content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', content)
            elements.append(Paragraph(f"  •  {content}", body_style))
            continue

        line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
        elements.append(Paragraph(line, body_style))

    return elements


def _build_question_table(i, q, user_ans, correct_letter, opts, styles):
    is_correct = user_ans == correct_letter
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
            line = f"▸  {letter.upper()}.  {text}   <b>✓ Your answer</b>"
            ostyle = opt_style['green']
        elif is_selected:
            line = f"▸  {letter.upper()}.  {text}   <b>✗ Your answer</b>"
            ostyle = opt_style['red']
        elif is_correct_opt:
            line = f"▸  {letter.upper()}.  {text}   <b>✓ Correct</b>"
            ostyle = opt_style['green']
        else:
            line = f"   {letter.upper()}.  {text}"
            ostyle = opt_style['normal']

        rows.append([Paragraph(line, ostyle), Paragraph('', badg_style)])

    score_row = [
        Paragraph(f"<b>Score:</b>  {q_score}", score_style),
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


def generate_report(chapter, correct, total, questions, answers, ai_analysis, wrong=0, unanswered=0):
    marks = correct * 4 - wrong * 1
    max_marks = total * 4
    pct = marks / max_marks * 100 if max_marks else 0

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=16*mm, rightMargin=16*mm,
                            topMargin=14*mm, bottomMargin=14*mm)

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('T1', fontSize=16, spaceAfter=2,
                                  alignment=TA_CENTER, textColor=DARK_BLUE,
                                  fontName='Helvetica-Bold')
    chapter_style = ParagraphStyle('T2', fontSize=13, spaceAfter=2,
                                    alignment=TA_CENTER, textColor=TEXT_DARK,
                                    fontName='Helvetica')
    date_style = ParagraphStyle('T3', fontSize=8, alignment=TA_CENTER,
                                 textColor=TEXT_MUTED, spaceAfter=4)
    section_style = ParagraphStyle('Sec', fontName='Helvetica-Bold',
                                    fontSize=13, spaceBefore=8, spaceAfter=3,
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
    elements.append(Paragraph("GPT BIOLOGY BOT", title_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=DARK_BLUE,
                                spaceBefore=2, spaceAfter=4))
    elements.append(Paragraph(f"<b>{chapter}</b>", chapter_style))
    elements.append(Paragraph(
        f"Test Report  •  {datetime.now().strftime('%d %b %Y, %I:%M %p')}",
        date_style))
    elements.append(Spacer(1, 5*mm))

    # ── 2. Score Card ──
    sc = ACCENT_GREEN if pct >= 60 else ACCENT_ORANGE
    score_data = [
        [Paragraph('<b>Score</b>', ParagraphStyle('h', fontSize=11, textColor=WHITE, alignment=TA_CENTER)),
         Paragraph(f'<b>{marks} / {max_marks}</b>', ParagraphStyle('v', fontSize=11, textColor=sc, alignment=TA_CENTER))],
        [Paragraph('<b>Accuracy</b>', ParagraphStyle('hl', fontSize=10, textColor=DARK_BLUE, alignment=TA_CENTER)),
         Paragraph(f'<b>{pct:.0f}%</b>', ParagraphStyle('vl', fontSize=10, textColor=sc, alignment=TA_CENTER))],
        [Paragraph('<b>Correct</b>', ParagraphStyle('hl', fontSize=10, textColor=DARK_BLUE, alignment=TA_CENTER)),
         Paragraph(f'<b>{correct}</b>', ParagraphStyle('vl', fontSize=10, textColor=ACCENT_GREEN, alignment=TA_CENTER))],
        [Paragraph('<b>Wrong</b>', ParagraphStyle('hl', fontSize=10, textColor=DARK_BLUE, alignment=TA_CENTER)),
         Paragraph(f'<b>{wrong}</b>', ParagraphStyle('vl', fontSize=10, textColor=ACCENT_RED, alignment=TA_CENTER))],
        [Paragraph('<b>Unattempted</b>', ParagraphStyle('hl', fontSize=10, textColor=DARK_BLUE, alignment=TA_CENTER)),
         Paragraph(f'<b>{unanswered}</b>', ParagraphStyle('vl', fontSize=10, textColor=ACCENT_ORANGE, alignment=TA_CENTER))],
    ]
    st = Table(score_data, colWidths=[55*mm, 55*mm])
    st.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BLUE),
        ('BACKGROUND', (0, 1), (0, -1), LIGHT_BLUE),
        ('BACKGROUND', (1, 1), (1, -1), WHITE),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, MED_GRAY),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(st)
    elements.append(Spacer(1, 5*mm))

    # ── 3. AI Analysis ──
    elements.append(HRFlowable(width="100%", thickness=0.5, color=MED_GRAY,
                                spaceBefore=2, spaceAfter=2))
    elements.append(Paragraph("AI ANALYSIS", section_style))
    elements.append(Spacer(1, 2*mm))

    if ai_analysis:
        analysis_elements = _render_analysis(ai_analysis, body_style, ai_head_style, ai_sub_style)
        if analysis_elements:
            analysis_table = Table([[e] for e in analysis_elements], colWidths=[168*mm])
            analysis_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), ANALYSIS_BG),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('BOX', (0, 0), (-1, -1), 0.5, MED_GRAY),
            ]))
            elements.append(analysis_table)
        else:
            elements.append(Paragraph(ai_analysis, body_style))
    else:
        elements.append(Paragraph("No analysis available.", body_style))
    elements.append(Spacer(1, 5*mm))

    # ── 4. Answer Key ──
    elements.append(HRFlowable(width="100%", thickness=0.5, color=MED_GRAY,
                                spaceBefore=2, spaceAfter=2))
    elements.append(Paragraph("ANSWER KEY", section_style))
    elements.append(Spacer(1, 2*mm))

    for i, q in enumerate(questions):
        user_ans = answers.get(i, '')
        correct_letter = q['answer']
        opts = q['options']
        elements.append(_build_question_table(i, q, user_ans, correct_letter, opts, q_styles))
        elements.append(Spacer(1, 3*mm))

    # ── 5. Footer ──
    elements.append(Spacer(1, 8*mm))
    elements.append(HRFlowable(width="40%", thickness=0.5, color=MED_GRAY,
                                spaceBefore=0, spaceAfter=3))
    elements.append(Paragraph("Generated by GPT Biology Bot — NeuralArun", footer_style))

    doc.build(elements)
    buf.seek(0)
    return buf
