import re
import spacy

nlp = spacy.load("en_core_web_sm")

PHONE_PATTERN = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')

def execute_privacy_redaction(raw_text: str) -> tuple[str, int]:
    """
    Two-pass privacy sanitizer:
    Pass 1: Regex scrubbing for emails and phone numbers.
    Pass 2: SpaCy NER to redact names (PERSON), locations (GPE), and organizations (ORG).
    """
    redaction_count = 0

    scrubbed_stage1, n_emails = EMAIL_PATTERN.subn("[REDACTED_EMAIL]", raw_text)
    scrubbed_stage1, n_phones = PHONE_PATTERN.subn("[REDACTED_PHONE]", scrubbed_stage1)
    redaction_count += (n_emails + n_phones)

    doc = nlp(scrubbed_stage1)
    target_labels = {"PERSON", "GPE", "ORG"}
    spans_to_redact = [
        (ent.start_char, ent.end_char, ent.label_)
        for ent in doc.ents if ent.label_ in target_labels
    ]

    # Process spans in reverse order to preserve string character offsets
    spans_to_redact.sort(key=lambda x: x[0], reverse=True)
    sanitized_text = scrubbed_stage1

    for start, end, label in spans_to_redact:
        sanitized_text = sanitized_text[:start] + f"[REDACTED_{label}]" + sanitized_text[end:]
        redaction_count += 1

    return sanitized_text, redaction_count