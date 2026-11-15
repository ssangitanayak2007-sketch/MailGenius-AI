import streamlit as st
from database.db import save_email
from utils.ai_helper import (
    generate_reply_ai,
    MissingAPIKeyError,
    InvalidAPIKeyError,
    PermissionDeniedError,
    ModelNotFoundError,
    AIRateLimitError,
    AIConnectionError,
    AIGenerationError
)
from utils.export_helper import generate_txt_content, generate_pdf_bytes

REPLY_STYLES = [
    "Professional",
    "Friendly",
    "Formal",
    "Short and simple"
]

REPLY_INTENTS = [
    "Accept / Agree positively",
    "Decline politely with justification",
    "Request more information / Clarify questions",
    "Propose alternative date / Reschedule",
    "Acknowledge receipt & follow up soon",
    "Negotiate terms / Counter-offer",
    "Custom response instructions"
]

SAMPLE_INCOMING = {
    "💼 Interview Invitation": (
        "From: recruiter@novatech.com\n"
        "Subject: Interview Invitation: AI Engineer Intern Position\n\n"
        "Dear Candidate,\n\n"
        "We reviewed your application and were impressed by your background in AI and full-stack development. "
        "We would love to invite you for a 45-minute technical discussion next week. "
        "Could you please let us know your availability between Tuesday and Thursday from 10 AM to 4 PM?\n\n"
        "Best regards,\n"
        "Talent Acquisition Team | NovaTech Solutions"
    ),
    "📅 Meeting Reschedule Request": (
        "From: advisor@university.edu\n"
        "Subject: Rescheduling Capstone Project Review Meeting\n\n"
        "Hello Team,\n\n"
        "Due to an unexpected faculty meeting, I won't be able to meet tomorrow at 11:00 AM for our project review. "
        "Can we reschedule to Friday at 2:00 PM or Monday morning at 10:00 AM? Please confirm what works best for your team.\n\n"
        "Best,\n"
        "Prof. Williams"
    ),
    "🤝 Partnership Proposal": (
        "From: partnerships@cloudscale.io\n"
        "Subject: Collaboration Opportunity with CloudScale\n\n"
        "Hi Team,\n\n"
        "We came across your MailGen AI application and would love to explore integrating our cloud infrastructure "
        "credits into your student development workflow. Are you open to a quick 15-minute sync this week to discuss?\n\n"
        "Cheers,\n"
        "Elena Rostova | Head of Partnerships"
    )
}

