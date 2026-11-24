"""Command-line validation, prompt export, inference, and scoring."""

import argparse
import json
import os
from pathlib import Path
import sys

from . import DATASET_VERSION
from .dataset import load_questions, load_answers, read_jsonl, messages_for, validate_release, write_jsonl
from .metrics import score


def main(argv=None):
    parser = argparse.ArgumentParser(prog="wlb", description="World Legal Bench evaluation toolkit")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository checkout (default: current directory)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate", help="verify hashes, data alignment, review coverage, and quotas")
    export = sub.add_parser("export-prompts", help="export model messages without gold or source materials")
    export.add_argument("--output", required=True, type=Path)
    export.add_argument("--country", help="optional country code, e.g. US")
    scoring = sub.add_parser("score", help="score saved final responses")
    scoring.add_argument("--predictions", required=True, type=Path)
    scoring.add_argument("--output", type=Path)
    scoring.add_argument("--allow-partial", action="store_true", help="debug only; macro score is withheld")
    judging = sub.add_parser("judge", help="grade saved predictions with an explicitly configured LLM")
    judging.add_argument("--predictions", required=True, type=Path)
    judging.add_argument("--output", required=True, type=Path)
    judging.add_argument("--base-url", required=True)
    judging.add_argument("--model", required=True)
    judging.add_argument("--workers", type=int, default=4)
    judging.add_argument("--qpm", type=float, default=60)
    judging.add_argument("--max-tokens", type=int, default=131072)
    running = sub.add_parser("run", help="send requests to an explicitly configured endpoint")
    running.add_argument("--base-url", default=os.environ.get("OPENAI_BASE_URL"))
    running.add_argument("--model", required=True)
    running.add_argument("--output", required=True, type=Path)
    running.add_argument("--workers", type=int, default=4)
    running.add_argument("--qpm", type=float, default=60)
    running.add_argument("--max-tokens", type=int, default=131072)
    running.add_argument("--temperature", type=float, default=0)
    running.add_argument("--timeout", type=float, default=600)
    running.add_argument("--retries", type=int, default=2)
    running.add_argument("--extra-body", type=json.loads, default={})
    running.add_argument("--resume", action="store_true")
    running.add_argument("--limit", type=int, help="debug subset; not a complete benchmark run")
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            result = validate_release(args.root)
        elif args.command == "export-prompts":
            questions = load_questions(args.root)
            if args.country:
                questions = [q for q in questions if q["country"] == args.country.upper()]
                if not questions:
                    raise ValueError("unknown country")
            write_jsonl(args.output, ({"id": q["id"], "country": q["country"], "language": q["language"],
                                      "messages": messages_for(q)} for q in questions))
            result = {"exported": len(questions), "output": str(args.output)}
        elif args.command == "score":
            validate_release(args.root)
            result = score(load_questions(args.root), load_answers(args.root),
                           read_jsonl(args.predictions), allow_partial=args.allow_partial)
            result["dataset_version"] = DATASET_VERSION
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            result = {k: value for k, value in result.items() if k != "cases"}
        elif args.command == "judge":
            validate_release(args.root)
            from .judge import judge_predictions
            result = judge_predictions(load_questions(args.root), load_answers(args.root),
                read_jsonl(args.predictions), output=args.output, base_url=args.base_url,
                model=args.model, workers=args.workers, qpm=args.qpm, max_tokens=args.max_tokens)
        else:
            if not args.base_url:
                raise ValueError("set --base-url or OPENAI_BASE_URL")
            questions = load_questions(args.root)
            if args.limit is not None:
                if args.limit <= 0:
                    raise ValueError("limit must be positive")
                questions = questions[:args.limit]
            from .runner import run
            result = run(questions, output=args.output, base_url=args.base_url, model=args.model,
                         workers=args.workers, qpm=args.qpm, max_tokens=args.max_tokens,
                         temperature=args.temperature, timeout=args.timeout, retries=args.retries,
                         resume=args.resume, extra_body=args.extra_body)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError) as exc:
        print(f"wlb: {exc}", file=sys.stderr)
        return 2
