import re
from aegis.models.escrow import UrgencyLevel

CRITICAL_INDICATORS = {
    "bribe", "assault", "violence", "threat", "blackmail", 
    "suicide", "weapon", "critical", "embezzlement", "extortion"
}
ELEVATED_INDICATORS = {
    "harass", "fraud", "exploit", "leak", "compromised", 
    "vulnerability", "toxic", "discriminate", "stole", "breach"
}

def evaluate_threat_matrix(narrative: str) -> tuple[UrgencyLevel, float]:
    """
    Deterministic threat scoring using semantic keyword density and severity weighting.
    """
    tokens = re.findall(r'\b\w+\b', narrative.lower())
    crit_hits = sum(1 for t in tokens if t in CRITICAL_INDICATORS)
    elev_hits = sum(1 for t in tokens if t in ELEVATED_INDICATORS)

    score = min(1.0, (crit_hits * 0.40) + (elev_hits * 0.20))

    if crit_hits >= 1 or score >= 0.75:
        return UrgencyLevel.CRITICAL, round(score, 2)
    elif elev_hits >= 1 or score >= 0.35:
        return UrgencyLevel.ELEVATED, round(score, 2)
    else:
        return UrgencyLevel.STANDARD, round(score, 2)