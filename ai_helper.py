import os
import re
from typing import Dict, Any, Optional, Tuple
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Currently available and supported Gemini models in priority order

# Current supported Gemini models in priority order
CANDIDATE_MODELS = [
    os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip() or "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
]


class MissingAPIKeyError(Exception):
    """Raised when no Gemini API key is configured or provided."""
    pass

class InvalidAPIKeyError(Exception):
    """Raised when Google rejects the API key with 400 API_KEY_INVALID or 401."""
    pass

class PermissionDeniedError(Exception):
    """Raised when the key/project lacks permission or location is restricted (403)."""
    pass

class ModelNotFoundError(Exception):
    """Raised when the requested model is not found (404)."""
    pass

class AIRateLimitError(Exception):
    """Raised when the Gemini API quota or rate limit is reached (429)."""
    pass

class AIConnectionError(Exception):
    """Raised when internet or API connectivity fails."""
    pass

class AIGenerationError(Exception):
    """Raised when the AI model returns an error or empty content."""
    pass

def sanitize_api_key(raw_key: Optional[str]) -> str:
    """
    Thoroughly clean and sanitize an API key:
    - Strips whitespace, tabs, and newlines
    - Strips surrounding single quotes, double quotes, and backticks
    - Strips common environment variable prefixes (e.g., 'GEMINI_API_KEY=', 'export GEMINI_API_KEY=')
    - Filters out dummy placeholder strings
    - Removes internal spaces/line breaks
    """
    if not raw_key:
        return ""
    
    key = str(raw_key).strip()
    
    # Strip common env line prefixes if user copied the whole declaration
    prefixes = [
        "export GEMINI_API_KEY=",
        "GEMINI_API_KEY=",
        "export GOOGLE_API_KEY=",
        "GOOGLE_API_KEY=",
        "API_KEY="
    ]
    for prefix in prefixes:
        if key.startswith(prefix):
            key = key[len(prefix):].strip()
            
    # Strip surrounding quotes and whitespace
    key = key.strip("'\"` \t\r\n")
    
    # Remove internal linebreaks or whitespace
    key = re.sub(r"\s+", "", key)
    
    # Check for common placeholder values
    placeholders = {
        "your_gemini_api_key_here",
        "paste-your-gemini-api-key-here",
        "paste_your_api_key_here",
        "your_api_key",
        "api_key",
        "none",
        "null",
        "undefined",
        "aizasy...",
        "aizasy"
    }
    if key.lower() in placeholders or key.lower().startswith("your_") or key.lower().startswith("paste-"):
        return ""
        
    return key

def mask_api_key(key: str) -> str:
    """Safely mask an API key for UI preview without exposing credentials."""
    clean = sanitize_api_key(key)
    if not clean:
        return "Not Set"
    if len(clean) <= 8:
        return "****"
    return f"{clean[:4]}...{clean[-4:]}"

def get_effective_api_key(provided_key: Optional[str] = None) -> str:
    """
    Resolve the active Gemini API key from explicit parameter,
    Streamlit session state, environment variables, or Streamlit secrets.
    Explicit user parameter takes highest priority.
    """
    # 1. Explicit parameter passed by caller
    clean_provided = sanitize_api_key(provided_key)
    if clean_provided:
        return clean_provided
    
    # 2. Streamlit session state (user entered via sidebar widget)
    try:
        import streamlit as st
        session_key = sanitize_api_key(st.session_state.get("gemini_api_key", ""))
        if session_key:
            return session_key
    except Exception:
        pass

    # 3. Environment variable (from .env or OS environment)
    env_key = sanitize_api_key(os.getenv("GEMINI_API_KEY", ""))
    if env_key:
        return env_key
    
    # 4. Streamlit secrets if configured
    try:
        import streamlit as st
        secret_key = sanitize_api_key(st.secrets.get("GEMINI_API_KEY", ""))
        if secret_key:
            return secret_key
    except Exception:
        pass

    return ""

