from aegis.services.sanitizer import execute_privacy_redaction
from aegis.services.triage import evaluate_threat_matrix
from aegis.models.escrow import UrgencyLevel

def test_sanitization_removes_direct_and_named_entities():
    leaked_text = "Reach out to John Doe at test.user@gmail.com or call 9876543210 regarding the corruption in Chennai."
    clean, count = execute_privacy_redaction(leaked_text)
    
    assert "test.user@gmail.com" not in clean
    assert "9876543210" not in clean
    assert "[REDACTED_" in clean
    assert count >= 2

def test_threat_urgency_classifier():
    urgent_report = "The finance director is threatening blackmail and demanding a bribe."
    urgency, score = evaluate_threat_matrix(urgent_report)
    
    assert urgency == UrgencyLevel.CRITICAL
    assert score >= 0.70