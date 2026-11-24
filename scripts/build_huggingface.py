"""Build a local, self-contained Hugging Face dataset-repository folder."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'huggingface'
RELEASE = ROOT / 'data/v2.0'


def read(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def main():
    questions = read(RELEASE / 'questions.jsonl')
    answers = {r['id']: r for r in read(RELEASE / 'answers.jsonl')}
    sources = {r['id']: r for r in read(RELEASE / 'sources.jsonl')}
    rows = []
    for q in questions:
        a = answers[q['id']]
        assert a['answer_text'] == q['choices'][a['answer']]
        rows.append({
            'country': q['country'], 'region': q['region'], 'language': q['language'], 'question_id': q['id'],
            'question': q['question'], 'choices': [f'{c}. {q["choices"][c]}' for c in 'ABCD'],
            'answer': a['answer'], 'answer_text': a['answer_text'],
            'task_family': q['task_family'],
            'source_urls': list(dict.fromkeys(sources[s]['url'] for s in q['source_ids'])),
        })
    OUT.mkdir(exist_ok=True)
    (OUT / 'data').mkdir(exist_ok=True)
    (OUT / 'annotations').mkdir(exist_ok=True)
    (OUT / 'evaluation').mkdir(exist_ok=True)
    (OUT / 'assets').mkdir(exist_ok=True)
    (OUT / 'provenance').mkdir(exist_ok=True)
    (OUT / 'data/test.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) + '\n' for r in rows), encoding='utf-8')
    copies = {
        'data/v2.0/sources.jsonl': 'annotations/sources.jsonl',
        'data/v2.0/answers.jsonl': 'annotations/answers.jsonl',
        'data/v2.0/jurisdictions.json': 'annotations/jurisdictions.json',
        'provenance/v2.0/selection.jsonl': 'provenance/v2.0/selection.jsonl',
        'provenance/v2.0/reference_selection.json': 'provenance/v2.0/reference_selection.json',
        'provenance/v2.0/release.json': 'provenance/v2.0/release.json',
        'LICENSE': 'LICENSE', 'LICENSE-DATA': 'LICENSE-DATA', 'NOTICE': 'NOTICE',
        'CITATION.cff': 'CITATION.cff',
        'assets/regional-coverage-v20.svg': 'assets/regional-coverage-v20.svg',
        'assets/banner.svg': 'assets/banner.svg',
        'assets/hero-research-v2.png': 'assets/hero-research-v2.png',
        'assets/coverage-matrix-v2.png': 'assets/coverage-matrix-v2.png',
        'assets/coverage-matrix-v2.svg': 'assets/coverage-matrix-v2.svg',
        'assets/evaluation-flow-v2.png': 'assets/evaluation-flow-v2.png',
        'assets/evaluation-flow-v2.svg': 'assets/evaluation-flow-v2.svg',
        'assets/selection-profile-v2.png': 'assets/selection-profile-v2.png',
        'assets/selection-profile-v2.svg': 'assets/selection-profile-v2.svg',
        'src/world_legal_bench/parser.py': 'evaluation/parser.py',
        'src/world_legal_bench/output.py': 'evaluation/output.py',
    }
    for src, dest in copies.items():
        (OUT / dest).parent.mkdir(exist_ok=True, parents=True)
        shutil.copyfile(ROOT / src, OUT / dest)
    (OUT / 'evaluation/__init__.py').write_text('"""Standalone evaluation helpers for the dataset repository."""\n', encoding='utf-8')
    metrics = (ROOT / 'src/world_legal_bench/metrics.py').read_text().replace('from .dataset import unique_by_id', 'from .records import unique_by_id')
    (OUT / 'evaluation/metrics.py').write_text(metrics, encoding='utf-8')
    module = (ROOT / 'src/world_legal_bench/dataset.py').read_text(encoding='utf-8')
    tree = ast.parse(module)
    helpers = [ast.get_source_segment(module, node) for node in tree.body
               if isinstance(node, ast.FunctionDef) and node.name in ('_unique_object', 'read_jsonl', 'unique_by_id')]
    (OUT / 'evaluation/records.py').write_text(
        '\"\"\"Record helpers generated from the canonical evaluator.\"\"\"\n\nimport json\nfrom pathlib import Path\n\n' + '\n\n'.join(helpers) + '\n', encoding='utf-8')
    contributing = (ROOT / 'CONTRIBUTING.md').read_text(encoding='utf-8').replace('python scripts/check_release.py\npython -m unittest discover -s tests -v', 'python evaluate.py --help')
    (OUT / 'CONTRIBUTING.md').write_text(contributing, encoding='utf-8')
    shutil.copyfile(ROOT / 'src/world_legal_bench/geography.py', OUT / 'evaluation/geography.py')
    judge_source = (ROOT / 'src/world_legal_bench/judge.py').read_text()
    judge_ast = ast.parse(judge_source)
    validator = next(ast.get_source_segment(judge_source, node) for node in judge_ast.body
                     if isinstance(node, ast.FunctionDef) and node.name == 'validate_grade')
    (OUT / 'evaluation/judge.py').write_text('import json\nfrom .output import final_answer_text\n\n' + validator + '\n')
    for name in ('methodology.md','evaluation.md','results.md'):
        (OUT / 'docs').mkdir(exist_ok=True)
        shutil.copyfile(ROOT / 'docs' / name, OUT / 'docs' / name)
    critical = ['data/test.jsonl', 'annotations/sources.jsonl', 'annotations/answers.jsonl',
                'annotations/jurisdictions.json', 'provenance/v2.0/selection.jsonl',
                'provenance/v2.0/reference_selection.json', 'provenance/v2.0/release.json', 'evaluation/parser.py', 'evaluation/output.py', 'evaluation/geography.py', 'evaluation/judge.py',
                'evaluation/metrics.py', 'evaluation/records.py', 'evaluation/__init__.py', 'evaluate.py']
    manifest = {'dataset': 'World Legal Bench', 'version': '2.0', 'config': 'default',
                'split': 'test', 'num_examples': len(rows), 'jurisdictions': 12, 'languages': 9,
                'judge_version': 'world-legal-llm-judge-v2.0',
                'files': {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in critical}}
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'folder': 'huggingface', 'split': 'test', 'rows': len(rows), 'columns': list(rows[0])}))


if __name__ == '__main__':
    main()
