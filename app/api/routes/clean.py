from fastapi import APIRouter, Depends
from app.api.dependencies import get_current_token
from app.schemas.clean import CleanRequest, CleanResponse
from app.services.cleaner import CleanerService

router = APIRouter(prefix="/clean", tags=["cleanup"])


@router.post("", response_model=CleanResponse)
def clean_html(
    request: CleanRequest, _token: str = Depends(get_current_token)
) -> CleanResponse:
    """
    Clean and format HTML content from raw HTML or a URL using BeautifulSoup.
    Requires Bearer token authentication.
    """
    return CleanerService().clean_html(request)
