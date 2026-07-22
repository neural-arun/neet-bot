from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_BASE_URL

client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

MODEL = 'gpt-4o-mini'

def analyze_performance(chapter, correct, total, wrong_answers):
    if not wrong_answers:
        return "Perfect score. No mistakes to analyze. Keep up the great work."

    wrong_details = []
    for i, wa in enumerate(wrong_answers, 1):
        wrong_details.append(
            f"Q{i}: {wa['question']}\n"
            f"  Your answer: {wa['user_answer']}\n"
            f"  Correct answer: {wa['correct_answer']}"
        )

    prompt = (
        "You are a NEET Biology tutor giving a detailed performance analysis. "
        "Use simple labels as headings (like ## Mistakes Overview, ## Weak Areas, ## Study Plan). "
        "Use **bold** for key terms only.\n\n"
        f"Chapter tested: {chapter}\n"
        f"Score: {correct}/{total} ({correct/total*100:.0f}%)\n\n"
        "Write these 3 sections:\n\n"
        "## Mistakes Overview\n"
        "For every wrong question, write 2-3 sentences: "
        "(a) what the student likely confused, "
        "(b) the correct concept in simple terms, "
        "(c) a memory tip or mnemonic.\n\n"
        "## Weak Areas\n"
        "Be very detailed and specific here. Do NOT just list 2-3 broad topics. "
        "For each weak topic:\n"
        "- Name the specific subtopic or concept the student struggles with.\n"
        "- Explain why it was missed — common misconceptions, similar-looking terms, or tricky distinctions.\n"
        "- Mention the exact NCERT chapter and section number where this concept is explained.\n"
        "- Give one clear, simple way to remember it differently.\n\n"
        "## Study Plan\n"
        "Give 3-4 actionable steps. For each step:\n"
        "- What specific topic to study.\n"
        "- How to study it (e.g., draw a table comparing X and Y, make a flowchart, write mnemonics).\n"
        "- How many practice questions to attempt and from which source.\n"
        "- Include revision strategy like spaced repetition or active recall.\n\n"
        "Wrong answers:\n"
        + "\n\n".join(wrong_details)
    )

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.3,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI analysis temporarily unavailable. Error: {e}"