def render_email_reply():
    """Render the AI Email Reply Generator view."""
    st.markdown('<div class="hero-eyebrow">FEATURE 6 · EMAIL REPLY GENERATOR</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="hero-title">Smart Reply Generator</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p style="color: #94a3b8; margin-bottom: 22px;">'
        'Paste an incoming email you received. MailGen AI will analyze the sender’s context and synthesize an articulate, goal-oriented reply.'
        '</p>',
        unsafe_allow_html=True
    )

    # Sample Incoming Emails loader
    st.markdown('<div style="font-size: 11px; font-weight: 700; color: #818cf8; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 8px;">⚡ Test with Incoming Sample Emails:</div>', unsafe_allow_html=True)
    incoming_cols = st.columns(len(SAMPLE_INCOMING))
    for i, (name, email_body) in enumerate(SAMPLE_INCOMING.items()):
        with incoming_cols[i]:
            if st.button(name, key=f"btn_reply_sample_{i}", width="stretch"):
                st.session_state["reply_incoming_text"] = email_body
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('<h3 style="margin-top:0; color:#f8fafc;">📩 Incoming Email Context</h3>', unsafe_allow_html=True)

        received_text = st.text_area(
            "Paste Received Email *",
            value=st.session_state.get("reply_incoming_text", ""),
            height=160,
            placeholder="Paste the email you received from your professor, recruiter, client, or colleague here...",
            key="input_received_email"
        )

        col1, col2 = st.columns(2)
        with col1:
            reply_style = st.selectbox(
                "Reply Style *",
                options=REPLY_STYLES,
                key="select_reply_style"
            )
        with col2:
            reply_intent = st.selectbox(
                "Your Reply Decision / Intent *",
                options=REPLY_INTENTS,
                key="select_reply_intent"
            )

        extra_context = st.text_input(
            "Specific Facts or Details to Include",
            placeholder="e.g., I am free Wednesday at 2 PM, attaching my updated resume, requesting room 302...",
            key="input_reply_context"
        )

        generate_reply_btn = st.button("💬 Draft Smart Reply with AI", width="stretch", key="btn_trigger_reply")

    if generate_reply_btn:
        if not received_text.strip():
            st.warning("⚠️ Please paste the received email before generating a reply.")
        else:
            api_key = st.session_state.get("gemini_api_key", "")
            try:
                with st.spinner("🤖 MailGen AI is analyzing received email and drafting your reply..."):
                    result = generate_reply_ai(
                        received_email=received_text,
                        reply_style=reply_style,
                        reply_intent=reply_intent,
                        additional_context=extra_context,
                        api_key=api_key
                    )

                st.session_state["current_reply"] = {
                    "received": received_text,
                    "subject": result.get("subject", "Re: Communication"),
                    "body": result.get("body", ""),
                    "style": reply_style,
                    "intent": reply_intent
                }

                # Auto-save to SQLite history
                db_id = save_email(
                    recipient_name="Sender of Received Email",
                    email_subject=result.get("subject", "Re: Communication"),
                    email_body=result.get("body", ""),
                    email_category=f"Reply ({reply_intent})",
                    writing_tone=reply_style,
                    action_type="Reply"
                )
                st.session_state["last_saved_id"] = db_id
                st.success(f"✅ Reply drafted successfully and auto-saved to SQLite history (Record #{db_id})!")
            except MissingAPIKeyError as e:
                st.error("🔑 API Key Required")
                st.info(str(e))
            except InvalidAPIKeyError as e:
                st.error("❌ Invalid Gemini API Key (400 / 401)")
                st.warning(str(e))
            except PermissionDeniedError as e:
                st.error("🚫 Permission Denied (403)")
                st.warning(str(e))
            except ModelNotFoundError as e:
                st.error("🔍 Model Not Found (404)")
                st.warning(str(e))
            except AIRateLimitError as e:
                st.error("⏳ Quota / Rate Limit Reached (429)")
                st.warning(str(e))
            except AIConnectionError as e:
                st.error("🌐 Network Connection Error")
                st.warning(str(e))
            except AIGenerationError as e:
                st.error("❌ AI Generation Error")
                st.warning(str(e))
            except Exception as e:
                st.error("An unexpected error occurred:")
                st.warning(str(e))

    # Display Generated Reply
    reply_data = st.session_state.get("current_reply")
    if reply_data:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="hero-eyebrow">DRAFTED RESPONSE</div>', unsafe_allow_html=True)
        st.markdown('<h3>Generated Smart Reply</h3>', unsafe_allow_html=True)

        # Subject line
        st.markdown(
            f"""
            <div class="subject-display-box">
                <div class="subject-tag">REPLY SUBJECT LINE</div>
                <div class="subject-text">{reply_data['subject']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div style="display:flex; gap:10px; margin-bottom:14px; flex-wrap:wrap;">
                <span class="badge-category">🎯 Intent: {reply_data['intent']}</span>
                <span class="badge-tone">🎨 Style: {reply_data['style']}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        edited_reply = st.text_area(
            "Reply Body (Review & Edit):",
            value=reply_data["body"],
            height=280,
            key="text_area_reply_body"
        )
        reply_data["body"] = edited_reply

        # Export & Actions
        st.markdown("#### Export & Actions")
        c1, c2, c3 = st.columns(3)
        with c1:
            with st.popover("📋 Copy Reply"):
                st.caption("Click the copy icon on the top right:")
                st.code(f"Subject: {reply_data['subject']}\n\n{reply_data['body']}", language="markdown")
        with c2:
            txt_reply = generate_txt_content(
                subject=reply_data["subject"],
                body=reply_data["body"],
                recipient_name="Sender",
                category=f"Reply ({reply_data['intent']})",
                tone=reply_data["style"]
            )
            st.download_button(
                "📄 Download as TXT",
                data=txt_reply,
                file_name="email_reply.txt",
                mime="text/plain",
                width="stretch",
                key="btn_dl_reply_txt"
            )
        with c3:
            pdf_reply = generate_pdf_bytes(
                subject=reply_data["subject"],
                body=reply_data["body"],
                recipient_name="Sender",
                category=f"Reply ({reply_data['intent']})",
                tone=reply_data["style"]
            )
            st.download_button(
                "📑 Download as PDF",
                data=bytes(pdf_reply),
                file_name="email_reply.pdf",
                mime="application/pdf",
                width="stretch",
                key="btn_dl_reply_pdf"
            )
