"""Human corrections are local JSON, never applied to Gmail."""
import json
from collections import Counter
from .semantic import CATEGORIES,IMPORTANCE,ACTIONS
def load(root,account):
    p=root/"secrets"/f"reviews_{account}.json"
    return json.loads(p.read_text(encoding="utf8")) if p.exists() else {}
def save(root,account,message_id,category,importance,action):
    if account not in ("account1","account2"):raise ValueError("Invalid account")
    for v,options in ((category,CATEGORIES),(importance,IMPORTANCE),(action,ACTIONS)):
        if v not in options:raise ValueError("Invalid correction")
    reviews=load(root,account)
    reviews[message_id]={"category":category,"importance":importance,"suggested_action":action}
    p=root/"secrets"/f"reviews_{account}.json"
    p.parent.mkdir(exist_ok=True,parents=True)
    p.write_text(json.dumps(reviews,ensure_ascii=False,indent=2),encoding="utf8")
def evaluate(records,reviews):
    pairs=[(r,reviews[r["id"]]) for r in records if r["id"] in reviews]
    result={"reviewed":len(pairs),"total":len(records),"agreement":{},"confusion":{}}
    if pairs:
        for field in ("category","importance","suggested_action"):
            result["agreement"][field]=round(sum(r.get(field)==human[field] for r,human in pairs)/len(pairs),3)
        result["confusion"]=dict(Counter(f'{human["category"]} → {r["category"]}' for r,human in pairs))
    return result
