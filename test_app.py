import sys
from pathlib import Path

# Add project root
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from database.db import (
    init_db,
    save_email,
    get_all_emails,
    get_email_by_id,
    delete_email,
    clear_all_emails,
    get_statistics
)
from utils.export_helper import generate_pdf_bytes, generate_txt_content, sanitize_for_pdf
from utils.ai_helper import (
    parse_subject_and_body,
    sanitize_api_key,
    mask_api_key,
    classify_gemini_error,
    test_api_connection,
    MissingAPIKeyError,
    InvalidAPIKeyError,
    PermissionDeniedError,
    ModelNotFoundError,
    AIRateLimitError,
    AIConnectionError,
    AIGenerationError,
    get_effective_api_key
)

def test_key_sanitization():
    print("--> Testing API Key Sanitization & Masking...")
    # 1. Plain key
    assert sanitize_api_key("AIzaSy1234567890") == "AIzaSy1234567890"

    # 2. Key with surrounding whitespace and quotes
    assert sanitize_api_key("  'AIzaSy1234567890'  ") == "AIzaSy1234567890"
    assert sanitize_api_key('  "AIzaSy1234567890"  ') == "AIzaSy1234567890"
    assert sanitize_api_key('`AIzaSy1234567890`') == "AIzaSy1234567890"

    # 3. Key with env prefix
    assert sanitize_api_key("GEMINI_API_KEY=AIzaSy1234567890") == "AIzaSy1234567890"
    assert sanitize_api_key("export GEMINI_API_KEY='AIzaSy1234567890'") == "AIzaSy1234567890"

    # 4. Placeholder rejection
    assert sanitize_api_key("your_gemini_api_key_here") == ""
    assert sanitize_api_key("paste-your-gemini-api-key-here") == ""
    assert sanitize_api_key("YOUR_API_KEY") == ""
    assert sanitize_api_key("") == ""
    assert sanitize_api_key(None) == ""

    # 5. Masking
    assert mask_api_key("AIzaSy1234567890") == "AIza...7890"
    assert mask_api_key("") == "Not Set"
    print("    [PASS] Key sanitization and masking logic verified")

def test_error_classification():
    print("--> Testing Gemini Error Classification...")

    # Mock 400 API_KEY_INVALID error
    class MockError(Exception):
        def __init__(self, message, code=None):
            super().__init__(message)
            self.code = code

    e_400 = MockError("400 INVALID_ARGUMENT: API key not valid. Please pass a valid API key. API_KEY_INVALID", code=400)
    classified_400 = classify_gemini_error(e_400)
    assert isinstance(classified_400, InvalidAPIKeyError), f"Expected InvalidAPIKeyError, got {type(classified_400)}"
    assert "Google rejected the API key (400: API_KEY_INVALID)" in str(classified_400)

    # Mock 401 Unauthenticated
    e_401 = MockError("401 UNAUTHENTICATED: Request had invalid authentication credentials.", code=401)
    classified_401 = classify_gemini_error(e_401)
    assert isinstance(classified_401, InvalidAPIKeyError)

    # Mock 403 Permission Denied
    e_403 = MockError("403 PERMISSION_DENIED: The caller does not have permission", code=403)
    classified_403 = classify_gemini_error(e_403)
    assert isinstance(classified_403, PermissionDeniedError)

    # Mock 404 Model Not Found
    e_404 = MockError("404 NOT_FOUND: Model not found", code=404)
    classified_404 = classify_gemini_error(e_404)
    assert isinstance(classified_404, ModelNotFoundError)

    # Mock 429 Rate Limit
    e_429 = MockError("429 RESOURCE_EXHAUSTED: Quota exceeded", code=429)
    classified_429 = classify_gemini_error(e_429)
    assert isinstance(classified_429, AIRateLimitError)

    # Mock Network Error
    e_net = MockError("Failed to connect to generativelanguage.googleapis.com: getaddrinfo failed")
    classified_net = classify_gemini_error(e_net)
    assert isinstance(classified_net, AIConnectionError)

    print("    [PASS] Error classification correctly identifies 400, 401, 403, 404, 429, and Network failures")

def test_connection_tester_with_invalid_key():
    print("--> Testing Connection Tester with Invalid Key...")
    success, category, message = test_api_connection("invalid_dummy_key_12345")
    assert success is False
    assert category in ("INVALID_KEY", "NETWORK_ERROR"), f"Expected INVALID_KEY or NETWORK_ERROR, got {category}"
    print(f"    [PASS] Connection tester response ({category}): {message[:60]}...")

def test_database():
    print("--> Testing SQLite Database Operations...")
    init_db()
    
    email_id = save_email(
        recipient_name="Dr. Alan Turing",
        email_subject="Test Subject: Machine Intelligence Inquiry",
        email_body="Dear Dr. Turing,\n\nWe are conducting research on neural reasoning systems.\n\nBest regards,\nStudent",
        email_category="College/Academic Email",
        writing_tone="Formal",
        recipient_email="alan.turing@cambridge.ac.uk",
        email_length="Short",
        action_type="Generated"
    )
    assert email_id > 0
    record = get_email_by_id(email_id)
    assert record is not None
    assert record["recipient_name"] == "Dr. Alan Turing"

    filtered = get_all_emails(category="College/Academic Email")
    assert len(filtered) >= 1

    stats = get_statistics()
    assert stats["total_emails"] >= 1

    deleted = delete_email(email_id)
    assert deleted is True
    print("    [PASS] SQLite operations verified")

def test_export():
    print("--> Testing Export Engine (PDF & TXT)...")
    subject = "Request for Internship — AI Systems"
    body = "Dear Hiring Manager,\n\nI am writing to express strong enthusiasm for the role… Best,\nCandidate"
    
    txt_out = generate_txt_content(
        subject=subject,
        body=body,
        recipient_name="HR Director",
        category="Internship Request Email",
        tone="Confident"
    )
    assert "HR Director" in txt_out

    pdf_bytes = generate_pdf_bytes(
        subject=subject,
        body=body,
        recipient_name="HR Director",
        category="Internship Request Email",
        tone="Confident"
    )
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF")
    print("    [PASS] Export engine verified")

if __name__ == "__main__":
    print("==================================================")
    print("RUNNING MAILGEN AI COMPREHENSIVE INTEGRATION TESTS")
    print("==================================================")
    test_key_sanitization()
    test_error_classification()
    test_connection_tester_with_invalid_key()
    test_database()
    test_export()
    print("==================================================")
    print("ALL TESTS PASSED WITH ZERO ERRORS!")
    print("==================================================")
