"""Render the language-count figure directly from the frozen question file."""

import collections
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
rows = [json.loads(line) for line in (ROOT / 'data/v1.4.1-release/questions.jsonl').open(encoding='utf-8')]
counts = collections.Counter(row['language'] for row in rows)
names = {'en': 'English', 'fr': 'French', 'ko': 'Korean', 'pt': 'Portuguese', 'es': 'Spanish',
         'zh-Hans': 'Simplified Chinese', 'ja': 'Japanese', 'hi': 'Hindi', 'id': 'Indonesian'}
order = ['en', 'fr', 'ko', 'pt', 'es', 'zh-Hans', 'ja', 'hi', 'id']
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 12, 'svg.fonttype': 'none', 'svg.hashsalt': 'world-legal-bench-v1.4.1-release'})
fig, ax = plt.subplots(figsize=(10, 5.5), facecolor='white')
values = [counts[lang] for lang in order]
ax.barh(range(len(order)), values, color='#267f89', height=.58)
ax.set_yticks(range(len(order)), [names[lang] for lang in order])
ax.invert_yaxis()
ax.set_xlim(0, 210)
ax.set_xticks([0, 60, 120, 180])
ax.set_xlabel('Questions', color='#445264')
ax.grid(axis='x', color='#e4eaf0', linewidth=.8)
ax.set_axisbelow(True)
ax.tick_params(axis='both', length=0, labelcolor='#34465a')
for spine in ax.spines.values():
    spine.set_visible(False)
for y, value in enumerate(values):
    ax.text(value + 4, y, str(value), va='center', color='#17394b', fontsize=12, weight='bold')
fig.text(.035, .95, 'Test-language coverage', fontsize=19, weight='bold', color='#132e42')
fig.text(.035, .89, 'Jurisdiction quotas are equal; language totals differ.', fontsize=12, color='#506477')
fig.text(.035, .025, 'World Legal Bench v1.4.1-release · counts derived from the 720 released questions', fontsize=9, color='#697a87')
fig.subplots_adjust(left=.25, right=.95, top=.82, bottom=.15)
output = ROOT / 'huggingface/assets'
output.mkdir(exist_ok=True, parents=True)
fig.savefig(output / 'language_coverage.png', dpi=160, facecolor='white')
fig.savefig(output / 'language_coverage.svg', facecolor='white', metadata={'Date': None})
svg = output / 'language_coverage.svg'
svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines()) + '\n')
plt.close(fig)
print(dict(counts))
