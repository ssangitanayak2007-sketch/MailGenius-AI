import streamlit as st
from ai_engine import generate_email
from database import save_activity

def render():
    st.markdown('<div class="eyebrow">AI WRITING STUDIO</div>',unsafe_allow_html=True)
    st.title("AI Email Generator")
    st.write("Turn a few notes into a thoughtful, ready-to-edit email.")
    with st.form("email_gen"):
        brief=st.text_area("What should the email communicate?",height=130,placeholder="Example: Ask my project guide for a meeting next week to discuss our progress...")
        a,b=st.columns(2)
        with a:
            recipient=st.selectbox("Recipient",["Professor / Faculty","Recruiter / HR","Manager","Client","Colleague","Friend","Other"])
            tone=st.selectbox("Tone",["Professional","Formal","Friendly","Polite","Confident","Persuasive"])
        with b:
            style=st.selectbox("Writing style",["Clear and direct","Warm and conversational","Structured and detailed","Diplomatic"])
            length=st.selectbox("Length",["Short","Medium","Detailed"])
        personalization=st.text_input("Personalization (optional)",placeholder="Name, role, context, reference number...")
        submitted=st.form_submit_button("✦ Generate email",use_container_width=True)
    if submitted:
        if not brief.strip(): st.warning("Please describe the email you want to create.")
        else:
            try:
                with st.spinner("Crafting your email..."):
                    result=generate_email(brief,recipient,tone,style,length,personalization,st.session_state.get("gemini_api_key"))
                st.session_state["generated_email"]=result
                save_activity("Email Generator","Email draft",brief,result)
            except Exception as e: st.error(f"Could not generate the email: {e}")
    result=st.session_state.get("generated_email")
    if result:
        st.markdown("### Your generated email")
        st.text_area("Edit or copy your email",value=result,height=300,key="generated_email_edit")
        st.download_button("⬇ Download .txt",st.session_state.get("generated_email_edit",result),file_name="mailgenius_email.txt",mime="text/plain")
        st.caption("Review names, facts, dates and attachments before sending.")
