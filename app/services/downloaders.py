import logging
from abc import ABC, abstractmethod
from typing import Union
import trafilatura
import trafilatura.settings
from app.schemas.extraction import ExtractionRequest
from app.schemas.clean import CleanRequest
from app.services.exceptions import ExtractionError

from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)


class HtmlSource(ABC):
    """
    Abstract base class representing a strategy for acquiring HTML.
    """
    @abstractmethod
    def get_html(self, request: Union[ExtractionRequest, CleanRequest]) -> str:
        """
        Acquire HTML string based on request options.
        """
        pass


class RawHtmlSource(HtmlSource):
    """
    Strategy for raw HTML content provided directly in the request.
    """
    def get_html(self, request: Union[ExtractionRequest, CleanRequest]) -> str:
        if request.raw_html is None:
            raise ExtractionError("No HTML content provided.")
        return request.raw_html


class TrafilaturaUrlSource(HtmlSource):
    """
    Strategy for fetching HTML from a URL using Trafilatura's internal downloader.
    """
    def get_html(self, request: Union[ExtractionRequest, CleanRequest]) -> str:
        if not request.url:
            raise ExtractionError("No URL provided.")

        logger.info("Fetching HTML using Trafilatura for URL: %s", request.url)
        config = trafilatura.settings.use_config()
        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15"
        ]
        config.set("DEFAULT", "USER_AGENTS", "\n".join(agents))
        try:
            html_content = trafilatura.fetch_url(request.url, config=config)
        except Exception as e:
            logger.exception("Trafilatura fetch failed for URL: %s", request.url)
            raise ExtractionError(f"Failed to fetch HTML content from the provided URL: {str(e)}")

        if html_content is None:
            raise ExtractionError("Failed to fetch HTML content from the provided URL.")
        return html_content


class CloakBrowserSource(HtmlSource):
    """
    Strategy for fetching HTML from a URL using CloakBrowser via a CDP service.
    """
    def get_html(self, request: Union[ExtractionRequest, CleanRequest]) -> str:
        if not request.url:
            raise ExtractionError("No URL provided.")

        from app.core.config import settings
        if not settings.CLOAKBROWSER_CDP_URL:
            raise ExtractionError("CloakBrowser CDP service URL is not configured (CLOAKBROWSER_CDP_URL is empty).")

        logger.info("Fetching HTML using CloakBrowser CDP service at %s for URL: %s", settings.CLOAKBROWSER_CDP_URL, request.url)
        try:
            with sync_playwright() as p:
                with p.chromium.connect_over_cdp(settings.CLOAKBROWSER_CDP_URL) as browser:
                    page = browser.new_page()
                    page.goto(request.url)
                    html_content = page.content()
        except Exception as e:
            logger.exception("CloakBrowser CDP fetch failed for URL: %s", request.url)
            raise ExtractionError(f"Failed to fetch HTML content using CloakBrowser CDP: {str(e)}")

        if html_content is None:
            raise ExtractionError("Failed to fetch HTML content using CloakBrowser CDP.")
        return html_content
