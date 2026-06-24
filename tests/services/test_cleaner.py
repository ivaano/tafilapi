from unittest.mock import patch, MagicMock
import pytest
from app.schemas.clean import CleanRequest
from app.services.cleaner import CleanerService
from app.services.exceptions import CleanError


def test_clean_correct_only():
    """
    Test correct_only level: fixes malformed HTML, does tag replacements, preserves all tags/attributes.
    """
    raw = "<html><body><strike>strike content</strike> <tt>tt content</tt> <acronym>acronym</acronym> <dir><li>item</li></dir> <listing>listing content</listing> <xmp>xmp content</xmp> <plaintext>plaintext content"
    
    req = CleanRequest(raw_html=raw, clean_level="correct_only")
    res = CleanerService().clean_html(req)

    assert res.success is True
    assert res.source == "raw_html"
    assert res.url is None
    assert res.raw_html is None

    # Check replacements
    assert "<del>\n   strike content\n  </del>" in res.data
    assert "<code>\n   tt content\n  </code>" in res.data
    assert "<abbr>\n   acronym\n  </abbr>" in res.data
    assert "<ul>\n   <li>\n    item\n   </li>\n  </ul>" in res.data
    assert "<pre>listing content</pre>" in res.data
    assert "<pre>xmp content</pre>" in res.data
    assert "<pre>plaintext content</pre>" in res.data


def test_clean_minimal():
    """
    Test minimal level: only headings, tables, lists, code, b/i/s/del, p, and a[href], abbr[title] allowed.
    """
    raw = """
    <html>
        <head><title>Test</title></head>
        <body>
            <div class="header"><h1>Header</h1></div>
            <span style="color:red"><p>Paragraph with <a href="http://link" title="ignored title">link</a></p></span>
            <article>
                <p><strong>Strong</strong> <em>Em</em> <b>B</b> <i>I</i> <s>S</s> <u>U (stripped)</u></p>
                <img src="img.jpg" alt="image" />
            </article>
        </body>
    </html>
    """
    req = CleanRequest(raw_html=raw, clean_level="minimal")
    res = CleanerService().clean_html(req)

    assert res.success is True
    # div, span, article, img should be removed/unwrapped
    assert "<div" not in res.data
    assert "<span" not in res.data
    assert "<article" not in res.data
    assert "<img" not in res.data
    assert "<u>" not in res.data  # <u> is not allowed, should be unwrapped to its text

    # paragraph and heading should exist
    assert "<h1>\n   Header\n  </h1>" in res.data
    # a href title: title should be stripped
    assert '<a href="http://link">' in res.data
    assert 'title="ignored title"' not in res.data
    assert "<strong>\n    Strong\n   </strong>" in res.data
    assert "U (stripped)" in res.data  # text preserved


def test_clean_standard():
    """
    Test standard level: includes images, audio/video, table, ol[start/type/reversed], del[datetime/cite], but strips divs/spans/article.
    """
    raw = """
    <html>
        <body>
            <div class="container">
                <article>
                    <p>Some text</p>
                    <img src="image.png" alt="img" class="stripped-class" />
                    <span class="bad-span">Span text</span>
                </article>
            </div>
        </body>
    </html>
    """
    req = CleanRequest(raw_html=raw, clean_level="standard")
    res = CleanerService().clean_html(req)

    assert res.success is True
    assert "<div" not in res.data
    assert "<article" not in res.data
    assert "<span" not in res.data
    assert '<img alt="img" src="image.png"/>' in res.data


def test_clean_styled():
    """
    Test styled level: allows <style> tag, and class/style attributes on all tags.
    """
    raw = """
    <html>
        <head>
            <style>body { color: blue; }</style>
        </head>
        <body>
            <div class="my-class" style="margin: 10px;">
                <p class="para">Styled content</p>
            </div>
            <script>alert('bad');</script>
        </body>
    </html>
    """
    req = CleanRequest(raw_html=raw, clean_level="styled")
    res = CleanerService().clean_html(req)

    assert res.success is True
    # style tag should be preserved
    assert "<style>\n   body { color: blue; }\n  </style>" in res.data
    # my-class, para class, style="margin: 10px;" should be preserved
    assert '<div class="my-class" style="margin: 10px;">' in res.data
    assert '<p class="para">' in res.data
    # script tag should be decomposed (completely removed)
    assert "alert" not in res.data


