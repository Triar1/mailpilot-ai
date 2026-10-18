from mailpilot.classifier import classify, classify_records

def test_invoice_protected():
    x = classify({'sender':'shop@example.com','subject':'Votre facture de juin','labels':['INBOX']})
    assert x['category']=='finance' and x['suggested_action']=='keep'

def test_promo_not_deleted():
    x = classify({'sender':'ads@example.com','subject':'Soldes exceptionnelles','labels':['INBOX']})
    assert x['suggested_action']=='review_for_cleanup'

def test_ambiguous_is_review():
    x = classify({'sender':'shop@example.com','subject':'Facture et promotion','labels':[]})
    assert x['category']=='other' and x['needs_review']

def test_unknown_is_review():
    assert classify({'sender':'friend@example.com','subject':'Salut','labels':[]})['suggested_action']=='review'

def test_preserves_records():
    rows = classify_records([{'id':'abc','subject':'Hello'}])
    assert rows[0]['id']=='abc' and len(rows)==1
