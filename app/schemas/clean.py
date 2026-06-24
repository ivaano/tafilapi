from typing import Optional, Literal
from pydantic import BaseModel, Field, model_validator

CleanLevel = Literal["correct_only", "styled", "permissive", "standard", "minimal"]
_DEFAULT_CLEAN_LEVEL: CleanLevel = "standard"
Downloader = Literal["TrafilaturaUrlSource", "CloakBrowserSource"]
_DEFAULT_DOWNLOADER: Downloader = "TrafilaturaUrlSource"

class CleanRequest(BaseModel):
    url: Optional[str] = Field(
        None, description="The URL of the webpage to fetch and clean HTML from."
    )
    raw_html: Optional[str] = Field(
        None, description="The raw HTML string to clean."
    )
    clean_level: CleanLevel = Field(
        default=_DEFAULT_CLEAN_LEVEL,
        description="The clean level defining which tags/attributes to retain.",
    )
    downloader: Downloader = Field(
        default=_DEFAULT_DOWNLOADER,
        description="The downloader to use when a URL is provided.",
    )

    @model_validator(mode="after")
    def validate_inputs(self) -> "CleanRequest":
        if not self.url and not self.raw_html:
            raise ValueError("Either 'url' or 'raw_html' must be provided.")
        if self.url and not (
            self.url.startswith("http://") or self.url.startswith("https://")
        ):
            raise ValueError("URL must start with http:// or https://")
        return self


class CleanResponse(BaseModel):
    success: bool = Field(
        ..., description="Indicates whether the HTML cleanup was successful."
    )
    data: Optional[str] = Field(
        None, description="The cleaned and reformatted HTML content."
    )
    raw_html: Optional[str] = Field(
        None, description="The raw HTML fetched from the URL, if applicable."
    )
    source: Literal["raw_html", "url"] = Field(
        ..., description="The source that was processed ('raw_html' or 'url')."
    )
    url: Optional[str] = Field(
        None, description="The URL that was processed, if applicable."
    )
    error: Optional[str] = Field(
        None, description="Error message if the HTML cleanup failed."
    )
