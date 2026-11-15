import os
from utils.ai_helper import (
    _call_gemini_with_fallback,
    parse_subject_and_body,
    sanitize_api_key,
    get_effective_api_key,
    test_api_connection,
    MissingAPIKeyError,
    InvalidAPIKeyError,
    PermissionDeniedError,
    AIRateLimitError,
    AIConnectionError,
    AIGenerationError,
    CANDIDATE_MODELS
)

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

class AIUnavailableError(RuntimeError):
    pass

def ask_gemini(prompt, api_key=None, system_instruction=None, temperature=0.65):
    try:
        return _call_gemini_with_fallback(
            prompt=prompt,
            system_instruction=system_instruction or "You are MailGenius AI, an executive email-writing assistant.",
            api_key=api_key,
            temperature=temperature
        )
    except Exception as e:
        raise AIUnavailableError(str(e))

def generate_email(description, recipient, tone, style, length, personalization="", api_key=None):
    prompt = f"""Create a polished email from this brief.
Brief: {description}
Recipient type: {recipient}
Tone: {tone}
Writing style: {style}
Length: {length}
Personalization/context: {personalization or "None"}
Return exactly:
SUBJECT: <subject>
BODY:
<email body>"""
    return ask_gemini(prompt, api_key)

def rewrite_email(text, goal, tone, api_key=None):
    return ask_gemini(f"Rewrite the email below. Goal: {goal}. Desired tone: {tone}. Preserve all facts and intent. Return a subject only if one exists, then the revised email.\n\nEMAIL:\n{text}", api_key)

def smart_reply(text, intent, tone, context="", api_key=None):
    return ask_gemini(f"Draft a context-aware reply to the received email. Reply intent: {intent}. Tone: {tone}. Extra context: {context or 'None'}. Do not invent commitments or facts. Include a subject if useful.\n\nReceived email:\n{text}", api_key)

def summarise_email(text, api_key=None):
    return ask_gemini("Summarize this email. Include a short overview, key points, deadlines (write 'None stated' if absent), and action items (write 'None stated' if absent). Do not invent dates.\n\n" + text, api_key)

def translate_email(text, language, api_key=None):
    return ask_gemini(f"Translate the following email into {language}. Preserve meaning, names, dates, formatting, and tone. Return only the translation.\n\n{text}", api_key)

def sentiment_analysis(text, api_key=None):
    return ask_gemini("Analyse the sentiment and emotional tone of this email. Give sentiment (positive/negative/neutral), tone, phrases influencing the result, and one constructive improvement.\n\n" + text, api_key)

def quality_analysis(text, api_key=None):
    return ask_gemini("Review this email for grammar, readability, clarity, professionalism and tone. Give heuristic scores out of 10 for each and list actionable improvements.\n\n" + text, api_key)

def subject_lines(topic, recipient, tone, api_key=None):
    return ask_gemini(f"Generate 8 distinct, relevant email subject lines. Topic: {topic}. Recipient: {recipient}. Tone: {tone}. Keep them clear and non-clickbait. Number the options.", api_key)
