import secrets
import string

def generate_claim_token() -> str:
    """
    Generates an unguessable tracking code using CSPRNG.
    Format: AEGIS-XXXX-XXXX-XXXX-XXXX
    """
    alphabet = string.ascii_uppercase + string.digits
    blocks = [''.join(secrets.choice(alphabet) for _ in range(4)) for _ in range(4)]
    return f"AEGIS-{'-'.join(blocks)}"