def classify_gemini_error(err: Exception) -> Exception:
    """
    Inspect a caught Exception from google-genai and return a typed, informative exception.
    Ensures that raw API keys are never exposed in error text.
    """
    err_str = str(err)
    err_lower = err_str.lower()
    code = getattr(err, "code", None)

    # 400 INVALID_ARGUMENT / API_KEY_INVALID
    if code == 400 or "api_key_invalid" in err_lower or "api key not valid" in err_lower:
        return InvalidAPIKeyError(
            "Google rejected the API key (400: API_KEY_INVALID). "
            "The key is unrecognized or improperly formatted. Please verify that you copied the complete key "
            "starting with 'AIza' from Google AI Studio (https://aistudio.google.com/app/apikey) without missing characters."
        )

    # 401 UNAUTHENTICATED
    if code == 401 or "unauthenticated" in err_lower or "401" in err_str:
        return InvalidAPIKeyError(
            "Authentication failed (401: Unauthenticated). "
            "Your Gemini API key is invalid or has expired. Please generate a fresh key at https://aistudio.google.com/app/apikey"
        )

    # 403 PERMISSION_DENIED
    if code == 403 or "permission_denied" in err_lower or "403" in err_str:
        return PermissionDeniedError(
            "Permission denied (403: Permission Denied). The API key does not have permission to access the Gemini API, "
            "the Google Cloud project is disabled, or your geographic region is currently unsupported by Google AI Studio."
        )

    # 404 NOT_FOUND
    if code == 404 or "not_found" in err_lower or "404" in err_str:
        return ModelNotFoundError(
            "Model not found (404: Not Found). The specified Gemini model is not accessible with this API key."
        )

    # 429 RESOURCE_EXHAUSTED
    if code == 429 or "quota" in err_lower or "resource_exhausted" in err_lower or "rate limit" in err_lower:
        return AIRateLimitError(
            "Rate limit or quota exceeded (429: Resource Exhausted). "
            "Please wait a few moments before trying again, or check your quota limits at Google AI Studio."
        )

    # Network / Connection / Timeout
    if (
        "connection" in err_lower
        or "network" in err_lower
        or "timeout" in err_lower
        or "dns" in err_lower
        or "failed to connect" in err_lower
        or "getaddrinfo" in err_lower
        or "remotedisconnected" in err_lower
    ):
        return AIConnectionError(
            "Network connectivity error. Could not establish a connection to Google Gemini API servers. "
            "Please check your internet connection, VPN, or firewall settings."
        )

    return AIGenerationError(f"Gemini API request failed: {err_str}")

def _get_client(api_key: Optional[str] = None):
    """
    Instantiate and return the official google-genai Client.
    Passes the sanitized key explicitly to prevent loading unexpected environment values.
    """
    key = get_effective_api_key(api_key)
    if not key:
        raise MissingAPIKeyError(
            "Gemini API key is not configured. Please paste your Gemini API key in the sidebar "
            "or set GEMINI_API_KEY in your .env file.\n\n"
            "Get a free API key from Google AI Studio: https://aistudio.google.com/app/apikey"
        )
    try:
        from google import genai
        return genai.Client(api_key=key)
    except Exception as e:
        raise AIConnectionError(f"Failed to initialize Gemini client: {e}")

def _call_gemini_with_fallback(
    prompt: str,
    system_instruction: str,
    api_key: Optional[str] = None,
    temperature: float = 0.7
) -> str:
    """
    Invoke Gemini Generate Content with automatic candidate model fallback and comprehensive error handling.
    """
    client = _get_client(api_key)
    from google.genai import types

    last_error: Optional[Exception] = None
    for model_name in CANDIDATE_MODELS:
        try:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=temperature,
            )
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config
            )
            text = getattr(response, "text", "")
            if text and text.strip():
                return text.strip()
        except Exception as e:
            classified = classify_gemini_error(e)
            last_error = classified
            
            # If the API key itself is invalid or permission is denied, fallback will NOT help; stop immediately
            if isinstance(classified, (InvalidAPIKeyError, PermissionDeniedError, AIRateLimitError)):
                raise classified
            
            # If network error, raise immediately
            if isinstance(classified, AIConnectionError):
                raise classified
                
            # If model not found, continue to next candidate model
            continue

    if last_error:
        raise last_error
    raise AIGenerationError("The AI service returned an empty response.")

