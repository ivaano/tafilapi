from fastapi import APIRouter, HTTPException, status
from app.services.extractor import ExtractionService
from app.schemas.extraction import ExtractionRequest

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    """
    Perform a simple self-test to validate that the application and extraction engine are working fine.
    """
    dummy_html = "<html><body><h1>App is working</h1><p>The health check is successful.</p></body></html>"
    request = ExtractionRequest(raw_html=dummy_html, output_format="txt")

    try:
        response = ExtractionService().extract_content(request)
        if (
            not response.success
            or not response.data
            or "health check is successful" not in response.data
        ):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Self-test failed: {response.error or 'invalid data extracted'}",
            )
        return {
            "status": "healthy",
            "message": "Application is working fine, extraction self-test succeeded.",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Self-test failed with exception: {str(e)}",
        )
