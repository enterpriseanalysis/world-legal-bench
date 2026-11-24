"""No-network checks for required LLM grades and separate Judge errors."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from world_legal_bench.judge import judge_predictions, validate_grade
from world_legal_bench.dataset import load_questions,load_answers,read_jsonl
from world_legal_bench.metrics import score

class JudgeTest(unittest.TestCase):
    def test_v20_refuses_unjudged_answers(self):
        q=load_questions(ROOT)[0];a=load_answers(ROOT)[0]
        with self.assertRaisesRegex(ValueError,'requires LLM'):
            score([q],[a],[{'id':q['id'],'prediction':a['answer']}])

    def test_transport_saves_validated_grade_and_separate_errors(self):
        questions=load_questions(ROOT)[:2];answers=load_answers(ROOT)[:2]
        preds=[{'id':a['id'],'prediction':a['answer']} for a in answers]
        grade={'outcome':'correct','choice':answers[0]['answer'],'evidence':answers[0]['answer'],'reason':'Mock response for transport validation.'}
        responses=[{'status':'ok','prediction':json.dumps(grade)},{'status':'ok','prediction':'not JSON'}]
        with tempfile.TemporaryDirectory() as tmp,patch('world_legal_bench.judge.request_case',side_effect=responses):
            target=Path(tmp)/'judged.jsonl'
            result=judge_predictions(questions,answers,preds,output=target,base_url='https://example.invalid/v1',model='mock-only',workers=1,retries=0)
            self.assertEqual(result['judge_errors'],1)
            scored=score(questions,answers,read_jsonl(target))
            self.assertEqual((scored['correct'],scored['judge_errors'],scored['inference_errors']),(1,1,0))
            self.assertIsNone(scored['region_macro_accuracy'])

    def test_fabricated_evidence_and_inconsistent_labels_are_rejected(self):
        for grade in [dict(outcome='correct',choice='B',evidence='B',reason='test'),dict(outcome='correct',choice='A',evidence='fabricated',reason='test')]:
            with self.assertRaises(ValueError):validate_grade(grade,'A','A')
