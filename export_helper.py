import io
from datetime import datetime
from typing import Optional
from fpdf import FPDF

def sanitize_for_pdf(text: str) -> str:
    """
    Sanitize text to be safely encodable by standard FPDF core fonts (latin-1).
    Replaces smart quotes, em-dashes, and special symbols with ASCII equivalents.
    """
    if not text:
        return ""
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2014": "--",
        "\u2013": "-",
        "\u2026": "...",
        "\u2022": "*",
        "\u00a0": " ",
        "\u200b": "",
        "\u2122": "(TM)",
        "\u00ae": "(R)",
        "\u00a9": "(c)",
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    
    # Encode into latin-1 replacing anything unencodable
    return text.encode("latin-1", "replace").decode("latin-1")

class EmailPDF(FPDF):
    def __init__(self, subject: str, recipient: str, category: str, tone: str):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.email_subject = sanitize_for_pdf(subject)
        self.email_recipient = sanitize_for_pdf(recipient)
        self.email_category = sanitize_for_pdf(category)
        self.email_tone = sanitize_for_pdf(tone)
        self.set_margins(left=20, top=20, right=20)
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        # Top accent gradient bar
        self.set_fill_color(99, 102, 241) # Indigo primary
        self.rect(0, 0, 210, 5, "F")

        # Brand header
        self.set_font("Helvetica", "B", 15)
        self.set_text_color(30, 41, 59)
        self.cell(0, 8, "MailGen AI", ln=False)

        self.set_font("Helvetica", "", 9)
        self.set_text_color(100, 116, 139)
        self.cell(0, 8, "Intelligent Email Writing Assistant", ln=True, align="R")

        self.set_draw_color(226, 232, 240)
        self.line(20, 22, 190, 22)
        self.ln(6)

    def footer(self):
        self.set_y(-18)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, f"Generated with MailGen AI | Page {self.page_no()}/{{nb}}", align="C")

def generate_pdf_bytes(
    subject: str,
    body: str,
    recipient_name: str,
    recipient_email: str = "",
    category: str = "Professional Email",
    tone: str = "Professional",
    date_str: Optional[str] = None
) -> bytes:
    """Generate a beautifully formatted PDF document as bytes."""
    date_display = date_str or datetime.now().strftime("%B %d, %Y, %I:%M %p")
    rec_text = recipient_name
    if recipient_email:
        rec_text += f" <{recipient_email}>"

    pdf = EmailPDF(subject, rec_text, category, tone)
    pdf.alias_nb_pages()
    pdf.add_page()

    # Meta card / header box
    pdf.set_fill_color(248, 250, 252) # Slate-50
    pdf.set_draw_color(226, 232, 240) # Slate-200
    pdf.rect(20, 26, 170, 36, "DF")

    # Metadata contents
    pdf.set_xy(24, 29)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(30, 5, "DATE:", ln=False)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 5, sanitize_for_pdf(date_display), ln=True)

    pdf.set_x(24)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(30, 5, "RECIPIENT:", ln=False)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 5, sanitize_for_pdf(rec_text), ln=True)

    pdf.set_x(24)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(30, 5, "CATEGORY:", ln=False)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(79, 70, 229)
    pdf.cell(50, 5, sanitize_for_pdf(category), ln=False)

    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(20, 5, "TONE:", ln=False)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 5, sanitize_for_pdf(tone), ln=True)

    pdf.set_x(24)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(30, 5, "SUBJECT:", ln=False)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 5, sanitize_for_pdf(subject), ln=True)

    pdf.ln(12)

    # Email Body Content
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(30, 41, 59)
    
    clean_body = sanitize_for_pdf(body)
    paragraphs = clean_body.split("\n")
    for para in paragraphs:
        if para.strip():
            pdf.multi_cell(170, 6, para)
            pdf.ln(2)
        else:
            pdf.ln(3)

    return pdf.output()

def generate_txt_content(
    subject: str,
    body: str,
    recipient_name: str,
    recipient_email: str = "",
    category: str = "Professional Email",
    tone: str = "Professional",
    date_str: Optional[str] = None
) -> str:
    """Format email content as clean plain text with headers for download."""
    date_display = date_str or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rec_text = recipient_name
    if recipient_email:
        rec_text += f" <{recipient_email}>"

    separator = "=" * 65
    return f"""{separator}
MAILGEN AI - INTELLIGENT EMAIL WRITING ASSISTANT
{separator}
Date:      {date_display}
Recipient: {rec_text}
Category:  {category}
Tone:      {tone}
Subject:   {subject}
{separator}

{body}

{separator}
Generated with MailGen AI | B.Tech CSE (AI) Project
"""
