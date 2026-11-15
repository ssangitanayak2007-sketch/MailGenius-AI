import streamlit as st

def render_about_project():
    """Render the academic documentation and project details for viva/evaluation."""
    st.markdown('<div class="hero-eyebrow">ACADEMIC & TECHNICAL SPECIFICATIONS</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="hero-title">About MailGen AI</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p style="color: #94a3b8; margin-bottom: 22px;">'
        'B.Tech Computer Science Engineering (Artificial Intelligence) Final Year Project Documentation.'
        '</p>',
        unsafe_allow_html=True
    )

    tab_overview, tab_arch, tab_tech, tab_viva = st.tabs([
        "📖 Project Overview",
        "🏗️ System Architecture",
        "⚙️ Technology Stack",
        "🎓 Viva & Evaluation Guide"
    ])

    with tab_overview:
        st.markdown("### 🎯 Problem Statement & Motivation")
        st.write(
            """
            In modern academic and corporate environments, email remains the primary medium of official communication.
            However, students, early-career professionals, and non-native English speakers frequently encounter significant hurdles:
            - **Tone Miscalibration:** Struggling to strike the right balance between politeness, assertiveness, and formal etiquette.
            - **Writer's Block & Time Inefficiency:** Spending disproportionate time drafting routine job applications, leave requests, or meeting follow-ups.
            - **Grammatical Inaccuracies:** Unintentional syntax errors that damage professional credibility.
            - **Privacy Concerns:** Cloud-based third-party extensions often ingest and store sensitive personal correspondence.

            **MailGen AI** solves these challenges by combining state-of-the-art Large Language Models (Google Gemini)
            with a local, privacy-first SQLite architecture and an executive SaaS design system.
            """
        )

        st.markdown("### 🚀 Core Functional Modules")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown(
                """
                - **AI Email Generator:** Tailors emails across 12 specific categories (Job Applications, Internship Requests, Leave Applications, College/Academic, Complaints, etc.) with 8 tones and 3 length modes.
                - **AI Email Rewriter:** Ingests existing rough drafts to fix grammar, condense verbosity, or elevate executive tone across 7 distinct goals.
                - **Smart Reply Generator:** Understands context from inbound emails to draft intelligent, goal-aligned replies.
                """
            )
        with col_m2:
            st.markdown(
                """
                - **SQLite Persistent History:** Automatically logs all generated and rewritten communications locally with complete search, filter, and deletion controls.
                - **Multi-Format Export Engine:** Exports emails as structured plain text (.txt) and beautifully styled, executive-grade PDF documents (.pdf).
                - **Secure Credential Management:** Supports environment variables (.env), Streamlit secrets, and runtime sidebar input with zero database leakage.
                """
            )

    with tab_arch:
        st.markdown("### 🏗️ Architectural Flow")
        st.markdown(
            """
            ```
            ┌────────────────────────────────────────────────────────┐
            │                  STREAMLIT FRONTEND                    │
            │  (Custom SaaS CSS, Material Accents, Responsive Grid)  │
            └───────────────┬───────────────────────┬────────────────┘
                            │                       │
             User Inputs    ▼                       ▼    Export Requests
            ┌───────────────────────┐      ┌─────────────────────────┐
            │   AI ENGINE / UTILS   │      │   EXPORT ENGINE (FPDF2) │
            │  - Prompt Conditioning│      │  - Branded PDF Builder  │
            │  - Multi-Model Router │      │  - TXT Formatter        │
            │  - Error Interceptor  │      └─────────────────────────┘
            └───────────┬───────────┘
                        │ API Call
                        ▼
            ┌───────────────────────┐      ┌─────────────────────────┐
            │   GOOGLE GEMINI API   │      │   LOCAL SQLITE DATABASE │
            │ (Flash 2.5/2.0/1.5)   │      │   - emails Table        │
            │ - High Speed LLM      │      │   - Indexed Timestamps  │
            │ - Rate-Limit Resilient│      │   - Fast Keyword Search │
            └───────────┬───────────┘      └────────────▲────────────┘
                        │                               │
                        └───────── Auto-Save ───────────┘
            ```
            """
        )

        st.markdown("### 🗄️ Database Schema (`mailgen.db`)")
        st.code(
            """
CREATE TABLE emails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipient_name TEXT NOT NULL,
    recipient_email TEXT DEFAULT '',
    email_subject TEXT NOT NULL,
    email_body TEXT NOT NULL,
    email_category TEXT NOT NULL,
    writing_tone TEXT NOT NULL,
    email_length TEXT DEFAULT 'Medium',
    action_type TEXT DEFAULT 'Generated',
    created_at TEXT NOT NULL
);

CREATE INDEX idx_emails_created ON emails(created_at DESC);
CREATE INDEX idx_emails_category ON emails(email_category);
            """,
            language="sql"
        )

    with tab_tech:
        st.markdown("### ⚙️ Technologies & Libraries Used")
        st.markdown(
            """
            | Layer | Technology | Version | Purpose |
            | :--- | :--- | :--- | :--- |
            | **Frontend** | Streamlit | `>= 1.40.0` | High-performance interactive Python web framework |
            | **Styling** | Custom CSS3 + HTML5 | - | Modern SaaS UI inspired by Grammarly & ChatGPT |
            | **AI Engine** | Google Gemini API (`google-genai`) | `>= 3.0.0` | Multi-model Generative AI inference |
            | **Database** | SQLite3 | Built-in Python | Zero-configuration, serverless relational persistence |
            | **Export** | FPDF2 | `>= 2.8.0` | Programmatic vector PDF generation |
            | **Configuration** | python-dotenv | `>= 1.0.0` | Safe 12-factor environment variable loading |
            """
        )

    with tab_viva:
        st.markdown("### 🎓 Frequently Asked Viva / Evaluation Questions")
        with st.expander("Q1: How does the AI Email Generator modulate tone and length without hallucinations?"):
            st.write(
                "MailGen AI employs structured few-shot prompt engineering and system instructions. "
                "The system explicitly sets target word bounds (e.g. 60-120 words for Short, 150-250 for Medium) "
                "and maps the 8 tone selections to concrete stylistic directives (e.g. 'apologetic' focuses on accountability "
                "and remedial solutions; 'confident' emphasizes definitive verbs and clear milestones)."
            )

        with st.expander("Q2: Why use SQLite instead of a cloud database like Firebase or MongoDB?"):
            st.write(
                "SQLite offers zero external latency, eliminates credential leakage, requires no network connectivity for storage, "
                "and ensures that all user email history remains entirely private on the host machine. For personal and enterprise desktop "
                "productivity assistants, local embedded storage is an industry best practice."
            )

        with st.expander("Q3: How is API resilience and rate-limiting managed?"):
            st.write(
                "The application wraps all Gemini API calls in `_call_gemini_with_fallback`, trying candidate models "
                "(`gemini-2.5-flash`, `gemini-2.0-flash`, `gemini-1.5-flash`). Specific exceptions (`AIRateLimitError`, "
                "`AIConnectionError`, `MissingAPIKeyError`) are isolated so the application gracefully informs the user without crashing."
            )

        with st.expander("Q4: How does the PDF generation handle Unicode characters from LLMs?"):
            st.write(
                "Standard core PDF fonts only support latin-1 encoding. MailGen AI includes a custom sanitization pipeline "
                "in `utils/export_helper.py` that normalizes smart quotes, em-dashes, bullets, and ellipses to ASCII equivalents "
                "prior to compilation, preventing encoding exceptions."
            )
