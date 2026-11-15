import re
from collections import Counter
from urllib.parse import urlparse

SUSPICIOUS_TERMS = [
    "verify your account", "urgent action", "account suspended", "click immediately",
    "confirm your password", "share otp", "send otp", "one time password",
    "bank details", "update kyc", "prize", "lottery", "you have won",
    "payment failed", "wire transfer", "gift card", "limited time"
]
URL_RE = re.compile(r"https?://[^\s<>\])}]+|www\.[^\s<>\])}]+", re.I)
SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "cutt.ly"}

def phishing_scan(text):
    lower = text.lower()
    hits = [term for term in SUSPICIOUS_TERMS if term in lower]
    urls = URL_RE.findall(text)
    domains = []
    url_flags = []
    for raw in urls:
        parsed = urlparse(raw if raw.startswith("http") else "https://" + raw)
        domain = (parsed.netloc or "").lower().split("@")[-1].split(":")[0]
        domains.append(domain)
        if domain in SHORTENERS:
            url_flags.append(f"URL shortener detected: {domain}")
        if domain.startswith("xn--") or any(ch.isdigit() for ch in domain.split(".")[0]):
            url_flags.append(f"Unusual-looking domain: {domain}")
        if parsed.scheme != "https":
            url_flags.append(f"Non-HTTPS link: {raw}")
    urgency = any(w in lower for w in ["immediately", "within 24 hours", "act now", "final warning", "urgent"])
    credential = any(w in lower for w in ["password", "otp", "pin", "cvv", "card number", "login"])
    money = any(w in lower for w in ["transfer", "payment", "bank", "refund", "fee", "wallet"])
    score = min(100, len(hits)*11 + len(url_flags)*18 + urgency*15 + credential*20 + money*10)
    level = "High" if score >= 60 else "Moderate" if score >= 30 else "Low"
    indicators = []
    if hits: indicators.append("Suspicious phrases: " + ", ".join(hits))
    if urgency: indicators.append("Urgency or pressure language")
    if credential: indicators.append("Credential, OTP, PIN or payment-card language")
    if money: indicators.append("Financial or payment-related language")
    if url_flags: indicators.extend(url_flags)
    if not indicators: indicators.append("No common text-based indicators detected")
    return {"score": score, "level": level, "indicators": indicators, "urls": urls, "domains": domains}

def word_count(text):
    return len(re.findall(r"\b[\w'-]+\b", text))

def readability_hint(text):
    words = re.findall(r"\b[\w'-]+\b", text)
    sentences = max(1, len(re.findall(r"[.!?]+", text)))
    avg = len(words)/sentences if words else 0
    return {"words": len(words), "sentences": sentences, "avg_words_per_sentence": round(avg, 1),
            "hint": "Easy to scan" if avg <= 18 else "Consider splitting long sentences" }

def highlight_terms(text, terms):
    return [t for t in terms if t.lower() in text.lower()]
