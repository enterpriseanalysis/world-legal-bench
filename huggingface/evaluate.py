"""Score saved predictions against this local HF-format release, without model calls."""

import argparse
import hashlib
import json
from pathlib import Path
import sys

from evaluation.records import read_jsonl
from evaluation.metrics import score

ROOT = Path(__file__).resolve().parent


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--predictions', required=True, type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--allow-partial', action='store_true')
    args = parser.parse_args(argv)
    try:
        manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
        for name, digest in manifest['files'].items():
            path = (ROOT / name).resolve()
            if not path.is_relative_to(ROOT) or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                raise ValueError(f'release file digest mismatch: {name}')
        rows = read_jsonl(ROOT / 'data/test.jsonl')
        questions = [{'id': r['question_id'], 'country': r['country']} for r in rows]
        answers = [{'id': r['question_id'], 'answer': r['answer']} for r in rows]
        report = score(questions, answers, read_jsonl(args.predictions), allow_partial=args.allow_partial)
        report['dataset_version'] = manifest['version']
        if args.output:
            args.output.parent.mkdir(exist_ok=True, parents=True)
            args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({k: v for k, v in report.items() if k != 'cases'}, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError) as exc:
        print(f'world-legal-bench: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
