import logging
from typing import Literal, Optional, Union
import trafilatura
import trafilatura.settings
from lxml import etree
from app.schemas.extraction import ExtractionRequest, ExtractionResponse
from app.services.exceptions import ExtractionError
from app.services.downloaders import (
    HtmlSource,
    RawHtmlSource,
    TrafilaturaUrlSource,
    CloakBrowserSource,
)

logger = logging.getLogger(__name__)


def document_to_dict(doc: trafilatura.settings.Document) -> dict:
    """
    Helper function to convert a Trafilatura Document to a JSON-serializable dictionary.
    Handles lxml Element objects like body or commentsbody by rendering them to string.
    """
    data = {}
    for attr in doc.__slots__:
        val = getattr(doc, attr, None)
        if val is None:
            data[attr] = None
        elif isinstance(val, (str, list, dict, int, float, bool)):
            data[attr] = val
        elif hasattr(val, "xpath"):
            try:
                data[attr] = etree.tostring(val, encoding="utf-8").decode("utf-8")
            except Exception:
                data[attr] = str(val)
        else:
            data[attr] = str(val)
    return data


class ExtractionService:
    """
    Service responsible for extracting text/metadata from HTML content using Trafilatura.
    """

    def extract_content(self, request: ExtractionRequest) -> ExtractionResponse:
        source_type: Literal["raw_html", "url"] = "raw_html" if request.raw_html is not None else "url"
        url_used = request.url

        logger.info("Starting extraction process for source: %s, URL: %s", source_type, url_used)

        try:
            html_content = self._get_html(request)

            if request.with_metadata:
                logger.info("Extracting metadata...")
                data = self._extract_metadata(html_content, request)
            else:
                logger.info("Extracting main text/content...")
                data = self._extract(html_content, request)

            logger.info("Extraction completed successfully.")
            return self._success(data, source_type, url_used)

        except ExtractionError as e:
            logger.warning("Extraction failed: %s", str(e))
            return self._failure(str(e), source_type, url_used)
        except Exception as e:
            logger.exception("Unexpected error during extraction")
            return self._failure(f"An unexpected error occurred: {str(e)}", source_type, url_used)

    def _source_factory(self, request: ExtractionRequest) -> HtmlSource:
        if request.raw_html is not None:
            return RawHtmlSource()
        elif request.url is not None:
            if request.cloakbrowser:
                return CloakBrowserSource()
            return TrafilaturaUrlSource()
        else:
            raise ExtractionError("No URL or HTML content provided.")

    def _get_html(self, request: ExtractionRequest) -> str:
        source = self._source_factory(request)
        return source.get_html(request)

    def _extract(self, html_content: str, request: ExtractionRequest) -> str:
        options = self._build_extract_options(request)
        try:
            extracted_data = trafilatura.extract(html_content, **options)
            if extracted_data is None:
                raise ExtractionError("Trafilatura was unable to extract meaningful content from the HTML.")
            return extracted_data
        except ExtractionError:
            raise
        except Exception as e:
            raise ExtractionError(f"An error occurred during extraction: {str(e)}")

    def _extract_metadata(self, html_content: str, request: ExtractionRequest) -> dict:
        options = self._build_extract_options(request)
        try:
            doc = trafilatura.extract_with_metadata(html_content, **options)
            if doc is None:
                raise ExtractionError("Trafilatura was unable to extract metadata from the HTML.")
            return document_to_dict(doc)
        except ExtractionError:
            raise
        except Exception as e:
            raise ExtractionError(f"An error occurred during metadata extraction: {str(e)}")

    @staticmethod
    def _build_extract_options(request: ExtractionRequest) -> dict:
        return {
            "output_format": request.output_format,
            "fast": request.fast,
            "favor_precision": request.favor_precision,
            "favor_recall": request.favor_recall,
            "include_comments": request.include_comments,
            "tei_validation": request.tei_validation,
            "target_language": request.target_language,
            "include_tables": request.include_tables,
            "include_images": request.include_images,
            "include_formatting": request.include_formatting,
            "include_links": request.include_links,
            "deduplicate": request.deduplicate,
            "date_extraction_params": request.date_extraction_params,
            "url_blacklist": request.url_blacklist,
            "author_blacklist": request.author_blacklist,
            "prune_xpath": request.prune_xpath,
            "url": request.url,
        }

    @staticmethod
    def _success(data: Union[str, dict], source: str, url: Optional[str]) -> ExtractionResponse:
        return ExtractionResponse(
            success=True,
            data=data,
            source=source,
            url=url,
        )

    @staticmethod
    def _failure(message: str, source: str, url: Optional[str]) -> ExtractionResponse:
        return ExtractionResponse(
            success=False,
            error=message,
            source=source,
            url=url,
        )
