# ✉️ MailGen AI – Intelligent Email Writing Assistant

> **A Modern, Full-Stack, AI-Powered Email Writing & Productivity Platform**  
> *B.Tech Computer Science Engineering (Artificial Intelligence) Capstone Project*

---

## 📌 Executive Summary & Introduction

In today's fast-paced academic, corporate, and entrepreneurial environments, email communication remains the cornerstone of professional relationships. However, drafting context-appropriate, grammatically flawless, and tone-calibrated emails is time-consuming and challenging for many individuals, particularly students and non-native English speakers.

**MailGen AI** is an intelligent, modern SaaS-style web application designed to eliminate writer's block, miscalibrated tone, and grammatical flaws. Leveraging Google Gemini Large Language Models (LLMs) alongside local SQLite persistence and an executive-grade typography export engine, MailGen AI delivers production-grade email drafting, intelligent rewriting, and context-aware inbound reply generation in a privacy-first architecture.

---

## 🎯 Project Objectives

1. **Contextual AI Generation:** Enable users to synthesize complete, ready-to-send emails across **12 distinct real-world categories** (Job Applications, Leave Applications, Business Proposals, College Communications, etc.) with precise control over **8 writing tones** and **3 length constraints**.
2. **Dynamic Email Rewriting:** Provide an intelligent editor capable of polishing existing rough drafts with 7 specialized objectives (improving grammar, enhancing politeness, executive condensing, or tone transformation).
3. **Inbound Smart Replies:** Decipher received emails from faculty, recruiters, or clients and formulate coherent, goal-aligned responses.
4. **Zero-Leakage Local Persistence:** Securely record all generated communications in an embedded **SQLite database** (`mailgen.db`) with full search, filter, and history management.
5. **Executive Multi-Format Export:** Empower users to download beautifully typeset, branded **PDF documents** and clean **TXT files** with strict separation of subject lines and email bodies.
6. **Commercial SaaS UI/UX:** Offer a fluid, responsive dark-mode interface inspired by Grammarly and ChatGPT with rounded cards, smooth hover transitions, and intuitive navigation.

---

## 🚀 Core Features

### 1. AI Email Generator
- **Structured Inputs:** Recipient name, optional recipient email, topic/subject, core purpose, important instructions/constraints.
- **12 Categories:**
  1. Professional Email
  2. Business Email
  3. Job Application Email
  4. Internship Request Email
  5. Leave Application Email
  6. College/Academic Email
  7. Complaint Email
  8. Apology Email
  9. Thank You Email
  10. Meeting Request Email
  11. Follow-up Email
  12. Personal Email
- **8 Writing Tones:** Professional, Formal, Friendly, Casual, Polite, Persuasive, Confident, Apologetic.
- **3 Length Modes:** Short (60–120 words), Medium (150–250 words), Detailed (280–450 words).
- **Quick Test Presets:** 1-click sample loaders (College Leave, Tech Internship, Business Meeting, Mentorship Thanks) for immediate demonstration during project evaluations.

### 2. AI Email Rewriter & Polisher
- Paste any rough, informal, or verbose draft.
- Select from **7 enhancement goals**:
  - *Make it professional*
  - *Correct grammar*
  - *Make it shorter*
  - *Make it more detailed*
  - *Make it more polite*
  - *Improve sentence structure*
  - *Change the tone*
- View before-and-after comparisons and key improvements applied.

### 3. Smart Email Reply Generator
- Ingests inbound emails received from recruiters, advisors, or clients.
- Analyzes context and drafts a targeted reply based on user intent (*Accept*, *Decline*, *Clarify*, *Reschedule*, *Follow up*).
- Four reply styles: *Professional*, *Friendly*, *Formal*, and *Short and simple*.

### 4. SQLite Persistent History
- Automatically indexes all generated emails, rewritten drafts, and smart replies.
- Fast multi-field keyword search across subjects, recipient names, and bodies.
- Categorical and tonal filtering.
- One-click copy, individual deletion, bulk CSV export, and complete database clearing.

### 5. Multi-Format Export & One-Click Copy
- **Separate Formatting:** Clean separation between the Email Subject Line and the formatted Body.
- **Plain Text (.txt):** Neatly formatted text with headers, timestamps, and recipient metadata.
- **Executive PDF (.pdf):** Vector PDF generated via `fpdf2` featuring brand accent lines, metadata cards, clean margins, and Unicode-safe character encoding.
- **Quick Copy:** Instant copy blocks for clipboard transfer into Gmail, Outlook, or Apple Mail.

---

## 🏗️ System Architecture

```
┌────────────────────────────────────────────────────────┐
│                   STREAMLIT FRONTEND                   │
│   (SaaS Design System, Custom CSS3, Responsive Grid)   │
└───────────────┬───────────────────────┬────────────────┘
                │                       │
 User Prompts   ▼                       ▼   Export Calls
┌───────────────────────┐      ┌─────────────────────────┐
│   UTILS / AI HELPER   │      │  EXPORT HELPER (FPDF2)  │
│  - Prompt Engineering │      │  - Branded PDF Builder  │
│  - Multi-Model Router │      │  - TXT Formatter        │
│  - Error Interceptor  │      └─────────────────────────┘
└───────────┬───────────┘
            │ API Call
            ▼
┌───────────────────────┐      ┌─────────────────────────┐
│   GOOGLE GEMINI API   │      │  SQLITE LOCAL DATABASE  │
│  (Flash 2.5/2.0/1.5)  │      │  - emails Table         │
│  - High Speed NLP     │      │  - Indexed Timestamps   │
│  - Zero Data Leak     │      │  - Search & Retrieval   │
└───────────┬───────────┘      └────────────▲────────────┘
            │                               │
            └────────── Auto-Save ──────────┘
```

