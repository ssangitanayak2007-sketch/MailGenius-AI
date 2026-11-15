import streamlit as st
from ai_engine import sentiment_analysis
from database import save_activity
from utils import readability_hint

def render():
    st.markdown('<div class="eyebrow">COMMUNICATION INSIGHTS</div>',unsafe_allow_html=True)
    st.title("Email Sentiment Analyzer")
    st.write("Understand the emotional tone behind a message and make it more constructive.")
    text=st.text_area("Paste an email or message",height=190)
    if st.button("◉ Analyse sentiment",use_container_width=True):
        if not text.strip(): st.warning("Enter a message first.")
        else:
            try:
                with st.spinner("Reading tone and context..."):
                    result=sentiment_analysis(text,st.session_state.get("gemini_api_key"))
                st.session_state["sentiment_result"]=result
                save_activity("Sentiment Analysis","Sentiment review",text,result)
            except Exception as e: st.error(f"Analysis failed: {e}")
    if st.session_state.get("sentiment_result"):
        st.markdown("### Analysis")
        st.markdown(st.session_state["sentiment_result"])
        hint=readability_hint(text)
        a,b,c=st.columns(3)
        a.metric("Words",hint["words"]); b.metric("Sentences",hint["sentences"]); c.metric("Avg. words / sentence",hint["avg_words_per_sentence"])
        st.caption(hint["hint"])
