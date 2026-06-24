from unittest.mock import patch, MagicMock, ANY
from app.services.extractor import ExtractionService
from app.schemas.extraction import ExtractionRequest, DocumentMetadataResponse


def test_extract_content_raw_html():
    """
    Test successful extraction of content from a raw HTML string.
    """
    html = "<html><body><h1>Test Page</h1><p>This is a paragraph.</p></body></html>"
    req = ExtractionRequest(raw_html=html, output_format="txt")
    res = ExtractionService().extract_content(req)
    assert res.success is True
    assert res.source == "raw_html"
    assert res.data is not None
    assert "This is a paragraph" in res.data


@patch("trafilatura.fetch_url")
def test_extract_content_url_success(mock_fetch):
    """
    Test successful extraction from a URL when fetch_url returns HTML.
    """
    mock_fetch.return_value = (
        "<html><body><h1>Test Page</h1><p>Extracted from URL.</p></body></html>"
    )
    req = ExtractionRequest(url="https://example.com/test", output_format="txt")
    res = ExtractionService().extract_content(req)
    assert res.success is True
    assert res.source == "url"
    assert res.url == "https://example.com/test"
    assert res.data is not None
    assert "Extracted from URL" in res.data
    mock_fetch.assert_called_once_with("https://example.com/test", config=ANY)


@patch("trafilatura.fetch_url")
def test_extract_content_url_fetch_failure(mock_fetch):
    """
    Test failure handling when fetch_url returns None.
    """
    mock_fetch.return_value = None
    req = ExtractionRequest(url="https://example.com/fail", output_format="txt")
    res = ExtractionService().extract_content(req)
    assert res.success is False
    assert res.source == "url"
    assert "Failed to fetch HTML content" in res.error
    mock_fetch.assert_called_once_with("https://example.com/fail", config=ANY)


def test_extract_content_both_provided_prefers_raw_html():
    """
    Test that raw_html is processed and fetch_url is not called when bothurl and raw_html are provided.
    """
    html = "<html><body><h1>Raw HTML Page</h1><p>Should select this.</p></body></html>"
    req = ExtractionRequest(
        url="https://example.com/ignored", raw_html=html, output_format="txt"
    )
    with patch("trafilatura.fetch_url") as mock_fetch:
        res = ExtractionService().extract_content(req)
        assert res.success is True
        assert res.source == "raw_html"
        assert res.data is not None
        assert "Should select this" in res.data
        mock_fetch.assert_not_called()


def test_extract_content_unextractable_html():
    """
    Test response when HTML contains no extractable main text/content.
    """
    html = "<html><body></body></html>"
    req = ExtractionRequest(raw_html=html, output_format="txt")
    res = ExtractionService().extract_content(req)
    assert res.success is False
    assert "unable to extract meaningful content" in res.error


@patch("cloakbrowser.launch")
def test_extract_content_cloakbrowser_success(mock_launch):
    """
    Test successful extraction from a URL using cloakbrowser downloader.
    """
    mock_page = MagicMock()
    mock_page.content.return_value = "<html><body><h1>Stealth Page</h1><p>Fetched with CloakBrowser.</p></body></html>"

    mock_browser = MagicMock()
    mock_browser.new_page.return_value = mock_page
    mock_browser.__enter__.return_value = mock_browser

    mock_launch.return_value = mock_browser

    req = ExtractionRequest(
        url="https://example.com/stealth", cloakbrowser=True, output_format="txt"
    )
    res = ExtractionService().extract_content(req)

    assert res.success is True
    assert res.source == "url"
    assert res.url == "https://example.com/stealth"
    assert "Fetched with CloakBrowser" in res.data

    mock_launch.assert_called_once_with(humanize=True, headless=True)
    mock_page.goto.assert_called_once_with("https://example.com/stealth")
    mock_page.content.assert_called_once()


@patch("cloakbrowser.launch")
def test_extract_content_cloakbrowser_failure(mock_launch):
    """
    Test failure handling when cloakbrowser launch or navigate throws an error.
    """
    mock_launch.side_effect = Exception("Browser crashed")

    req = ExtractionRequest(
        url="https://example.com/stealth-fail",
        cloakbrowser=True,
        output_format="txt",
    )
    res = ExtractionService().extract_content(req)

    assert res.success is False
    assert res.source == "url"
    assert "Failed to fetch HTML content using cloakbrowser" in res.error
    assert "Browser crashed" in res.error


def test_extract_content_with_metadata_success():
    """
    Test successful metadata extraction from raw HTML.
    """
    html = "<html><head><title>My Metadata Test Page</title><meta name='description' content='Page description.'></head><body><p>Unused text.</p></body></html>"
    req = ExtractionRequest(raw_html=html, with_metadata=True)
    res = ExtractionService().extract_content(req)
    assert res.success is True
    assert res.source == "raw_html"
    assert isinstance(res.data, DocumentMetadataResponse)
    assert res.data.title == "My Metadata Test Page"
    assert res.data.description == "Page description."