---

## ⚙️ Technology Stack

| Layer | Component | Version | Role / Justification |
| :--- | :--- | :--- | :--- |
| **Frontend** | Streamlit | `>= 1.40.0` | Rapid, interactive Python web application framework |
| **Styling** | Custom CSS3 & HTML5 | - | Modern SaaS dark mode inspired by ChatGPT and Grammarly |
| **AI Engine** | Google Gemini API (`google-genai`) | `>= 1.0.0` | State-of-the-art Generative AI for natural language reasoning |
| **Database** | SQLite3 | Native | Zero-dependency, file-based embedded relational database |
| **PDF Generation** | FPDF2 | `>= 2.8.0` | Lightweight, Unicode-sanitized PDF document compiler |
| **Configuration** | python-dotenv | `>= 1.0.0` | 12-factor application environment variable management |
| **Data Handling** | Pandas | `>= 2.0.0` | Tabular data manipulation and CSV export |

---

## 📁 Project Folder Structure

```
MailGenius_AI/
│
├── app.py                      # Main application entry point & navigation
├── requirements.txt            # Python dependencies
├── README.md                   # Comprehensive project documentation
├── .env                        # Local environment variables (API keys)
├── .env.example                # Example template for environment configuration
├── .gitignore                  # Git ignore rules for virtualenvs and secrets
├── test_app.py                 # Automated system verification test suite
├── run_app.bat                 # Windows 1-click launch batch script
│
├── database/
│   ├── __init__.py
│   ├── db.py                   # SQLite schema, CRUD operations & metrics
│   └── mailgen.db              # Local SQLite database file (auto-generated)
│
├── modules/
│   ├── __init__.py
│   ├── dashboard.py            # Modern dashboard with KPI metrics & recent activity
│   ├── email_generator.py      # Feature 1-4: 12 Categories, 8 Tones, 3 Lengths
│   ├── email_rewriter.py       # Feature 5: 7 Rewrite & Polish Objectives
│   ├── email_reply.py          # Feature 6: Inbound Context-Aware Reply Generator
│   ├── email_history.py        # Feature 7: Persistent SQLite History & Search
│   └── about_project.py        # Academic viva & architectural documentation
│
├── utils/
│   ├── __init__.py
│   ├── ai_helper.py            # Gemini API integration & multi-model fallback
│   └── export_helper.py        # PDF & TXT formatting and sanitization engine
│
└── assets/
    └── style.css               # SaaS CSS styles (colors, cards, typography)
```

---

## 🛠️ Installation & Setup Guide

### 1. Prerequisites
- **Python 3.10 to 3.14** installed on your system.
- Git (optional, for version control).

### 2. Clone or Navigate to the Project Directory
```bash
cd C:\Users\ssang\Downloads\MailGenius_AI\MailGenius_AI
```

### 3. Create and Activate a Virtual Environment
```bash
# Windows (PowerShell or Command Prompt)
python -m venv .venv
.\.venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure the Google Gemini API Key
You can obtain a **100% free Gemini API key** from Google AI Studio:
👉 **[https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)**

Create a `.env` file in the project folder (or copy from `.env.example`):
```bash
copy .env.example .env
```
Open `.env` and set your key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

> 💡 **In-App API Key Entry:** You can also paste your Gemini API key directly into the **Google Gemini API Key** input field in the sidebar of the running application. It will be active immediately for your session without restarting the server!

---

## ▶️ Running the Application

### Option A: Using the Windows Batch Script
Simply double-click `run_app.bat` in the project folder.

### Option B: Using the Command Line
```bash
# Activate your virtual environment first
.\.venv\Scripts\activate

# Run the Streamlit application
streamlit run app.py
```

Once started, Streamlit will automatically open your default browser at:
🌐 **`http://localhost:8501`**

---

## 🧪 Automated Testing & Verification

Run the built-in system verification suite:
```bash
python test_app.py
```
This tests:
- SQLite database schema initialization, insertion, retrieval, and deletion.
- Plain text (.txt) export compilation.
- Executive PDF (.pdf) vector compilation with Unicode sanitization.
- AI response parsing (`SUBJECT:` and `BODY:` extraction).

---

## 🎓 Academic Viva / Evaluation Guide

### Q1: What makes this project more advanced than a basic wrapper around an LLM?
**Answer:** MailGen AI implements a complete full-stack architecture:
- Dynamic prompt engineering enforcing word count bounds and distinct tonal traits across 12 realistic communication domains.
- Multi-model routing (`gemini-2.5-flash` $\to$ `gemini-2.0-flash` $\to$ `gemini-1.5-flash`) with error resilience for rate-limits and network dropouts.
- Embedded relational persistence via SQLite (`mailgen.db`) with keyword indexing.
- Custom vector PDF compiler with character sanitization handling Latin-1 limitations.
- Modern dark-mode UI with session-synchronized navigation.

### Q2: How does the application prevent credential leakage?
**Answer:** The Gemini API key is loaded via `python-dotenv` into memory or held in Streamlit's ephemeral session state. The API key is **never written to the SQLite database** or exposed in client-facing HTML.

---

## 👨‍💻 Author & Attribution
- **Student Name:** College B.Tech CSE (AI) Student
- **Degree:** Bachelor of Technology in Computer Science and Engineering (Artificial Intelligence)
- **Year:** 2026–2027
- **License:** MIT License
