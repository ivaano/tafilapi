import logging
from typing import Literal, Optional, Dict, List, Set
from bs4 import BeautifulSoup, Comment

from app.schemas.clean import CleanRequest, CleanResponse
from app.services.exceptions import CleanError
from app.services.downloaders import (
    HtmlSource,
    RawHtmlSource,
    TrafilaturaUrlSource,
    CloakBrowserSource,
)

logger = logging.getLogger(__name__)

# Map tag replacements
REPLACEMENTS: Dict[str, str] = {
    "strike": "del",
    "tt": "code",
    "acronym": "abbr",
    "dir": "ul",
    "listing": "pre",
    "xmp": "pre",
    "plaintext": "pre",
}

# Tags to decompose (completely remove along with their children) if they are not allowed
DECOMPOSE_TAGS: Set[str] = {
    "script",
    "style",
    "iframe",
    "noscript",
    "canvas",
    "svg",
    "math",
    "template",
    "embed",
    "object",
    "select",
    "option",
    "button",
    "input",
    "textarea",
    "form",
    "label",
    "fieldset",
    "legend",
    "link",
}

# Allowed tags and attributes for the 'styled' level
ALLOWED_TAGS_STYLED: Dict[str, List[str]] = {
    "html": ["lang"],
    "head": [],
    "meta": ["charset", "name", "content"],
    "title": [],
    "body": [],
    "style": [],
    "p": [],
    "blockquote": ["cite"],
    "hr": [],
    "figure": [],
    "figcaption": [],
    "a": ["href", "title", "target"],
    "strong": [],
    "em": [],
    "b": [],
    "i": [],
    "s": [],
    "u": [],
    "br": [],
    "h1": [], "h2": [], "h3": [], "h4": [], "h5": [], "h6": [],
    "img": ["src", "alt", "width", "height", "loading"],
    "picture": [],
    "source": ["srcset", "sizes", "media", "type", "src"],
    "video": ["src", "width", "height", "poster", "controls", "preload"],
    "audio": ["src", "controls", "preload"],
    "track": ["src", "kind", "srclang", "label", "default"],
    "table": [],
    "caption": [],
    "thead": [],
    "tbody": [],
    "tfoot": [],
    "tr": [],
    "th": ["colspan", "rowspan"],
    "td": ["colspan", "rowspan"],
    "col": ["span"],
    "colgroup": ["span"],
    "code": [],
    "pre": [],
    "ul": [],
    "ol": ["start", "type", "reversed"],
    "li": [],
    "dl": [],
    "dt": [],
    "dd": [],
    "abbr": ["title"],
    "cite": [],
    "dfn": [],
    "kbd": [],
    "samp": [],
    "var": [],
    "mark": [],
    "small": [],
    "q": [],
    "wbr": [],
    "del": ["datetime", "cite"],
    "ins": ["datetime", "cite"],
    "sub": [],
    "sup": [],
    "time": ["datetime"],
    "article": [],
    "section": [],
    "main": [],
    "header": [],
    "footer": [],
    "nav": [],
    "aside": [],
    "hgroup": [],
    "address": [],
    "search": [],
    "div": [],
    "span": [],
    "details": ["open"],
    "summary": [],
    "map": ["name"],
    "area": ["href", "alt", "shape", "coords", "target"],
    "bdi": [],
    "bdo": [],
    "ruby": [],
    "rp": [],
    "rt": [],
}

# 'permissive' allowed tags is identical to 'styled' but without '<style>' tag
ALLOWED_TAGS_PERMISSIVE: Dict[str, List[str]] = {
    k: v for k, v in ALLOWED_TAGS_STYLED.items() if k != "style"
}

# 'standard' allowed tags
ALLOWED_TAGS_STANDARD: Dict[str, List[str]] = {
    "html": ["lang"],
    "head": [],
    "meta": ["charset", "name", "content"],
    "title": [],
    "body": [],
    "p": [],
    "blockquote": ["cite"],
    "hr": [],
    "figure": [],
    "figcaption": [],
    "a": ["href", "title", "target"],
    "strong": [],
    "em": [],
    "b": [],
    "i": [],
    "s": [],
    "u": [],
    "br": [],
    "h1": [], "h2": [], "h3": [], "h4": [], "h5": [], "h6": [],
    "img": ["src", "alt", "width", "height", "loading"],
    "picture": [],
    "source": ["srcset", "sizes", "media", "type", "src"],
    "video": ["src", "width", "height", "poster", "controls", "preload"],
    "audio": ["src", "controls", "preload"],
    "table": [],
    "caption": [],
    "thead": [],
    "tbody": [],
    "tfoot": [],
    "tr": [],
    "th": ["colspan", "rowspan"],
    "td": ["colspan", "rowspan"],
    "col": ["span"],
    "colgroup": ["span"],
    "code": [],
    "pre": [],
    "ul": [],
    "ol": ["start", "type", "reversed"],
    "li": [],
    "dl": [],
    "dt": [],
    "dd": [],
    "abbr": ["title"],
    "cite": [],
    "dfn": [],
    "kbd": [],
    "samp": [],
    "var": [],
    "mark": [],
    "small": [],
    "q": [],
    "wbr": [],
    "del": ["datetime", "cite"],
    "ins": ["datetime", "cite"],
    "sub": [],
    "sup": [],
    "time": ["datetime"],
}

