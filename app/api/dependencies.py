from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import verify_token

# auto_error=False allows us to handle empty/missing token header gracefully and return a descriptive message
security_scheme = HTTPBearer(auto_error=False)


async def get_current_token(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> str:
    """
    Dependency that enforces Bearer token authentication.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    if not verify_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token