def test_api_connection(api_key: Optional[str] = None) -> Tuple[bool, str, str]:
    """
    Test the actual Gemini API connection by making a real live API call.
    Returns: (is_success: bool, status_category: str, message: str)
    Categories: 'SUCCESS', 'MISSING_KEY', 'INVALID_KEY', 'PERMISSION_DENIED', 'RATE_LIMIT', 'NETWORK_ERROR', 'MODEL_NOT_FOUND', 'UNKNOWN_ERROR'
    """
    key = get_effective_api_key(api_key)
    if not key:
        return False, "MISSING_KEY", "No Gemini API key provided. Please enter an API key in the sidebar."

    try:
        from google import genai
        client = genai.Client(api_key=key)
        
        last_classified: Optional[Exception] = None
        for model in CANDIDATE_MODELS:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents="Please reply with the single word: READY"
                )
                text = getattr(response, "text", "")
                if text and text.strip():
                    return True, "SUCCESS", f"Connected successfully! Gemini model '{model}' is online and verified."
            except Exception as e:
                classified = classify_gemini_error(e)
                last_classified = classified
                # Critical auth errors apply to all models
                if isinstance(classified, (InvalidAPIKeyError, PermissionDeniedError, AIRateLimitError, AIConnectionError)):
                    break
                continue
                
        if last_classified:
            if isinstance(last_classified, InvalidAPIKeyError):
                return False, "INVALID_KEY", str(last_classified)
            elif isinstance(last_classified, PermissionDeniedError):
                return False, "PERMISSION_DENIED", str(last_classified)
            elif isinstance(last_classified, AIRateLimitError):
                return False, "RATE_LIMIT", str(last_classified)
            elif isinstance(last_classified, AIConnectionError):
                return False, "NETWORK_ERROR", str(last_classified)
            elif isinstance(last_classified, ModelNotFoundError):
                return False, "MODEL_NOT_FOUND", str(last_classified)
            else:
                return False, "UNKNOWN_ERROR", str(last_classified)
                
        return False, "UNKNOWN_ERROR", "Could not obtain response from Gemini API."
    except Exception as e:
        classified = classify_gemini_error(e)
        return False, type(classified).__name__, str(classified)

def parse_subject_and_body(raw_text: str, default_subject: str = "") -> Dict[str, str]:
    """
    Parse model output structured with 'SUBJECT: ...' and 'BODY: ...'.
    """
    subject = default_subject
    body = raw_text

    # Match SUBJECT: <content>
    sub_match = re.search(r"SUBJECT:\s*(.*?)(?:\n|\r\n|BODY:|$)", raw_text, re.IGNORECASE)
    if sub_match:
        subject = sub_match.group(1).strip()

    # Match BODY:\s*<content>
    body_match = re.search(r"BODY:\s*([\s\S]*)", raw_text, re.IGNORECASE)
    if body_match:
        body = body_match.group(1).strip()
    else:
        # If no explicit BODY: marker, remove SUBJECT line if present
        if sub_match:
            body = raw_text.replace(sub_match.group(0), "").strip()

    # Clean markdown bold/brackets around subject if present
    subject = re.sub(r"^[*#\s\"']+|[*#\s\"']+$", "", subject)

    return {
        "subject": subject or default_subject or "Important Update",
        "body": body.strip()
    }

def generate_email_ai(
    recipient_name: str,
    recipient_email: str,
    subject_topic: str,
    purpose: str,
    details: str,
    category: str,
    tone: str,
    length: str,
    api_key: Optional[str] = None
) -> Dict[str, str]:
    """
    Generate a full-featured, contextually tailored email based on user inputs.
    """
    system_instruction = (
        "You are MailGen AI, an elite AI-powered Executive Email Assistant. "
        "You specialize in writing pristine, context-rich, human-like communications that adhere strictly "
        "to industry conventions, appropriate tone, and specified lengths. "
        "Never output placeholders like [Your Name] if identifiable; maintain natural flow and high aesthetic structure."
    )

    length_guidelines = {
        "Short": "Keep it concise (60-120 words), direct, and focused on immediate action.",
        "Medium": "Standard length (150-250 words), balanced context, polite greeting, clear message, and distinct call-to-action.",
        "Detailed": "Comprehensive length (280-450 words), thorough explanation, structured paragraphs or bullet points, and professional closing."
    }
    length_desc = length_guidelines.get(length, "Balanced and structured length.")

    prompt = f"""
Please compose a complete, beautifully structured email based on these exact specifications:

- Email Category: {category}
- Desired Tone: {tone}
- Length Target: {length} ({length_desc})
- Recipient Name: {recipient_name or 'Valued Recipient'}
- Recipient Email: {recipient_email or 'Not specified'}
- Email Topic / Primary Subject: {subject_topic}
- Core Purpose of Email: {purpose}
- Important Details / Specific Instructions: {details or 'Standard professional etiquette'}

OUTPUT FORMAT:
You MUST format your response strictly as follows:
SUBJECT: <Compelling, clear, and relevant subject line without clickbait>
BODY:
<Formal or appropriate salutation tailored to {recipient_name or 'the recipient'}>

<Email body paragraphs formatted with proper spacing, professional sentence flow, and strong etiquette following the {tone} tone and {category} category standards>

<Polite closing sign-off>
[Sender / MailGen AI User]
"""

    raw_response = _call_gemini_with_fallback(
        prompt=prompt,
        system_instruction=system_instruction,
        api_key=api_key,
        temperature=0.65
    )

    return parse_subject_and_body(raw_response, default_subject=subject_topic)

