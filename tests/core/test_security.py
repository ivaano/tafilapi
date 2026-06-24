from app.core.security import verify_token
from app.core.config import settings


def test_verify_token_valid():
    """
    Test that verify_token returns True for the configured valid token.
    """
    assert verify_token(settings.API_AUTH_TOKEN) is True


def test_verify_token_invalid():
    """
    Test that verify_token returns False for an invalid token.
    """
    assert verify_token("wrong-token-value") is False
    assert verify_token("") is False
