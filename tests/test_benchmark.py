"""Behavioral checks for the frozen dataset and scoring contract."""

import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from world_legal_bench.dataset import load_questions, load_answers, messages_for, read_jsonl, validate_release
from world_legal_bench.metrics import score
from world_legal_bench.parser import extract_final_choice


class ReleaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.questions = load_questions(ROOT)
        cls.answers = load_answers(ROOT)

    def test_frozen_release(self):
        report = validate_release(ROOT)
        self.assertEqual((report["cases"], report["jurisdictions"], report["languages"]), (720, 12, 9))

    def test_prompt_export_only_uses_question_and_options(self):
        q = self.questions[0]
        poisoned = {**q, "answer": "SECRET_GOLD", "source_text": "SECRET_SOURCE"}
        messages = messages_for(poisoned)
        self.assertEqual(messages, messages_for(q))
        self.assertNotIn("SECRET_", json.dumps(messages))
        self.assertEqual(len(messages), 2)
        for label, value in q["choices"].items():
            self.assertIn(f"{label}. {value}", messages[1]["content"])

    def test_gold_smoke_test_and_equal_country_weight(self):
        preds = [{"id": a["id"], "prediction": a["answer"]} for a in self.answers]
        result = score(self.questions, self.answers, preds)
        self.assertEqual(result["accuracy"], 100)
        self.assertEqual(result["macro_accuracy"], 100)
        self.assertEqual(result["country_gap"], 0)
        self.assertTrue(result["complete"])

    def test_reference_selection_profile_is_reproducible_without_model_calls(self):
        selected = read_jsonl(ROOT / "provenance/selection.jsonl")
        result = score(self.questions, self.answers,
                       [{"id": r["id"], "prediction": r["reference_choice"]} for r in selected])
        self.assertEqual((result["correct"], result["incorrect"], result["invalid"]), (128, 592, 0))
        self.assertAlmostEqual(result["accuracy"], 100 * 128 / 720)
        self.assertAlmostEqual(result["macro_accuracy"], result["accuracy"])

    def test_partial_scores_withhold_full_benchmark_metrics(self):
        one = [{"id": self.answers[0]["id"], "prediction": self.answers[0]["answer"]}]
        with self.assertRaisesRegex(ValueError, "missing 719"):
            score(self.questions, self.answers, one)
        result = score(self.questions, self.answers, one, allow_partial=True)
        self.assertFalse(result["complete"])
        self.assertEqual(result["submitted"], 1)
        self.assertIsNone(result["macro_accuracy"])
        self.assertIsNone(result["worst_country_accuracy"])

    def test_invalid_and_inference_errors_stay_in_denominator(self):
        preds = [{"id": a["id"], "prediction": a["answer"]} for a in self.answers]
        preds[0]["prediction"] = "A or B"
        preds[1]["status"] = "error"
        result = score(self.questions, self.answers, preds)
        self.assertEqual((result["correct"], result["invalid"], result["inference_errors"]), (718, 2, 1))
        self.assertAlmostEqual(result["accuracy"], 100 * 718 / 720)

    def test_duplicate_unknown_and_nonstring_predictions_fail(self):
        a = self.answers[0]
        row = {"id": a["id"], "prediction": a["answer"]}
        with self.assertRaisesRegex(ValueError, "duplicate"):
            score(self.questions, self.answers, [row, row], allow_partial=True)
        with self.assertRaisesRegex(ValueError, "unknown"):
            score(self.questions, self.answers, [{"id": "wrong-id", "prediction": "A"}], allow_partial=True)
        with self.assertRaisesRegex(ValueError, "must be a string"):
            score(self.questions, self.answers, [{"id": a["id"], "prediction": None}], allow_partial=True)

    def test_changed_release_bytes_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            for folder in ("data", "provenance"):
                shutil.copytree(ROOT / folder, Path(tmp) / folder)
            path = Path(tmp) / "data/v1.4.1-release/answers.jsonl"
            path.write_bytes(path.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                validate_release(tmp)

    def test_duplicate_json_keys_are_not_silently_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "predictions.jsonl"
            path.write_text('{"id":"a","prediction":"A","prediction":"B"}\n')
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                read_jsonl(path)


class ParserTest(unittest.TestCase):
    def test_multilingual_explicit_answers(self):
        samples = [
            ("A", "**Correct answer: A.**"), ("B", "The correct answer is B."),
            ("C", "La bonne réponse est C."), ("D", "A alternativa correta é D."),
            ("B", "La respuesta correcta es la B."), ("A", "Jawaban yang paling tepat adalah A."),
            ("C", "सही निष्कर्ष C है।"), ("A", "正确选项：**A**。"),
            ("C", "正解は C です。"), ("B", "정답은 B입니다."),
            ("D", "B</think>Final answer: D."), ("A", "```text\nA\n```"),
        ]
        for expected, text in samples:
            with self.subTest(text=text):
                self.assertEqual(extract_final_choice(text), (expected, None))

    def test_multiple_answers_and_reasoning_are_rejected(self):
        for text in ["", "<think>A</think>", "A or B", "Answer: A/B", "Answer: A\nFinal answer: B.",
                     "A court may decide this.", "A alternativa depende da lei.",
                     "La proposition A serait vraie si les conditions étaient réunies.",
                     "Option A is wrong. Option B is possible.", "> Answer: A\nA quote is being discussed."]:
            with self.subTest(text=text):
                self.assertIsNone(extract_final_choice(text)[0])

    def test_portuguese_article_is_not_option_a(self):
        self.assertEqual(extract_final_choice("A alternativa correta é a **B**."), ("B", None))


if __name__ == "__main__":
    unittest.main()
