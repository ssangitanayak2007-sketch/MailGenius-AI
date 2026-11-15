import streamlit as st
from ai_engine import smart_reply, summarise_email, translate_email, quality_analysis, subject_lines
from database import save_activity
from utils import readability_hint

TEMPLATES = {
"Internship application":("Application for [Internship Role]","Dear [Hiring Manager],\n\nI am writing to express my interest in the [Internship Role] opportunity at [Company]. I am currently pursuing [Degree / Year] and have been developing skills in [Relevant Skills].\n\nI would appreciate the opportunity to contribute and learn from your team. I have attached my resume for your consideration.\n\nThank you for your time.\n\nSincerely,\n[Your Name]"),
"Job application":("Application for [Job Title]","Dear [Hiring Manager],\n\nI am interested in applying for the [Job Title] position. My experience in [Area] and skills in [Skills] align with the role's requirements.\n\nI would welcome the opportunity to discuss how I can contribute. Please find my resume attached.\n\nRegards,\n[Your Name]"),
"Leave request":("Leave Request for [Date]","Dear [Name],\n\nI request leave on [Date] due to [Brief Reason]. I will ensure that any pending responsibilities are addressed and will catch up on missed work.\n\nThank you for your understanding.\n\nRegards,\n[Your Name]"),
"Assignment extension":("Request for Assignment Extension","Dear [Professor's Name],\n\nI am writing to request a short extension for [Assignment Name] due to [Brief Reason]. I have completed [Progress] and would be grateful for additional time until [Proposed Date].\n\nThank you for considering my request.\n\nSincerely,\n[Your Name]"),
"Meeting request":("Meeting Request: [Topic]","Hello [Name],\n\nCould we schedule a brief meeting to discuss [Topic]? I am available [Options], but I am happy to work around your schedule.\n\nPlease let me know what works best.\n\nBest,\n[Your Name]"),
"Thank-you email":("Thank You for [Reason]","Dear [Name],\n\nThank you for [specific support / opportunity]. I appreciate the time and effort you took to help me. Your guidance has been valuable.\n\nWith thanks,\n[Your Name]"),
"Project update":("Project Update: [Project Name]","Hello [Name],\n\nHere is a brief update on [Project Name].\n\nCompleted: [Completed Work]\nIn progress: [Current Work]\nNext steps: [Upcoming Work]\n\nPlease let me know if you would like any additional details.\n\nRegards,\n[Your Name]"),
"Complaint email":("Concern Regarding [Issue]","Dear [Team / Name],\n\nI am writing to bring to your attention an issue regarding [Issue]. The situation occurred on [Date] and has resulted in [Impact].\n\nI would appreciate your assistance in reviewing this matter and advising on the next steps.\n\nThank you,\n[Your Name]")
}

def render_replies():
    st.markdown('<div class="eyebrow">CONTEXT-AWARE COMMUNICATION</div>',unsafe_allow_html=True)
    st.title("Smart Reply & Follow-up")
    tab1,tab2=st.tabs(["Smart reply","Follow-up email"])
    with tab1:
        received=st.text_area("Paste the received email",height=170,key="reply_received")
        a,b=st.columns(2)
        with a: intent=st.selectbox("Reply intent",["Accept","Decline politely","Request clarification","Acknowledge","Ask for more time","Custom response"])
        with b: tone=st.selectbox("Tone",["Professional","Polite","Friendly","Formal","Confident"])
        context=st.text_input("Extra context (optional)",key="reply_context")
        if st.button("Generate smart reply",key="reply_btn"):
            if not received.strip(): st.warning("Paste the email you received.")
            else:
                try:
                    with st.spinner("Drafting a contextual reply..."):
                        out=smart_reply(received,intent,tone,context,st.session_state.get("gemini_api_key"))
                    st.session_state["smart_reply_out"]=out
                    save_activity("Smart Reply","Smart reply draft",received,out)
                except Exception as e: st.error(str(e))
        if st.session_state.get("smart_reply_out"): st.text_area("Your reply",st.session_state["smart_reply_out"],height=220,key="reply_edit")
    with tab2:
        kind=st.selectbox("Follow-up situation",["Internship application","Job application","Meeting request","Unanswered email","Project update"])
        original=st.text_area("What are you following up on?",height=130,key="follow_input")
        follow_tone=st.selectbox("Follow-up tone",["Polite and patient","Professional","Confident but courteous","Friendly"],key="follow_tone")
        if st.button("Generate follow-up",key="follow_btn"):
            if not original.strip(): st.warning("Add context for the follow-up.")
            else:
                try:
                    from ai_engine import ask_gemini
                    out=ask_gemini(f"Write a concise {follow_tone} follow-up email for this situation: {kind}. Context: {original}. Avoid sounding demanding. Include subject and body.",st.session_state.get("gemini_api_key"))
                    st.session_state["follow_out"]=out
                    save_activity("Follow-up","Follow-up email",original,out)
                except Exception as e: st.error(str(e))
        if st.session_state.get("follow_out"): st.text_area("Follow-up draft",st.session_state["follow_out"],height=220,key="follow_edit")

