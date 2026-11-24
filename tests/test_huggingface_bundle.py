"""The HF-format export must preserve content and score like the canonical release."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "huggingface"
from grade_helpers import prediction as fixture_prediction


def records(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class HuggingFaceBundleTest(unittest.TestCase):
    def test_join_preserves_every_question_choice_and_gold(self):
        questions = {r["id"]: r for r in records(ROOT / "data/v2.0/questions.jsonl")}
        answers = {r["id"]: r for r in records(ROOT / "data/v2.0/answers.jsonl")}
        rows = records(BUNDLE / "data/test.jsonl")
        self.assertEqual(len(rows), 360)
        self.assertEqual({r["question_id"] for r in rows}, set(questions))
        for row in rows:
            q, a = questions[row["question_id"]], answers[row["question_id"]]
            self.assertEqual(row["question"], q["question"])
            self.assertEqual(row["country"], q["country"])
            self.assertEqual(row["choices"], [f"{label}. {q['choices'][label]}" for label in "ABCD"])
            self.assertEqual((row["answer"], row["answer_text"]), (a["answer"], a["answer_text"]))

    def test_manifest_covers_unchanged_data_and_standalone_scorer(self):
        manifest = json.loads((BUNDLE / "manifest.json").read_text())
        self.assertEqual(manifest["num_examples"], 360)
        self.assertIn("evaluate.py", manifest["files"])
        for name, digest in manifest["files"].items():
            self.assertEqual(hashlib.sha256((BUNDLE / name).read_bytes()).hexdigest(), digest, name)
        self.assertEqual((BUNDLE / "evaluation/parser.py").read_bytes(),
                         (ROOT / "src/world_legal_bench/parser.py").read_bytes())

    def test_standalone_scorer_reproduces_reference_profile(self):
        selected = records(ROOT / "provenance/v2.0/selection.jsonl")
        with tempfile.TemporaryDirectory() as tmp:
            predictions = Path(tmp) / "predictions.jsonl"
            predictions.write_text("".join(json.dumps(fixture_prediction(r["id"], r["reference_choice"], r["reference_outcome"]))
                                             + "\n" for r in selected))
            result = subprocess.run([sys.executable, str(BUNDLE / "evaluate.py"),
                                     "--predictions", str(predictions)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual((report["correct"], report["incorrect"], report["invalid"]), (33, 301, 26))
            self.assertTrue(report["complete"])
            self.assertAlmostEqual(report["region_macro_accuracy"], 9.127202294483556)

    def test_standalone_partial_report_does_not_claim_full_score(self):
        result = subprocess.run([sys.executable, str(BUNDLE / "evaluate.py"), "--predictions",
                                 str(ROOT / "examples/predictions.example.jsonl"), "--allow-partial"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual((report["submitted"], report["missing"]), (3, 357))
        self.assertFalse(report["complete"])
        self.assertIsNone(report["macro_accuracy"])


if __name__ == "__main__":
    unittest.main()
