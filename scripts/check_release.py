"""Validate the release directly from a source checkout."""

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from world_legal_bench.dataset import validate_release

print(json.dumps(validate_release(ROOT), ensure_ascii=False, indent=2))
