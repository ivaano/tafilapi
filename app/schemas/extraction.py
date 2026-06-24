from typing import Optional, Literal, Union
from pydantic import BaseModel, Field, model_validator

OutputFormat = Literal["csv", "html", "json", "markdown", "txt", "xml", "xmltei"]
_DEFAULT_FORMAT: OutputFormat = "txt"


class ExtractionRequest(BaseModel):
    url: Optional[str] = Field(
        None, description="The URL of the webpage to fetch and extract content from."
    )
    raw_html: Optional[str] = Field(
        None, description="The raw HTML string to extract content from."
    )
    output_format: OutputFormat = Field(
        default=_DEFAULT_FORMAT,
        description="Output format for the extracted content in text key.",
    )
    cloakbrowser: bool = Field(
        False,
        description="Use cloakbrowser instead of the internal trafilatura downloader to fetch HTML. Only works when url is set.",
    )
    with_metadata: bool = Field(
        False,
        description="Extract and return page metadata instead of parsed content.",
    )
    fast: bool = Field(
        False, description="Use faster heuristics and skip backup extraction."
    )
    favor_precision: bool = Field(
        False, description="Prefer less text but correct extraction."
    )
    favor_recall: bool = Field(False, description="When unsure, prefer more text.")
    include_comments: bool = Field(
        True, description="Extract comments along with the main text."
    )
    tei_validation: bool = Field(
        False,
        description="Validate the XML-TEI output with respect to the TEI standard.",
    )
    target_language: Optional[str] = Field(
        None,
        description="Define a language to discard invalid documents (ISO 639-1 format).",
    )
    include_tables: bool = Field(
        True,
        description="Take into account information within the HTML <table> element.",
    )
    include_images: bool = Field(
        False, description="Take images into account (experimental)."
    )
    include_formatting: bool = Field(
        False,
        description="Keep structural elements related to formatting (only valuable if output_format is set to XML).",
    )
    include_links: bool = Field(
        False, description="Keep links along with their targets (experimental)."
    )
    deduplicate: bool = Field(
        False, description="Remove duplicate segments and documents."
    )
    date_extraction_params: Optional[dict] = Field(
        None, description="Provide extraction parameters to htmldate as dict()."
    )
    url_blacklist: Optional[set[str]] = Field(
        None,
        description="Provide a blacklist of URLs as set() to filter out documents.",
    )
    author_blacklist: Optional[set[str]] = Field(
        None,
        description="Provide a blacklist of Author Names as set() to filter out authors.",
    )
    prune_xpath: Optional[Union[str, list[str]]] = Field(
        None,
        description="Provide an XPath expression to prune the tree before extraction. Can be str or list of str.",
    )

    @model_validator(mode="after")
    def validate_inputs(self) -> "ExtractionRequest":
        if not self.url and not self.raw_html:
            raise ValueError("Either 'url' or 'raw_html' must be provided.")
        if self.url and not (
            self.url.startswith("http://") or self.url.startswith("https://")
        ):
            raise ValueError("URL must start with http:// or https://")
        if self.cloakbrowser and not self.url:
            raise ValueError("'url' must be provided when 'cloakbrowser' is True.")
        return self


class DocumentMetadataResponse(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    url: Optional[str] = None
    hostname: Optional[str] = None
    description: Optional[str] = None
    sitename: Optional[str] = None
    date: Optional[str] = None
    categories: Optional[list[str]] = None
    tags: Optional[list[str]] = None
    fingerprint: Optional[str] = None
    id: Optional[str] = None
    license: Optional[str] = None
    body: Optional[str] = None
    comments: Optional[str] = None
    commentsbody: Optional[str] = None
    raw_text: Optional[str] = None
    text: Optional[str] = None
    language: Optional[str] = None
    image: Optional[str] = None
    pagetype: Optional[str] = None
    filedate: Optional[str] = None


class ExtractionResponse(BaseModel):
    success: bool = Field(
        ..., description="Indicates whether the extraction was successful."
    )
    data: Optional[Union[str, DocumentMetadataResponse]] = Field(
        None,
        description="The extracted content (either plain text or metadata object).",
    )
    source: Literal["raw_html", "url"] = Field(
        ..., description="The source that was processed ('raw_html' or 'url')."
    )
    url: Optional[str] = Field(
        None, description="The URL that was processed, if applicable."
    )
    error: Optional[str] = Field(
        None, description="Error message if the extraction failed."
    )
