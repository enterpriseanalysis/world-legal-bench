import json
from .output import final_answer_text

def validate_grade(grade, prediction, reference):
    if isinstance(grade, str):
        text = final_answer_text(grade).strip()
        if text.startswith('```json') and text.endswith('```'):
            text = text[7:-3].strip()
        grade = json.loads(text)
    if not isinstance(grade, dict) or set(grade) != {'outcome','choice','evidence','reason'}:
        raise ValueError('invalid Judge JSON fields')
    outcome, choice = grade['outcome'], grade['choice']
    if outcome not in ('correct','incorrect','invalid_output') or choice not in ('A','B','C','D',None):
        raise ValueError('invalid Judge outcome or choice')
    final = final_answer_text(prediction).strip()
    evidence = grade['evidence']
    if not isinstance(evidence,str) or evidence not in final or (final and not evidence.strip()):
        raise ValueError('Judge evidence must be a candidate excerpt')
    if not isinstance(grade['reason'],str) or not grade['reason'].strip():
        raise ValueError('Judge reason is missing')
    if outcome != 'invalid_output' and choice is None:
        raise ValueError('Judge must identify a unique choice')
    if outcome == 'correct' and choice != reference or outcome == 'incorrect' and choice == reference:
        raise ValueError('Judge outcome contradicts its extracted choice')
    if not final and (outcome != 'invalid_output' or choice is not None):
        raise ValueError('empty final answer cannot receive an answer grade')
    return grade
