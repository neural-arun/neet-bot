import asyncio
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_BASE_URL

client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
MODEL = 'gpt-4o-mini'

def analyze_performance(chapter, correct, total, wrong_answers, subject='biology'):
    if not wrong_answers:
        return "🎉 **PERFECT SCORE!** You answered 100% of questions correctly. Excellent mastery of this topic!"

    wrong_details = []
    for i, wa in enumerate(wrong_answers, 1):
        wrong_details.append(
            f"Question {i}: {wa['question']}\n"
            f"  Student Choice: {wa['user_answer']}\n"
            f"  Correct Answer: {wa['correct_answer']}"
        )

    prompt = (
        f"You are an expert NEET {subject.upper()} Master Diagnostic Mentor.\n"
        "Analyze ONLY the student's missed/unattempted questions below.\n"
        "DO NOT solve or explain the questions line by line. Instead, diagnose the student's core conceptual weak areas and provide an actionable focus plan.\n\n"
        f"Subject: NEET {subject.upper()}\n"
        f"Test Topic: {chapter}\n"
        f"Score: {correct}/{total} ({correct/total*100:.0f}%)\n\n"
        "Provide your evaluation using these exact markdown headers:\n\n"
        "## Core Weak Topics & Sub-Concepts\n"
        "- Identify 2-3 specific NCERT subtopics/concepts where the student lost marks.\n"
        "- Explain why these mistakes happened (e.g. formula confusion, unit error, conceptual trap).\n\n"
        "## Key Misconceptions & Traps\n"
        "- Point out the exact misconceptions that led to the wrong choices.\n\n"
        "## Actionable NCERT Focus Plan\n"
        "- List 3 high-yield NCERT revision points and practice steps for the student before their next test.\n\n"
        "Missed/Unattempted Questions List:\n"
        + "\n\n".join(wrong_details)
    )

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.3,
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI evaluation temporarily offline ({e}). Review the answer key above to analyze missed questions."

async def analyze_performance_async(chapter, correct, total, wrong_answers, subject='biology'):
    return await asyncio.to_thread(analyze_performance, chapter, correct, total, wrong_answers, subject)
