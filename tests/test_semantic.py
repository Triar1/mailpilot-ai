import json
import pytest
from mailpilot.semantic import classify
from mailpilot.review import save,load,evaluate

class Response:
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self,*args):
        return json.dumps({"message":{"content":json.dumps({"category":"finance","importance":"high",
            "suggested_action":"review_for_cleanup","reason":"receipt"})}}).encode()

def test_protected_receipt(monkeypatch):
    monkeypatch.setattr("urllib.request.urlopen",lambda *args,**kwargs:Response())
    result=classify({"id":"x","sender":"steam","subject":"receipt"})
    assert result["category"]=="finance"
    assert result["suggested_action"]=="review"

def test_review_roundtrip(tmp_path):
    save(tmp_path,"account1","x","career","normal","keep")
    assert load(tmp_path,"account1")["x"]["category"]=="career"
    stats=evaluate([{"id":"x","category":"career","importance":"normal","suggested_action":"review"}],load(tmp_path,"account1"))
    assert stats["agreement"]["category"]==1
    assert stats["agreement"]["suggested_action"]==0

def test_invalid_review(tmp_path):
    with pytest.raises(ValueError):save(tmp_path,"account1","x","unknown","normal","keep")
