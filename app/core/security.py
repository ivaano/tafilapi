from app.core.config import settings


def verify_token(token: str) -> bool:
    """
    Verifies that the provided token matches the configured API auth token.
    """
    return token == settings.API_AUTH_TOKEN
