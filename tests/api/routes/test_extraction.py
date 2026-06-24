from unittest.mock import patch, ANY


def test_extract_unauthorized_missing_token(client):
    """
    Test that calling /extract without token returns 401 Unauthorized.
    """
    response = client.post("/extract", json={"raw_html": "<p>test</p>"})
    assert response.status_code == 401
    assert "Missing authentication token" in response.json()["detail"]


def test_extract_unauthorized_invalid_token(client):
    """
    Test that calling /extract with an invalid token returns 401 Unauthorized.
    """
    headers = {"Authorization": "Bearer invalid-token-123"}
    response = client.post(
        "/extract", json={"raw_html": "<p>test</p>"}, headers=headers
    )
    assert response.status_code == 401
    assert "Invalid authentication token" in response.json()["detail"]


def test_extract_invalid_payload_both_missing(client, auth_headers):
    """
    Test that calling /extract without raw_html or url returns 422 validation error.
    """
    response = client.post("/extract", json={}, headers=auth_headers)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(
        "Either 'url' or 'raw_html' must be provided." in err["msg"] for err in errors
    )


def test_extract_invalid_payload_bad_url(client, auth_headers):
    """
    Test that calling /extract with a URL not starting with http/https returns 422 validation error.
    """
    response = client.post(
        "/extract", json={"url": "ftp://example.com"}, headers=auth_headers
    )
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(
        "URL must start with http:// or https://" in err["msg"] for err in errors
    )


def test_extract_success_raw_html(client, auth_headers):
    """
    Test successful HTML extraction via POST with raw_html.
    """
    html = "<html><body><h1>Sample Page</h1><p>Main readable text goes here.</p></body></html>"
    response = client.post("/extract", json={"raw_html": html}, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["source"] == "raw_html"
    assert "Main readable text goes here" in data["data"]


@patch("trafilatura.fetch_url")
def test_extract_success_url(mock_fetch, client, auth_headers):
    """
    Test successful HTML extraction via POST with url.
    """
    mock_fetch.return_value = (
        "<html><body><h1>Sample Page</h1><p>Fetched readable text.</p></body></html>"
    )
    response = client.post(
        "/extract",
        json={"url": "https://example.com/item"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["source"] == "url"
    assert data["url"] == "https://example.com/item"
    assert "Fetched readable text" in data["data"]
    mock_fetch.assert_called_once_with("https://example.com/item", config=ANY)


def test_extract_invalid_payload_cloakbrowser_no_url(client, auth_headers):
    """
    Test that calling /extract with cloakbrowser=True but no url returns 422 validation error.
    """
    response = client.post(
        "/extract",
        json={"cloakbrowser": True, "raw_html": "<html></html>"},
        headers=auth_headers,
    )
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(
        "'url' must be provided when 'cloakbrowser' is True." in err["msg"]
        for err in errors
    )


@patch("cloakbrowser.launch")
def test_extract_success_cloakbrowser(mock_launch, client, auth_headers):
    """
    Test successful HTML extraction via POST with url and cloakbrowser=True.
    """
    from unittest.mock import MagicMock

    mock_page = MagicMock()
    mock_page.content.return_value = "<html><body><h1>Stealth Page</h1><p>Fetched with CloakBrowser integration.</p></body></html>"

    mock_browser = MagicMock()
    mock_browser.new_page.return_value = mock_page
    mock_browser.__enter__.return_value = mock_browser

    mock_launch.return_value = mock_browser

    response = client.post(
        "/extract",
        json={"url": "https://example.com/stealth", "cloakbrowser": True},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["source"] == "url"
    assert data["url"] == "https://example.com/stealth"
    assert "Fetched with CloakBrowser integration" in data["data"]

    mock_launch.assert_called_once_with(humanize=True, headless=True)
    mock_page.goto.assert_called_once_with("https://example.com/stealth")
    mock_page.content.assert_called_once()


def test_extract_success_with_metadata(client, auth_headers):
    """
    Test successful metadata extraction via POST with with_metadata=True.
    """
    html = "<html><head><title>Integration Metadata Title</title></head><body><p>Unused.</p></body></html>"
    response = client.post(
        "/extract",
        json={"raw_html": html, "with_metadata": True},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["source"] == "raw_html"
    assert isinstance(data["data"], dict)
    assert data["data"]["title"] == "Integration Metadata Title"
