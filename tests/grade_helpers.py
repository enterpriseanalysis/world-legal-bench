"""Synthetic grade fixtures for arithmetic checks, never provider results."""
def prediction(qid, choice, outcome='correct'):
    text = choice if choice else 'Unresolved final answer'
    return {'id':qid,'prediction':text,'judge_model':'synthetic-test-only',
            'judgement':{'outcome':outcome,'choice':choice,'evidence':text,'reason':'Synthetic arithmetic fixture, not an LLM result.'}}
