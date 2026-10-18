"""Private, read-only Streamlit review UI."""
import json
from pathlib import Path
import pandas as pd
import streamlit as st
from mailpilot.review import load,save,evaluate
from mailpilot.semantic import CATEGORIES,IMPORTANCE,ACTIONS

st.set_page_config(page_title="MailPilot AI v0.3",page_icon="📨",layout="wide")
st.title("📨 MailPilot AI — Local Intelligence")
st.caption("v0.3 · Ollama classification · Human corrections · Gmail READ-ONLY")
st.warning("Local-only dashboard. Suggestions and corrections never modify Gmail. Do not publish personal data.")
root=Path.cwd()
for account in ("account1","account2"):
    st.subheader(account)
    path=root/"secrets"/f"semantic_{account}.json"
    if not path.exists():
        st.info(f"Run: python -m mailpilot.semantic_cli --account {account} --limit 100")
        continue
    report=json.loads(path.read_text(encoding="utf8"))
    records=report["records"]
    if not records: continue
    df=pd.DataFrame(records)
    st.caption(f'{report["account"]} · model {report["model"]}')
    a,b,c=st.columns(3)
    a.metric("Analyzed",len(df))
    b.metric("Other",int((df.category=="other").sum()))
    c.metric("Model errors",int((df.classifier=="fallback_error").sum()))
    st.bar_chart(df.category.value_counts())
    chosen=st.multiselect("Categories",CATEGORIES,default=list(CATEGORIES),key=f"filter_{account}")
    corrections=load(root,account)
    only_pending=st.checkbox("Show unreviewed only",value=True,key=f"pending_{account}")
    view=df[df.category.isin(chosen)]
    if only_pending:view=view[~view.id.isin(corrections)]
    st.dataframe(view[["sender","subject","category","importance","suggested_action","reason","classifier"]],
                 hide_index=True,width="stretch")
    if not view.empty:
        options=view.id.tolist()
        selected=st.selectbox("Review a message",options,key=f"selected_{account}",
            format_func=lambda mid: next((f'{r["sender"][:35]} — {r["subject"][:65]}' for r in records if r["id"]==mid),mid))
        r=next(x for x in records if x["id"]==selected)
        prior=corrections.get(selected,{})
        with st.form(f"review_{account}_{selected}"):
            st.write("**Sender:**",r["sender"])
            st.write("**Subject:**",r["subject"])
            cat=st.selectbox("Correct category",CATEGORIES,index=CATEGORIES.index(prior.get("category",r["category"])))
            imp=st.selectbox("Correct importance",IMPORTANCE,index=IMPORTANCE.index(prior.get("importance",r["importance"])))
            act=st.selectbox("Correct action",ACTIONS,index=ACTIONS.index(prior.get("suggested_action",r["suggested_action"])))
            if st.form_submit_button("Save correction"):
                save(root,account,selected,cat,imp,act)
                st.success("Saved locally; Gmail unchanged.")
                st.rerun()
    stats=evaluate(records,corrections)
    st.markdown("#### Evaluation on reviewed messages")
    st.write(f'Reviewed: {stats["reviewed"]}/{stats["total"]}')
    if stats["reviewed"]:
        st.dataframe(pd.DataFrame([{"Dimension":k,"Agreement":v} for k,v in stats["agreement"].items()]),hide_index=True)
        st.json(stats["confusion"])
        st.caption("Agreement on self-selected reviewed messages is NOT unbiased accuracy. Review a random sample for reliable estimates.")
