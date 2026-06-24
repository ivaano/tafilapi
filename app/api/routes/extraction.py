from fastapi import APIRouter, Depends
from app.api.dependencies import get_current_token
from app.schemas.extraction import ExtractionRequest, ExtractionResponse
from app.services.extractor import ExtractionService

router = APIRouter(prefix="/extract", tags=["extraction"])


@router.post("", response_model=ExtractionResponse)
def extract_html(
    request: ExtractionRequest, _token: str = Depends(get_current_token)
) -> ExtractionResponse:
    """
    Extract content from raw HTML or a URL using Trafilatura.
    Requires Bearer token authentication.
    """
    return ExtractionService().extract_content(request)