# 'minimal' allowed tags
ALLOWED_TAGS_MINIMAL: Dict[str, List[str]] = {
    "html": ["lang"],
    "head": [],
    "meta": ["charset", "name", "content"],
    "title": [],
    "body": [],
    "p": [],
    "a": ["href"],
    "strong": [],
    "em": [],
    "b": [],
    "i": [],
    "s": [],
    "br": [],
    "h1": [], "h2": [], "h3": [], "h4": [], "h5": [], "h6": [],
    "table": [],
    "thead": [],
    "tbody": [],
    "tr": [],
    "th": ["colspan", "rowspan"],
    "td": ["colspan", "rowspan"],
    "code": [],
    "pre": [],
    "ul": [],
    "ol": [],
    "li": [],
    "del": [],
    "abbr": ["title"],
}


class CleanerService:
    """
    Service responsible for cleaning HTML content based on clean levels.
    """

    def clean_html(self, request: CleanRequest) -> CleanResponse:
        source_type: Literal["raw_html", "url"] = "raw_html" if request.raw_html is not None else "url"
        url_used = request.url

        logger.info(
            "Starting HTML cleanup process. Source: %s, URL: %s, Level: %s",
            source_type,
            url_used,
            request.clean_level,
        )

        try:
            raw_html_content = self._get_html(request)

            cleaned_html = self._clean(raw_html_content, request.clean_level)

            logger.info("HTML cleanup completed successfully.")

            # Return raw html only if the request contained a URL
            response_raw_html = raw_html_content if source_type == "url" else None

            return self._success(
                data=cleaned_html,
                raw_html=response_raw_html,
                source=source_type,
                url=url_used,
            )

        except CleanError as e:
            logger.warning("HTML cleanup failed: %s", str(e))
            return self._failure(str(e), source_type, url_used)
        except Exception as e:
            logger.exception("Unexpected error during HTML cleanup")
            return self._failure(
                f"An unexpected error occurred: {str(e)}", source_type, url_used
            )

    def _source_factory(self, request: CleanRequest) -> HtmlSource:
        if request.raw_html is not None:
            return RawHtmlSource()
        elif request.url is not None:
            if request.downloader == "CloakBrowserSource":
                return CloakBrowserSource()
            return TrafilaturaUrlSource()
        else:
            raise CleanError("No URL or HTML content provided.")

    def _get_html(self, request: CleanRequest) -> str:
        try:
            source = self._source_factory(request)
            return source.get_html(request)
        except Exception as e:
            if not isinstance(e, CleanError):
                raise CleanError(f"Failed to retrieve HTML: {str(e)}") from e
            raise

    def _clean(self, html_content: str, clean_level: str) -> str:
        try:
            # Parse using BeautifulSoup with the lxml parser
            soup = BeautifulSoup(html_content, "lxml")

            # Perform tag replacements case-insensitively in a single pass
            for tag in list(soup.find_all()):
                tag_name_lower = tag.name.lower()
                if tag_name_lower in REPLACEMENTS:
                    tag.name = REPLACEMENTS[tag_name_lower]

            if clean_level != "correct_only":
                # Get the appropriate allowed tags dictionary
                if clean_level == "styled":
                    allowed_tags = ALLOWED_TAGS_STYLED
                elif clean_level == "permissive":
                    allowed_tags = ALLOWED_TAGS_PERMISSIVE
                elif clean_level == "standard":
                    allowed_tags = ALLOWED_TAGS_STANDARD
                elif clean_level == "minimal":
                    allowed_tags = ALLOWED_TAGS_MINIMAL
                else:
                    raise CleanError(f"Unsupported clean level: {clean_level}")

                # Determine whether we allow class/style attributes (only for 'styled' level)
                is_styled = clean_level == "styled"

                # Strip comments for cleaner output in standard/styled/permissive/minimal levels
                comments = list(soup.find_all(string=lambda text: isinstance(text, Comment) or text.__class__.__name__ == 'Comment'))
                for comment in comments:
                    comment.extract()

                # Process all tags in the parsed HTML tree
                for tag in list(soup.find_all()):
                    if tag.parent is None:
                        # Already removed/decomposed
                        continue

                    tag_name_lower = tag.name.lower()
                    if tag_name_lower not in allowed_tags:
                        # Check if we should decompose or unwrap
                        if tag_name_lower in DECOMPOSE_TAGS or tag_name_lower.endswith((':script', ':style')):
                            tag.decompose()
                        else:
                            tag.unwrap()
                    else:
                        # Normalize tag name to lowercase
                        tag.name = tag_name_lower

                        # Filter attributes for allowed tags
                        allowed_attrs = allowed_tags[tag_name_lower]
                        if is_styled:
                            allowed_attrs = allowed_attrs + ["class", "style"]

                        # Delete unallowed attributes
                        attrs_to_remove = [
                            attr for attr in tag.attrs if attr not in allowed_attrs
                        ]
                        for attr in attrs_to_remove:
                            del tag.attrs[attr]

            # Reformat HTML using prettify() to ensure proper indents and line breaks
            formatted_html = soup.prettify()
            return formatted_html

        except Exception as e:
            logger.exception("Error processing HTML cleanup with BeautifulSoup")
            raise CleanError(f"BeautifulSoup parsing/cleanup failed: {str(e)}") from e

    @staticmethod
    def _success(
        data: str, raw_html: Optional[str], source: str, url: Optional[str]
    ) -> CleanResponse:
        return CleanResponse(
            success=True,
            data=data,
            raw_html=raw_html,
            source=source,
            url=url,
        )

    @staticmethod
    def _failure(message: str, source: str, url: Optional[str]) -> CleanResponse:
        return CleanResponse(
            success=False,
            error=message,
            source=source,
            url=url,
        )