def rewrite_email_ai(
    original_email: str,
    rewrite_option: str,
    target_tone: str,
    custom_instructions: str = "",
    api_key: Optional[str] = None
) -> Dict[str, str]:
    """
    Intelligently rewrite, polish, or transform an existing email.
    """
    system_instruction = (
        "You are MailGen AI's Email Editor and Writing Coach. "
        "Your task is to rewrite and enhance existing emails according to the user's selected improvement goal "
        "and target tone. Always preserve the sender's core intent, key facts, deadlines, and dates while "
        "elevating vocabulary, syntax, clarity, and etiquette."
    )

    prompt = f"""
Please improve and rewrite the following email according to these guidelines:

PRIMARY GOAL: {rewrite_option}
TARGET TONE: {target_tone}
ADDITIONAL INSTRUCTIONS: {custom_instructions or 'None. Apply standard professional polish.'}

ORIGINAL EMAIL:
\"\"\"
{original_email}
\"\"\"

OUTPUT FORMAT:
SUBJECT: <Preserve or improve the subject line>
BODY:
<The revised, enhanced email body>
IMPROVEMENTS_SUMMARY:
- <Bullet point 1 of key change made>
- <Bullet point 2 of key change made>
"""

    raw_response = _call_gemini_with_fallback(
        prompt=prompt,
        system_instruction=system_instruction,
        api_key=api_key,
        temperature=0.5
    )

    # Extract IMPROVEMENTS_SUMMARY if present
    summary = ""
    summary_match = re.search(r"IMPROVEMENTS_SUMMARY:\s*([\s\S]*)", raw_response, re.IGNORECASE)
    clean_text = raw_response
    if summary_match:
        summary = summary_match.group(1).strip()
        clean_text = raw_response[:summary_match.start()].strip()

    parsed = parse_subject_and_body(clean_text)
    parsed["improvements"] = summary or "Enhanced vocabulary, tone modulation, and refined phrasing."
    return parsed

def generate_reply_ai(
    received_email: str,
    reply_style: str,
    reply_intent: str,
    additional_context: str = "",
    api_key: Optional[str] = None
) -> Dict[str, str]:
    """
    Generate an intelligent, context-aware reply to an incoming email.
    """
    system_instruction = (
        "You are MailGen AI's Smart Reply Engine. "
        "Analyze the incoming email carefully, identify the sender's key points, questions, and requests, "
        "and draft an appropriate, contextually sound reply following the user's intent and chosen style."
    )

    prompt = f"""
Please generate an intelligent reply to this received email.

REPLY STYLE: {reply_style}
REPLY INTENT: {reply_intent}
SPECIFIC FACTS / EXTRA CONTEXT: {additional_context or 'Acknowledge politely and address all points.'}

RECEIVED EMAIL:
\"\"\"
{received_email}
\"\"\"

OUTPUT FORMAT:
SUBJECT: Re: <Appropriate reply subject>
BODY:
<Polite greeting acknowledging sender's message>

<Contextually accurate reply addressing all questions, agreeing/proposing as indicated by intent>

<Appropriate sign-off>
[Sender / MailGen AI User]
"""

    raw_response = _call_gemini_with_fallback(
        prompt=prompt,
        system_instruction=system_instruction,
        api_key=api_key,
        temperature=0.6
    )

    return parse_subject_and_body(raw_response, default_subject="Re: Update")
