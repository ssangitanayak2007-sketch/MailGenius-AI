import streamlit as st
from utils import phishing_scan
from ai_engine import analyse_phishing
from database import save_activity

def render():
    st.markdown('<div class="eyebrow">MESSAGE DEFENCE CENTRE</div>',unsafe_allow_html=True)
    st.title("Phishing & Scam Intelligence")
    st.write("Inspect suspicious emails, SMS messages and links for common warning signs.")
    message=st.text_area("Paste the complete message",height=210,placeholder="Paste message text here. Remove private details before analysis.")
    if st.button("⬡ Analyse security risk",use_container_width=True):
        if not message.strip(): st.warning("Paste a message to analyse.")
        else:
            scan=phishing_scan(message)
            ai_result=""
            try:
                with st.spinner("Checking message patterns and AI context..."):
                    ai_result=analyse_phishing(message,st.session_state.get("gemini_api_key"))
            except Exception as e:
                st.info(f"AI explanation unavailable; showing local indicator scan. ({e})")
            st.session_state["phish_result"]={"scan":scan,"ai":ai_result,"message":message}
            save_activity("Phishing Analysis",f'{scan["level"]} risk · {scan["score"]}/100',message,ai_result or "\n".join(scan["indicators"]),f'score={scan["score"]}')
    result=st.session_state.get("phish_result")
    if result:
        scan=result["scan"]
        st.markdown("### Risk intelligence")
        c1,c2=st.columns([1,2])
        with c1:
            st.markdown(f'<div class="risk-wrap"><div class="metric-label">TEXT-BASED RISK INDICATOR</div><div class="metric-value">{scan["score"]}<span style="font-size:14px;color:#8490a8"> / 100</span></div><b>{scan["level"]} risk signals</b><div class="risk-track"><div class="risk-fill" style="width:{scan["score"]}%"></div></div><div class="muted">Heuristic indicator score</div></div>',unsafe_allow_html=True)
        with c2:
            st.markdown("**Detected indicators**")
            for item in scan["indicators"]: st.markdown(f"- {item}")
            if scan["urls"]:
                st.markdown("**URLs found**")
                for url in scan["urls"]: st.code(url)
        if result["ai"]:
            st.markdown("### AI assessment")
            st.markdown(result["ai"])
        st.warning("Important: This is a text-based screening aid, not proof that a message is safe or malicious. Do not share OTPs, passwords or banking credentials. Verify requests using an independently obtained official contact channel.")
