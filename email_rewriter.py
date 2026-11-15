import streamlit as st
from ai_engine import rewrite_email
from database import save_activity

def render():
    st.markdown('<div class="eyebrow">REFINE YOUR MESSAGE</div>',unsafe_allow_html=True)
    st.title("Email Rewriter & Tone Transformer")
    st.write("Improve a draft while preserving the meaning and details.")
    original=st.text_area("Paste your draft",height=190,placeholder="Hi sir, I wanted to ask...")
    a,b=st.columns(2)
    with a: goal=st.selectbox("Improvement goal",["Fix grammar and spelling","Improve professionalism","Make concise","Expand with useful detail","Improve clarity and structure"])
    with b: tone=st.selectbox("Target tone",["Professional","Friendly","Formal","Confident","Polite","Concise"])
    if st.button("✦ Rewrite email",use_container_width=True):
        if not original.strip(): st.warning("Paste an email draft first.")
        else:
            try:
                with st.spinner("Improving your draft..."):
                    result=rewrite_email(original,goal,tone,st.session_state.get("gemini_api_key"))
                st.session_state["rewritten_email"]=result
                save_activity("Email Rewriter","Rewritten email",original,result)
            except Exception as e: st.error(f"Rewrite failed: {e}")
    result=st.session_state.get("rewritten_email")
    if result:
        st.markdown("### Improved version")
        c1,c2=st.columns(2)
        with c1: st.text_area("Original",original,height=240,disabled=True)
        with c2: st.text_area("Rewritten",value=result,height=240,key="rewrite_result")
        st.download_button("⬇ Download rewritten email",st.session_state.get("rewrite_result",result),file_name="rewritten_email.txt")
        st.caption("Comparison is side-by-side. Check that the rewritten version retains your intended meaning.")