def render_language():
    st.markdown('<div class="eyebrow">UNDERSTAND EVERY MESSAGE</div>',unsafe_allow_html=True)
    st.title("Summarizer & Translator")
    tab1,tab2=st.tabs(["Email summarizer","Email translator"])
    with tab1:
        text=st.text_area("Paste a long email",height=190,key="summary_input")
        if st.button("Summarize email"):
            if not text.strip(): st.warning("Paste an email first.")
            else:
                try:
                    with st.spinner("Extracting the essentials..."): out=summarise_email(text,st.session_state.get("gemini_api_key"))
                    st.session_state["summary_out"]=out; save_activity("Summarizer","Email summary",text,out)
                except Exception as e: st.error(str(e))
        if st.session_state.get("summary_out"): st.markdown(st.session_state["summary_out"])
    with tab2:
        text=st.text_area("Paste text to translate",height=170,key="translate_input")
        language=st.selectbox("Translate into",["Hindi","Odia","Bengali","English","Spanish","French","German","Japanese","Arabic","Tamil","Telugu","Marathi"])
        if st.button("Translate email"):
            if not text.strip(): st.warning("Paste text to translate.")
            else:
                try:
                    with st.spinner(f"Translating into {language}..."): out=translate_email(text,language,st.session_state.get("gemini_api_key"))
                    st.session_state["translation_out"]=out; save_activity("Translator",f"Translation · {language}",text,out)
                except Exception as e: st.error(str(e))
        if st.session_state.get("translation_out"): st.text_area("Translation",st.session_state["translation_out"],height=200)

def render_quality():
    st.markdown('<div class="eyebrow">WRITE WITH INTENTION</div>',unsafe_allow_html=True)
    st.title("Email Quality Analyzer & Writing Coach")
    text=st.text_area("Paste an email to review",height=190)
    if text:
        hint=readability_hint(text)
        a,b,c=st.columns(3); a.metric("Word count",hint["words"]); b.metric("Sentences",hint["sentences"]); c.metric("Avg. sentence length",hint["avg_words_per_sentence"])
    if st.button("Analyse email quality"):
        if not text.strip(): st.warning("Enter an email first.")
        else:
            try:
                with st.spinner("Reviewing clarity, tone and readability..."): out=quality_analysis(text,st.session_state.get("gemini_api_key"))
                st.session_state["quality_out"]=out; save_activity("Quality Analysis","Email quality review",text,out)
            except Exception as e: st.error(str(e))
    if st.session_state.get("quality_out"): st.markdown(st.session_state["quality_out"])

def render_templates():
    st.markdown('<div class="eyebrow">START WITH A STRONG STRUCTURE</div>',unsafe_allow_html=True)
    st.title("Templates & Subject Line Studio")
    tab1,tab2=st.tabs(["Professional templates","AI subject lines"])
    with tab1:
        name=st.selectbox("Choose a template",list(TEMPLATES.keys()))
        subject,body=TEMPLATES[name]
        st.text_input("Subject",subject,key="template_subject")
        st.text_area("Template body",body,height=260,key="template_body")
        st.download_button("Download template",f"Subject: {subject}\n\n{body}",file_name="mailgenius_template.txt")
        st.caption("Replace all bracketed placeholders before using the template.")
    with tab2:
        topic=st.text_input("Email topic / purpose")
        recipient=st.text_input("Recipient type", "Recruiter")
        tone=st.selectbox("Subject tone",["Professional","Friendly","Formal","Confident"])
        if st.button("Generate subject lines"):
            if not topic.strip(): st.warning("Enter a topic.")
            else:
                try:
                    with st.spinner("Generating subject ideas..."): out=subject_lines(topic,recipient,tone,st.session_state.get("gemini_api_key"))
                    st.session_state["subject_out"]=out; save_activity("Subject Lines","Subject line ideas",topic,out)
                except Exception as e: st.error(str(e))
        if st.session_state.get("subject_out"): st.markdown(st.session_state["subject_out"])