def test_clean_permissive():
    """
    Test permissive level: structural HTML5, details/summary, divs/spans, but no style tag or class/style attributes.
    """
    raw = """
    <html>
        <head>
            <style>body { color: blue; }</style>
        </head>
        <body>
            <div class="my-class" style="margin: 10px;">
                <details open="open"><summary>Summary</summary>Details</details>
            </div>
        </body>
    </html>
    """
    req = CleanRequest(raw_html=raw, clean_level="permissive")
    res = CleanerService().clean_html(req)

    assert res.success is True
    # style tag must be decomposed/removed
    assert "<style>" not in res.data
    # div, details, summary allowed, but class/style attributes stripped
    assert "<div>" in res.data.replace(" ", "").replace("\n", "")
    assert '<detailsopen="open">' in res.data.replace(" ", "").replace("\n", "")


@patch("app.services.downloaders.TrafilaturaUrlSource.get_html")
def test_clean_url_trafilatura_success(mock_get_html):
    """
    Test successful URL cleanup using TrafilaturaUrlSource (default).
    """
    mock_get_html.return_value = "<html><body><h1>URL Title</h1></body></html>"

    req = CleanRequest(url="https://example.com/test", clean_level="standard")
    res = CleanerService().clean_html(req)

    assert res.success is True
    assert res.source == "url"
    assert res.url == "https://example.com/test"
    # Must include raw_html if request contained a URL
    assert res.raw_html == "<html><body><h1>URL Title</h1></body></html>"
    assert "<h1>\n   URL Title\n  </h1>" in res.data
    mock_get_html.assert_called_once_with(req)


@patch("app.services.downloaders.CloakBrowserSource.get_html")
def test_clean_url_cloakbrowser_success(mock_get_html):
    """
    Test successful URL cleanup using CloakBrowserSource.
    """
    mock_get_html.return_value = "<html><body><h1>Stealth Title</h1></body></html>"

    req = CleanRequest(
        url="https://example.com/stealth",
        downloader="CloakBrowserSource",
        clean_level="standard",
    )
    res = CleanerService().clean_html(req)

    assert res.success is True
    assert res.source == "url"
    assert res.url == "https://example.com/stealth"
    assert res.raw_html == "<html><body><h1>Stealth Title</h1></body></html>"
    assert "<h1>\n   Stealth Title\n  </h1>" in res.data
    mock_get_html.assert_called_once_with(req)


@patch("app.services.downloaders.TrafilaturaUrlSource.get_html")
def test_clean_url_failure(mock_get_html):
    """
    Test failure handling during URL cleanup when fetch throws exception.
    """
    mock_get_html.side_effect = Exception("Network down")

    req = CleanRequest(url="https://example.com/fail", clean_level="standard")
    res = CleanerService().clean_html(req)

    assert res.success is False
    assert "Network down" in res.error
    assert res.data is None
    assert res.raw_html is None


def test_clean_minimal_case_insensitivity_and_comments():
    """
    Test minimal clean level with uppercase tags (SCRIPT, STYLE), comments, and verify they are correctly stripped/decomposed.
    """
    raw = """
    <HTML>
        <HEAD>
            <TITLE>Title</TITLE>
            <STYLE>body { font-family: sans-serif; }</STYLE>
            <SCRIPT>console.log("head script");</SCRIPT>
        </HEAD>
        <BODY>
            <!-- A test comment -->
            <DIV class="container">
                <H1>Heading</H1>
                <P>Paragraph <SCRIPT>console.log("inline script");</SCRIPT></P>
            </DIV>
        </BODY>
    </HTML>
    """
    req = CleanRequest(raw_html=raw, clean_level="minimal")
    res = CleanerService().clean_html(req)

    assert res.success is True
    # The output tag names must be lowercase
    assert "<html>" in res.data
    assert "<head>" in res.data
    assert "<body>" in res.data
    assert "<h1>\n   Heading\n  </h1>" in res.data
    # Comments, script, style must be completely removed (decomposed/extracted)
    assert "A test comment" not in res.data
    assert "console.log" not in res.data
    assert "font-family" not in res.data
    assert "style" not in res.data.lower()
    assert "script" not in res.data.lower()
    assert "div" not in res.data.lower()

