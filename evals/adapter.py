"""Normalize API responses without granting the model customer confirmation authority.
The adapter records structure only. It does not prove the FE confirmation path or DB safety.
"""
def product_response(raw):
    mapping={'show_candidates':'candidates','ask_clarification':'clarify','unidentified':'unidentified'}
    candidates=raw.get('candidates',[])
    return {'action':mapping.get(raw.get('action'),'invalid'),
            'candidate_ids':[c.get('id') for c in candidates if c.get('kind') in {'exact','confirm'}],
            'alternative_ids':[c.get('id') for c in candidates if c.get('kind')=='alternative'],
            'confirmed_sku':raw.get('confirmed_sku'),
            'confirmation_required':True,
            'question':raw.get('question'),
            'raw_kind_valid':all(c.get('kind') in {'exact','confirm','alternative'} for c in candidates)}


def merchant_response(raw):
    intent=raw.get('intent');scope=raw.get('scope')
    if intent=='clarify' or scope=='clarify':
        return {'action':'clarify','question':raw.get('question'),'confirmation_required':True}
    constraints={k:v for k,v in (raw.get('constraints') or {}).items() if v is not None and v!=[] and v is not False}
    return {'action':'propose','confirmation_required':True,'command':{'intent':intent,'scope':scope,'constraints':constraints}}
