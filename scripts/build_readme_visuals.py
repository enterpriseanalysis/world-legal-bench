"""Render publication-style coverage and protocol figures from the release files."""

import collections
import json
from pathlib import Path
import shutil

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch
from matplotlib.colors import to_rgb

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets'
HF = ROOT / 'huggingface/assets'
rows = [json.loads(l) for l in (ROOT / 'data/v1.4.1-release/questions.jsonl').open(encoding='utf-8')]
counts = collections.Counter(r['country'] for r in rows)
jur = {r['code']: r for r in json.loads((ROOT / 'data/jurisdictions.json').read_text())}
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 12,
                     'svg.fonttype': 'none', 'svg.hashsalt': 'world-legal-bench-readme-v2'})


def save(fig, name):
    fig.savefig(OUT / (name+'.png'), dpi=170, facecolor='white')
    path = OUT / (name+'.svg')
    fig.savefig(path, facecolor='white', metadata={'Date': None})
    path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
    for suffix in ['.png', '.svg']:
        shutil.copyfile(OUT / (name+suffix), HF / (name+suffix))
    plt.close(fig)


# Language blocks span one equal-area cell per jurisdiction.
fig, ax = plt.subplots(figsize=(12, 6.8), facecolor='white')
ax.set_xlim(0, 12);ax.set_ylim(0, 5.5);ax.axis('off')
fig.text(.025, .95, 'World Legal Bench: question coverage', fontsize=20, weight='bold', color='#163247')
fig.text(.025, .895, 'Each jurisdiction contributes 60 questions. Blocks are grouped by test language.', fontsize=11.5, color='#5c6c7d')
groups = [
    (0, 2.75, 'English', ['US','AU','ZA'], '#187e70'),
    (6, 2.75, 'French', ['CA','FR'], '#168394'),
    (10, 2.75, 'Korean', ['KR'], '#8760a5'),
    (0, .1, 'Portuguese', ['BR'], '#368bb5'),
    (2, .1, 'Spanish', ['MX'], '#c56c47'),
    (4, .1, 'Chinese', ['CN'], '#8270b5'),
    (6, .1, 'Japanese', ['JP'], '#4a81a5'),
    (8, .1, 'Hindi', ['IN'], '#a75e86'),
    (10, .1, 'Indonesian', ['ID'], '#738b42'),
]
for x,y,label,codes,color in groups:
    width=2*len(codes)-.08; height=2.45
    ax.add_patch(Rectangle((x+.04,y),width,height,facecolor=color,edgecolor='white',lw=2))
    ax.text(x+.04+width/2,y+height-.22,label,ha='center',va='center',fontsize=12.5,color='white',weight='bold')
    tint=tuple(.13*c+.87 for c in to_rgb(color))
    for n,country in enumerate(codes):
        cx=x+n*2+.09
        ax.add_patch(Rectangle((cx,y+.055),1.82,1.97,facecolor=tint,edgecolor='white',lw=1.4))
        name=jur[country]['name']
        if name in ['United States','South Africa','South Korea']:
            name=name.replace(' ','\n',1)
        ax.text(cx+.91,y+1.30,name,ha='center',va='center',fontsize=13,color='#1e3c4e',linespacing=1.3)
        ax.text(cx+.91,y+.55,str(counts[country]),ha='center',va='center',fontsize=21,weight='bold',color=color)
fig.text(.025,.035,'720 questions  ·  12 jurisdictions  ·  9 test languages  |  v1.4.1-release',fontsize=10,color='#6d7b86')
fig.subplots_adjust(left=.02,right=.98,top=.82,bottom=.10)
save(fig,'coverage-matrix-v2')

# The pipeline describes the actual single-turn closed-book scoring contract.
fig, ax = plt.subplots(figsize=(12, 4.7), facecolor='white')
ax.set_xlim(0,12);ax.set_ylim(0,4);ax.axis('off')
fig.text(.025,.94,'One question. One final choice. Deterministic scoring.',fontsize=19,weight='bold',color='#163247')
fig.text(.025,.865,'Closed-book evaluation; source annotations and gold answers remain outside model input.',fontsize=11.2,color='#5c6c7d')
items=[(.15,'01  QUESTION','Legal scenario\n+ four choices','Authored test language','#187e70'),
       (3.25,'02  MODEL','One independent\nsingle-turn request','No retrieval or agent tools','#168394'),
       (6.35,'03  PARSER','Unique final\nA, B, C or D','Multilingual answer extraction','#8270b5'),
       (9.45,'04  SCORE','Compare choice\nwith reference key','Country accuracy + macro score','#bc7444')]
for x,head,body,note,color in items:
    ax.add_patch(FancyBboxPatch((x,1.05),2.38,1.8,boxstyle='round,pad=0.02,rounding_size=.09',facecolor='#f7f9fb',edgecolor='#dbe3e9',lw=1.1))
    ax.text(x+.17,2.57,head,fontsize=11,weight='bold',color=color)
    ax.text(x+.17,1.99,body,fontsize=13.5,color='#203d50',va='center',linespacing=1.35)
    ax.text(x+.17,1.27,note,fontsize=8.7,color='#657687')
    if x<9:
        ax.add_patch(FancyArrowPatch((x+2.43,1.95),(x+2.99,1.95),arrowstyle='-|>',mutation_scale=15,color='#a3b3c0',lw=1.3))
ax.text(.18,.56,'Gold answers are used by the scorer only.',fontsize=10,color='#657687')
ax.text(.18,.15,'Invalid and failed-inference responses remain unsuccessful; conflicting final choices are not guessed.',fontsize=10,color='#657687')
fig.subplots_adjust(left=.015,right=.985,top=.78,bottom=.035)
save(fig,'evaluation-flow-v2')

# A valid descriptive figure: no invented model leaderboard.
profile=json.loads((ROOT/'provenance/reference_selection.json').read_text())
fig, ax=plt.subplots(figsize=(12,4.7),facecolor='white')
ax.set_xlim(0,720);ax.set_ylim(0,1);ax.axis('off')
fig.text(.025,.94,'Reference selection profile',fontsize=20,weight='bold',color='#163247')
fig.text(.025,.865,'Historical answers used to choose the items; this is not a new benchmark run.',fontsize=11.2,color='#5c6c7d')
wrong,correct=profile['incorrect'],profile['correct']
ax.barh(.58,wrong,height=.23,color='#278695',left=0)
ax.barh(.58,correct,height=.23,color='#d9a34f',left=wrong)
ax.text(wrong/2,.58,f'{wrong} reference errors',ha='center',va='center',color='white',fontsize=15,weight='bold')
ax.text(wrong+correct/2,.58,f'{correct} correct',ha='center',va='center',color='#233b49',fontsize=13,weight='bold')
ax.text(0,.29,'Selection favors reference-model errors. Jurisdictions with fewer eligible errors use correct-item fill.',fontsize=10,color='#657687')
ax.text(0,.10,'17.78% retrospective accuracy is conditional on selection and is not an unbiased capability estimate.',fontsize=10,color='#657687')
fig.subplots_adjust(left=.027,right=.975,top=.77,bottom=.05)
save(fig,'selection-profile-v2')
print('Rendered coverage-matrix-v2, evaluation-flow-v2, selection-profile-v2')
