from unittest.mock import patch


def test_clean_unauthorized_missing_token(client):
    """
    Test that calling /clean without token returns 401 Unauthorized.
    """
    response = client.post("/clean", json={"raw_html": "<p>test</p>"})
    assert response.status_code == 401
    assert "Missing authentication token" in response.json()["detail"]


def test_clean_unauthorized_invalid_token(client):
    """
    Test that calling /clean with an invalid token returns 401 Unauthorized.
    """
    headers = {"Authorization": "Bearer invalid-token-123"}
    response = client.post(
        "/clean", json={"raw_html": "<p>test</p>"}, headers=headers
    )
    assert response.status_code == 401
    assert "Invalid authentication token" in response.json()["detail"]


def test_clean_invalid_payload_both_missing(client, auth_headers):
    """
    Test that calling /clean without raw_html or url returns 422 validation error.
    """
    response = client.post("/clean", json={}, headers=auth_headers)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(
        "Either 'url' or 'raw_html' must be provided." in err["msg"] for err in errors
    )


def test_clean_invalid_payload_bad_url(client, auth_headers):
    """
    Test that calling /clean with a URL not starting with http/https returns 422 validation error.
    """
    response = client.post(
        "/clean", json={"url": "ftp://example.com"}, headers=auth_headers
    )
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(
        "URL must start with http:// or https://" in err["msg"] for err in errors
    )


def test_clean_success_raw_html(client, auth_headers):
    """
    Test successful HTML cleanup via POST with raw_html.
    """
    html = "<html><body><strike>strike content</strike><p>Text</p></body></html>"
    response = client.post(
        "/clean",
        json={"raw_html": html, "clean_level": "standard"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["source"] == "raw_html"
    assert data["url"] is None
    assert data["raw_html"] is None
    assert "<del>\n   strike content\n  </del>" in data["data"]
    assert "<p>\n   Text\n  </p>" in data["data"]


@patch("app.services.downloaders.TrafilaturaUrlSource.get_html")
def test_clean_success_url_trafilatura(mock_get_html, client, auth_headers):
    """
    Test successful HTML cleanup via POST with url using TrafilaturaUrlSource.
    """
    mock_get_html.return_value = "<html><body><h1>Page Title</h1></body></html>"

    response = client.post(
        "/clean",
        json={
            "url": "https://example.com/clean-url",
            "downloader": "TrafilaturaUrlSource",
            "clean_level": "standard",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["source"] == "url"
    assert data["url"] == "https://example.com/clean-url"
    assert data["raw_html"] == "<html><body><h1>Page Title</h1></body></html>"
    assert "<h1>\n   Page Title\n  </h1>" in data["data"]
    mock_get_html.assert_called_once()


@patch("app.services.downloaders.CloakBrowserSource.get_html")
def test_clean_success_url_cloakbrowser(mock_get_html, client, auth_headers):
    """
    Test successful HTML cleanup via POST with url using CloakBrowserSource.
    """
    mock_get_html.return_value = "<html><body><h1>Cloaked Title</h1></body></html>"

    response = client.post(
        "/clean",
        json={
            "url": "https://example.com/stealth-url",
            "downloader": "CloakBrowserSource",
            "clean_level": "standard",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["source"] == "url"
    assert data["url"] == "https://example.com/stealth-url"
    assert data["raw_html"] == "<html><body><h1>Cloaked Title</h1></body></html>"
    assert "<h1>\n   Cloaked Title\n  </h1>" in data["data"]
    mock_get_html.assert_called_once()


@patch("app.services.downloaders.TrafilaturaUrlSource.get_html")
def test_clean_failure_url_fetch(mock_get_html, client, auth_headers):
    """
    Test API response when HTML fetch fails.
    """
    mock_get_html.side_effect = Exception("Connection timeout")

    response = client.post(
        "/clean",
        json={"url": "https://example.com/fail-fetch", "clean_level": "standard"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "Connection timeout" in data["error"]
    assert data["data"] is None
    assert data["raw_html"] is None
