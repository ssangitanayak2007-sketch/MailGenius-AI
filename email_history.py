import streamlit as st
import pandas as pd
from database import search_history, delete_activity, clear_history

def render():
    st.markdown('<div class="eyebrow">YOUR LOCAL KNOWLEDGE BASE</div>',unsafe_allow_html=True)
    st.title("Email History")
    st.write("Search, filter, revisit, download or remove previous AI tasks stored on this device.")
    a,b=st.columns([2,1])
    with a: term=st.text_input("Search history",placeholder="Search title or message content...")
    with b: feature=st.selectbox("Feature",["All","Email Generator","Email Rewriter","Smart Reply","Follow-up","Summarizer","Translator","Phishing Analysis","Sentiment Analysis","Quality Analysis","Subject Lines"])
    rows=search_history(term,feature)
    st.caption(f"{len(rows)} matching records")
    if rows:
        df=pd.DataFrame([{"ID":r["id"],"Feature":r["feature"],"Title":r["title"],"Created":r["created_at"]} for r in rows])
        st.dataframe(df,use_container_width=True,hide_index=True)
        options={f'#{r["id"]} · {r["feature"]} · {r["title"]} · {r["created_at"]}':r for r in rows}
        selected=st.selectbox("Open a record",list(options.keys()))
        record=options[selected]
        st.markdown("### Record details")
        st.text_area("Input",record["input_text"] or "",height=130,disabled=True)
        st.text_area("Output",record["output_text"] or "",height=200,disabled=True)
        st.download_button("Download this record",f'{record["title"]}\n\nINPUT\n{record["input_text"]}\n\nOUTPUT\n{record["output_text"]}',file_name=f'mailgenius_record_{record["id"]}.txt')
        if st.button("Delete selected record"):
            delete_activity(record["id"]); st.success("Record deleted."); st.rerun()
    else: st.info("No matching activity yet. Your AI work will be saved here automatically.")
    st.markdown("---")
    with st.expander("Danger zone · Clear all history"):
        st.warning("This permanently deletes all saved activity from the local SQLite database.")
        confirm=st.checkbox("I understand and want to clear all history")
        if st.button("Clear all records",disabled=not confirm):
            clear_history(); st.success("History cleared."); st.rerun()
