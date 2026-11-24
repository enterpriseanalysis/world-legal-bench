"""Build an auditable v2.0 subset from pinned v1.4.2 items and saved grades.

No model calls. Private platform snapshots are inputs, never public artifacts.
"""
import argparse,collections,hashlib,html,json
from pathlib import Path

REGIONS={'Americas':['US','CA','BR','MX'],'Asia':['KR','CN','JP','IN','ID'],'Europe':['FR'],'Africa':['ZA'],'Oceania':['AU']}
REGION={c:r for r,cs in REGIONS.items() for c in cs}
QUOTAS=dict(US=2,CA=4,AU=3,KR=6,FR=4,BR=0,MX=1,CN=1,JP=5,IN=1,ZA=4,ID=2)
EXPECTED=dict(US=21,CA=38,AU=33,KR=56,FR=41,BR=4,MX=14,CN=10,JP=53,IN=8,ZA=34,ID=15)

def sha(raw):return hashlib.sha256(raw).hexdigest()
def dump(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def lines(path,values):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(''.join(json.dumps(v,ensure_ascii=False,separators=(',',':'))+'\n' for v in values))
def decode(value):return json.loads(html.unescape(value))

def build(args):
 parent_raw=(args.parent/'candidates.jsonl').read_bytes();parent_manifest=json.loads((args.parent/'manifest.json').read_text())
 assert sha(parent_raw)==parent_manifest['sha256']
 by_country=collections.defaultdict(list)
 for line in parent_raw.splitlines():
  row=json.loads(line);by_country[row['country']].append(row)
 snapshots={c:json.loads((args.outcomes/(c.lower()+'.json')).read_text()) for c in QUOTAS}
 selected=[];records=[]
 def bound(country,detail,outcome):
  identity=decode(detail['gold']);index=detail['sampleIndex'];row=by_country[country][index];reference=identity['reference']
  assert identity['sample_index']==index and reference['id']==row['id']
  assert reference['answer']==row['private_gold']['correct_option']
  assert detail['caseStatus']==4 and bool(detail['isCorrect'])==(outcome=='correct')
  native=decode(detail['result'])['world_legal_bench']
  assert native['judge_version']=='world-legal-llm-judge-v1.4.2'
  assert native['outcome'] in (('correct',) if outcome=='correct' else ('incorrect','invalid_output'))
  assert html.unescape(detail.get('answer') or detail.get('prediction') or '').strip()
  return row,native,index
 def features(row):
  meta=row['metadata'];return {('family',str(meta.get('knowledge_family',''))),('task',str(meta.get('task_family','')))}|{('source',str(s.get('source_id') or s.get('url'))) for s in row['source_refs']}
 for country in QUOTAS:
  snapshot=snapshots[country];failures=[bound(country,r,'failed') for r in snapshot['failures']]
  assert len(failures)==EXPECTED[country]
  chosen=list(failures);seen=set().union(*(features(row) for row,_,_ in chosen))
  candidates=[bound(country,r,'correct') for r in snapshot['success_candidates']]
  for _ in range(QUOTAS[country]):
   def priority(item):
    row=item[0];new=features(row)-seen
    return (-sum(4 if k=='family' else 2 if k=='task' else 1 for k,_ in new),sha(row['id'].encode()))
   candidate=min(candidates,key=priority);candidates.remove(candidate);chosen.append(candidate);seen|=features(candidate[0])
  for row,native,index in sorted(chosen,key=lambda item:item[2]):
   selected.append(row)
   records.append({'id':row['id'],'country':country,'region':REGION[country],
       'source_sample_index':index,'answer':row['private_gold']['correct_option'],
       'reference_choice':native.get('choice'),'reference_outcome':native['outcome'],
       'reference_model':'gpt-6-luna','reasoning_effort':'max','judge_version':native['judge_version'],
       'selection_reason':'retain_all_scored_nonpasses' if native['outcome']!='correct' else 'legal_topic_coverage_fill'})
 assert len(selected)==360 and len({r['id'] for r in selected})==360
 profile=collections.Counter(r['reference_outcome'] for r in records)
 assert profile=={'correct':33,'incorrect':301,'invalid_output':26},profile
 service_raw=''.join(json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n' for row in selected).encode()
 release_id='world-legal-bench-v2-0-'+sha(service_raw)[:12]
 service={**parent_manifest,'version':'2.0','parent_version':'1.4.2','release_id':release_id,
  'protocol':'world-legal-bench-mcq-v2.0','suite_id':'world-legal-bench-v2-0','sha256':sha(service_raw),
  'case_count':360,'new_case_count':0,'retained_case_count':360,'judge_version':'world-legal-llm-judge-v2.0',
  'evaluation_mode':'llm_judge','regions':[{'name':r,'countries':cs,'count':sum(1 for x in records if x['region']==r)} for r,cs in REGIONS.items()],
  'description':'World Legal Bench 2.0: 360 difficulty-selected questions across 12 jurisdictions and five UN M49-referenced reporting regions. Full LLM judging. Report item-micro and region-macro accuracy; reference selection is not an independent model evaluation.',
  'review_status':'inherited_author_checks_no_new_expert_audit','reference_selection':dict(profile),
  'parent_bundle_sha256':sha(parent_raw),'reference_model':'gpt-6-luna','selection_date':'2026-11-24'}
 for obsolete in ('difficulty','screening_status','selection_model'):service.pop(obsolete,None)
 for c in service['countries']:
  c['count']=sum(r['country']==c['code'] for r in selected);c['dataset_id']='world-legal-bench-v2-0-'+c['code'].lower();c['region']=REGION[c['code']]
 for destination in (args.bm/'app/resources/world_legal_bench_v20',args.java/'fsafetyai-service/src/main/resources/world-legal-bench-v20'):
  destination.mkdir(parents=True,exist_ok=True);(destination/'candidates.jsonl').write_bytes(service_raw);dump(destination/'manifest.json',service)
 root=args.public;folder=root/'data/v2.0';provenance=root/'provenance/v2.0'
 questions=[];answers=[];sources={}
 for row in selected:
  source_ids=[]
  for ref in row['source_refs']:
   source={'country':row['country'],'url':ref['url'],'locator':ref.get('locator',ref.get('article','')),'version':ref.get('source_version','pinned parent source'),'digests':{k:v for k,v in ref.items() if 'sha256' in k}}
   sid='SRC-'+sha(json.dumps(source,sort_keys=True,ensure_ascii=False).encode())[:20];source['id']=sid;sources[sid]=source;source_ids.append(sid)
  questions.append({'id':row['id'],'revision':row['revision'],'country':row['country'],'region':REGION[row['country']],
       'language':row['language'],'question':row['prompt'],'choices':row['options'],'task_family':row['metadata'].get('task_family','legal_reasoning'),'source_ids':source_ids})
  gold=row['private_gold'];answer={'id':row['id'],'answer':gold['correct_option'],'answer_text':gold['correct_answer_text']}
  if 'option_reviews' in gold:answer['option_rationales']=gold['option_reviews']
  else:answer['statement_reviews']=gold['statement_reviews']
  answers.append(answer)
 lines(folder/'questions.jsonl',questions);lines(folder/'answers.jsonl',answers);lines(folder/'sources.jsonl',sorted(sources.values(),key=lambda r:r['id']))
 lines(provenance/'selection.jsonl',records)
 regional=[]
 for region,cs in REGIONS.items():
  rows=[r for r in records if r['region']==region];correct=sum(r['reference_outcome']=='correct' for r in rows)
  regional.append({'region':region,'total':len(rows),'correct':correct,'nonpassing':len(rows)-correct,'accuracy':100*correct/len(rows)})
 report={'version':'2.0','model':'gpt-6-luna','reasoning_effort':'max','status':'retrospective_selection_profile_not_independent_evaluation',
   'total':360,'correct':33,'incorrect':301,'invalid_output':26,'nonpassing':327,'accuracy':100*33/360,
   'region_macro_accuracy':sum(r['accuracy'] for r in regional)/5,'by_region':regional,
   'by_country':{c:{'correct':QUOTAS[c],'nonpassing':EXPECTED[c],'total':QUOTAS[c]+EXPECTED[c]} for c in QUOTAS}}
 dump(provenance/'reference_selection.json',report)
 dump(provenance/'release.json',{'version':'2.0','release_id':release_id,'parent_version':'1.4.2','parent_sha256':sha(parent_raw),'date':'2026-11-24',
  'selection_policy':'Retain all 327 scored nonpasses, including 26 invalid final answers; add 33 coverage fills from recorded successes. Exclude execution failures, unscored and empty responses.',
  'review_scope':'Identity, source binding, score status, counts and duplicate checks only; no new legal expert audit.',
  'geography_source':'https://unstats.un.org/unsd/methodology/m49/'})
 jurisdictions=json.loads((root/'data/jurisdictions.json').read_text())
 for row in jurisdictions:row.update(cases=QUOTAS[row['code']]+EXPECTED[row['code']],region=REGION[row['code']])
 dump(folder/'jurisdictions.json',jurisdictions)
 files=[str(p.relative_to(root)) for p in [folder/'questions.jsonl',folder/'answers.jsonl',folder/'sources.jsonl',folder/'jurisdictions.json',provenance/'selection.jsonl',provenance/'reference_selection.json',provenance/'release.json']]
 manifest={'name':'World Legal Bench','version':'2.0','mode':'closed_book','case_count':360,'jurisdictions':12,'languages':9,'regions':5,
   'country_counts':{c:QUOTAS[c]+EXPECTED[c] for c in QUOTAS},'answer_labels':list('ABCD'),'scoring_protocol':'world-legal-bench-mcq-v2.0',
   'judge_version':'world-legal-llm-judge-v2.0','jurisdictions_file':'data/v2.0/jurisdictions.json','provenance_dir':'provenance/v2.0',
   'files':{p:sha((root/p).read_bytes()) for p in files}}
 dump(folder/'manifest.json',manifest)
 dump(args.receipt,{'service_release':release_id,'profile':report,'parent_sha256':sha(parent_raw)})
 print(json.dumps(report,indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('parent','outcomes','bm','java','public','receipt'):p.add_argument('--'+name,type=Path,required=True)
 build(p.parse_args())
