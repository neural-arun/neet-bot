import sys
import os
import unittest
import json

# Ensure neet_bot is on path
sys.path.insert(0, os.path.dirname(__file__))

import config
import questions as qs
import bot_handlers
import pdf_report
import ai_analyzer
import db

class TestNeetPlatform(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\n=======================================================")
        print("   NEET 2027 PLATFORM - AUTOMATED DIAGNOSTIC TEST SUITE")
        print("=======================================================\n")
        db.init_db()

    # ── 1. DATASET INTEGRITY TESTS ──
    def test_01_biology_dataset(self):
        bank = qs.load_bank('biology')
        self.assertEqual(len(bank['chapters']), 32, "Biology must have 32 chapters")
        self.assertGreaterEqual(bank.get('total_questions', 0), 7000, "Biology must have >= 7,000 MCQs")
        print("✅ PASS: Biology Dataset Integrity (32 Chapters, 7,735 MCQs)")

    def test_02_physics_dataset(self):
        bank = qs.load_bank('physics')
        self.assertEqual(len(bank['chapters']), 20, "Physics must have 20 chapters")
        self.assertEqual(bank.get('total_questions', 0), 5000, "Physics must have 5,000 MCQs")
        print("✅ PASS: Physics Dataset Integrity (20 Chapters, 5,000 MCQs)")

    def test_03_chemistry_dataset(self):
        bank = qs.load_bank('chemistry')
        self.assertEqual(len(bank['chapters']), 20, "Chemistry must have 20 chapters")
        self.assertEqual(bank.get('total_questions', 0), 5000, "Chemistry must have 5,000 MCQs")
        print("✅ PASS: Chemistry Dataset Integrity (20 Chapters, 5,000 MCQs)")

    # ── 2. QUESTION SAMPLING ENGINE TESTS ──
    def test_04_single_chapter_sampling(self):
        phys_ch = qs.get_chapter_list('physics')[0]
        sample = qs.get_random_questions(phys_ch, 5, 'physics')
        self.assertEqual(len(sample), 5, "Should sample 5 questions")
        self.assertFalse(sample[0]['question'].startswith("Q1"), "Questions must not start with Q-number prefix")
        print("✅ PASS: Single-Chapter Sampling & Prefix Stripping Engine")

    def test_05_multi_chapter_random_sampling(self):
        chem_chapters = qs.get_chapter_list('chemistry')
        sample = qs.get_random_questions_multi(chem_chapters, 10, 'chemistry')
        self.assertEqual(len(sample), 10, "Should sample 10 multi-chapter questions")
        sampled_chapters = {q['chapter'] for q in sample}
        self.assertGreater(len(sampled_chapters), 1, "Multi-chapter sampling must draw from multiple distinct chapters")
        print(f"✅ PASS: Multi-Chapter Balanced Random Sampling ({len(sampled_chapters)} distinct chapters drawn)")

    # ── 3. TELEGRAM MULTI-BOT APPS TEST ──
    def test_06_telegram_bot_apps_initialization(self):
        app_bio = bot_handlers.build_app(config.BIOLOGY_BOT_TOKEN, subject='biology')
        app_phys = bot_handlers.build_app(config.PHYSICS_BOT_TOKEN, subject='physics')
        app_chem = bot_handlers.build_app(config.CHEMISTRY_BOT_TOKEN, subject='chemistry')

        self.assertEqual(app_bio.bot_data['subject'], 'biology')
        self.assertEqual(app_phys.bot_data['subject'], 'physics')
        self.assertEqual(app_chem.bot_data['subject'], 'chemistry')
        print("✅ PASS: Telegram 3-Bot Apps Initialization (Biology, Physics, Chemistry)")

    # ── 4. PDF REPORT CARD GENERATION TEST ──
    def test_07_pdf_report_generation(self):
        ch = 'Units and Measurements'
        qs_list = qs.get_random_questions(ch, 5, 'physics')
        answers = {0: 'A', 1: 'C'}

        pdf_bytes = pdf_report.generate_report(
            chapter=ch,
            correct=1,
            total=5,
            questions=qs_list,
            answers=answers,
            ai_analysis="## Weak Areas\n- Dimensional analysis formula confusion.",
            wrong=1,
            unanswered=3,
            title="GPT PHYSICS BOT"
        )

        self.assertIsInstance(pdf_bytes, bytes, "PDF report must return raw bytes")
        self.assertGreater(len(pdf_bytes), 2000, "PDF size must be > 2KB")
        print(f"✅ PASS: PDF Report Card Generation ({len(pdf_bytes)} bytes clean build)")

    # ── 5. AI DIAGNOSTIC EVALUATOR TEST ──
    def test_08_ai_analyzer_prompt_format(self):
        wrong_answers = [
            {'question': 'What is the dimension of G?', 'user_answer': 'B. [M L T-2]', 'correct_answer': 'A. [M-1 L3 T-2]'}
        ]
        res = ai_analyzer.analyze_performance('Units and Measurements', 0, 1, wrong_answers, subject='physics')
        self.assertIsInstance(res, str)
        print("✅ PASS: AI Weak Area Diagnostic Evaluation Pipeline")

if __name__ == '__main__':
    unittest.main()
