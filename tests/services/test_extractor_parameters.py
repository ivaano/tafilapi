from unittest.mock import patch, MagicMock
from app.services.extractor import ExtractionService
from app.schemas.extraction import ExtractionRequest, DocumentMetadataResponse


@patch("trafilatura.extract")
def test_extract_content_parameters_forwarding(mock_extract):
    """
    Verify that all optional parameters in ExtractionRequest are correctly passed to trafilatura.extract.
    """
    mock_extract.return_value = "Extracted Text"

    req = ExtractionRequest(
        raw_html="<html><body><p>Hello World</p></body></html>",
        output_format="xmltei",
        fast=True,
        favor_precision=True,
        favor_recall=True,
        include_comments=False,
        tei_validation=True,
        target_language="en",
        include_tables=False,
        include_images=True,
        include_formatting=True,
        include_links=True,
        deduplicate=True,
        date_extraction_params={"custom": "param"},
        url_blacklist={"http://spam.com"},
        author_blacklist={"John Doe"},
        prune_xpath="//div[@id='ads']",
        url="https://example.com",
    )

    res = ExtractionService().extract_content(req)

    assert res.success is True
    assert res.data == "Extracted Text"

    mock_extract.assert_called_once_with(
        "<html><body><p>Hello World</p></body></html>",
        output_format="xmltei",
        fast=True,
        favor_precision=True,
        favor_recall=True,
        include_comments=False,
        tei_validation=True,
        target_language="en",
        include_tables=False,
        include_images=True,
        include_formatting=True,
        include_links=True,
        deduplicate=True,
        date_extraction_params={"custom": "param"},
        url_blacklist={"http://spam.com"},
        author_blacklist={"John Doe"},
        prune_xpath="//div[@id='ads']",
        url="https://example.com",
    )


@patch("trafilatura.extract_with_metadata")
def test_extract_with_metadata_parameters_forwarding(mock_extract_metadata):
    """
    Verify that all optional parameters in ExtractionRequest are correctly passed to trafilatura.extract_with_metadata.
    """
    mock_doc = MagicMock()
    mock_doc.__slots__ = ["title"]
    mock_doc.title = "Mock Title"
    mock_extract_metadata.return_value = mock_doc

    req = ExtractionRequest(
        raw_html="<html><body><p>Hello World</p></body></html>",
        with_metadata=True,
        output_format="json",
        fast=True,
        favor_precision=True,
        favor_recall=True,
        include_comments=False,
        tei_validation=True,
        target_language="fr",
        include_tables=False,
        include_images=True,
        include_formatting=True,
        include_links=True,
        deduplicate=True,
        date_extraction_params={"custom": "param"},
        url_blacklist={"http://blacklist.com"},
        author_blacklist={"Jane Doe"},
        prune_xpath=["//div", "//span"],
        url="https://example.com/meta",
    )

    res = ExtractionService().extract_content(req)

    assert res.success is True
    assert isinstance(res.data, DocumentMetadataResponse)
    assert res.data.title == "Mock Title"

    mock_extract_metadata.assert_called_once_with(
        "<html><body><p>Hello World</p></body></html>",
        output_format="json",
        fast=True,
        favor_precision=True,
        favor_recall=True,
        include_comments=False,
        tei_validation=True,
        target_language="fr",
        include_tables=False,
        include_images=True,
        include_formatting=True,
        include_links=True,
        deduplicate=True,
        date_extraction_params={"custom": "param"},
        url_blacklist={"http://blacklist.com"},
        author_blacklist={"Jane Doe"},
        prune_xpath=["//div", "//span"],
        url="https://example.com/meta",
    )
