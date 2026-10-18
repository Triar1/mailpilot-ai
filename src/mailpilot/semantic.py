"""Ollama local metadata-only classifier; no Gmail mutations."""
import json
import urllib.request
from pathlib import Path
from collections import Counter

CATEGORIES=("finance","administrative","security","personal","work_studies","career","reservations","marketing","service_notifications","other")
IMPORTANCE=("critical","high","normal","low")
ACTIONS=("keep","archive_candidate","review_for_cleanup","reply_candidate","review")
PROMPT="""Classify the email from sender and subject ONLY. Return JSON with keys category, importance, suggested_action, reason.
Categories: finance (invoices, bank, receipts); administrative (contracts, identity); security (logins, codes); personal (family, friends); work_studies (work, school); career (job applications and job alerts); reservations (tickets, transport, events, bookings); marketing (ads, promotional newsletters); service_notifications (routine updates); other (unclear).
Importance: critical, high, normal, low. Action: keep, archive_candidate, review_for_cleanup, reply_candidate, review.
A brand can send different types of mail: a Steam receipt is finance, Steam offers are marketing; LinkedIn jobs are career, LinkedIn promotions are marketing. NEVER propose cleanup for finance, security, personal, administrative, or reservations. Be conservative. The email body is not available. Return only JSON."""
def classify(record,model="qwen2.5:3b",timeout=120):
    sample={k:str(record.get(k,""))[:400] for k in ("sender","sender_name","subject")}
    request={"model":model,"stream":False,"format":"json","options":{"temperature":0},
             "messages":[{"role":"system","content":PROMPT},{"role":"user","content":json.dumps(sample,ensure_ascii=False)}]}
    req=urllib.request.Request("http://127.0.0.1:11434/api/chat",data=json.dumps(request).encode(),headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=timeout) as response:
        data=json.load(response)
    result=json.loads(data["message"]["content"])
    for key,valid in (("category",CATEGORIES),("importance",IMPORTANCE),("suggested_action",ACTIONS)):
        if result.get(key) not in valid: raise ValueError(f"Invalid model output: {key}")
    cat=result["category"]
    if result["suggested_action"]=="review_for_cleanup" and cat!="marketing":
        result["suggested_action"]="review"
    if result["suggested_action"]=="archive_candidate" and cat in ("finance","security","personal","administrative","reservations"):
        result["suggested_action"]="keep"
    return {**record,"category":cat,"importance":result["importance"],
            "suggested_action":result["suggested_action"],"reason":str(result.get("reason",""))[:300],
            "classifier":"ollama_local","needs_review":True}
def classify_file(root,account,limit=100,model="qwen2.5:3b"):
    source=root/"secrets"/f"audit_{account}.json"
    data=json.loads(source.read_text(encoding="utf8"))
    records=data["records"][:limit]
    dest=root/"secrets"/f"semantic_{account}.json"
    cached={}
    if dest.exists():
        previous=json.loads(dest.read_text(encoding="utf8"))
        if previous.get("model")==model:
            cached={r["id"]:r for r in previous.get("records",[]) if r.get("classifier")=="ollama_local"}
    results=[]
    for i,record in enumerate(records,1):
        if record["id"] in cached:
            result=cached[record["id"]]
        else:
            try: result=classify(record,model=model)
            except Exception as exc:
                result={**record,"category":"other","importance":"normal","suggested_action":"review",
                        "reason":f"Model error ({type(exc).__name__}); review manually","classifier":"fallback_error","needs_review":True}
        results.append(result)
        if i%10==0 or i==len(records):
            report={"account":data.get("account",account),"model":model,"records":results,
                    "categories":dict(Counter(r["category"] for r in results)),"mode":"read-only"}
            dest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf8")
            print(f"{account}: {i}/{len(records)} processed",flush=True)
    return dest
