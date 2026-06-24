from unittest.mock import patch, MagicMock


@patch("trafilatura.extract")
def test_extract_endpoint_receives_all_parameters(mock_extract, client, auth_headers):
    """
    Test that the POST /extract endpoint successfully validates the new request body structure
    and forwards all fields to the extraction service.
    """
    mock_extract.return_value = "<TEI>Parsed document</TEI>"

    payload = {
        "raw_html": "<html><body><p>Test content</p></body></html>",
        "output_format": "xmltei",
        "fast": True,
        "favor_precision": True,
        "favor_recall": True,
        "include_comments": False,
        "tei_validation": True,
        "target_language": "de",
        "include_tables": False,
        "include_images": True,
        "include_formatting": True,
        "include_links": True,
        "deduplicate": True,
        "date_extraction_params": {"some_param": 123},
        "url_blacklist": ["https://spam-site.com", "https://bad-site.org"],
        "author_blacklist": ["Author A", "Author B"],
        "prune_xpath": "//div[@class='ad']",
        "url": "https://example.com/german-article",
    }

    response = client.post("/extract", json=payload, headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"] == "<TEI>Parsed document</TEI>"

    # Verify parameters received in mock_extract
    mock_extract.assert_called_once()
    called_kwargs = mock_extract.call_args[1]

    assert called_kwargs["output_format"] == "xmltei"
    assert called_kwargs["fast"] is True
    assert called_kwargs["favor_precision"] is True
    assert called_kwargs["favor_recall"] is True
    assert called_kwargs["include_comments"] is False
    assert called_kwargs["tei_validation"] is True
    assert called_kwargs["target_language"] == "de"
    assert called_kwargs["include_tables"] is False
    assert called_kwargs["include_images"] is True
    assert called_kwargs["include_formatting"] is True
    assert called_kwargs["include_links"] is True
    assert called_kwargs["deduplicate"] is True
    assert called_kwargs["date_extraction_params"] == {"some_param": 123}
    assert called_kwargs["url_blacklist"] == {
        "https://spam-site.com",
        "https://bad-site.org",
    }
    assert called_kwargs["author_blacklist"] == {"Author A", "Author B"}
    assert called_kwargs["prune_xpath"] == "//div[@class='ad']"
    assert called_kwargs["url"] == "https://example.com/german-article"


@patch("trafilatura.extract_with_metadata")
def test_extract_metadata_endpoint_receives_all_parameters(
    mock_extract_metadata, client, auth_headers
):
    """
    Test that the POST /extract endpoint with with_metadata=True successfully validates and forwards all parameters.
    """
    mock_doc = MagicMock()
    mock_doc.__slots__ = ["title", "author"]
    mock_doc.title = "German Article"
    mock_doc.author = "Author A"
    mock_extract_metadata.return_value = mock_doc

    payload = {
        "raw_html": "<html><body><p>Test content</p></body></html>",
        "with_metadata": True,
        "output_format": "json",
        "fast": True,
        "favor_precision": True,
        "favor_recall": True,
        "include_comments": False,
        "tei_validation": True,
        "target_language": "de",
        "include_tables": False,
        "include_images": True,
        "include_formatting": True,
        "include_links": True,
        "deduplicate": True,
        "date_extraction_params": {"some_param": 123},
        "url_blacklist": ["https://spam-site.com"],
        "author_blacklist": ["Author A"],
        "prune_xpath": ["//div", "//span"],
        "url": "https://example.com/german-article",
    }

    response = client.post("/extract", json=payload, headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["title"] == "German Article"
    assert response.json()["data"]["author"] == "Author A"

    # Verify parameters received in mock_extract_metadata
    mock_extract_metadata.assert_called_once()
    called_kwargs = mock_extract_metadata.call_args[1]

    assert called_kwargs["output_format"] == "json"
    assert called_kwargs["fast"] is True
    assert called_kwargs["favor_precision"] is True
    assert called_kwargs["favor_recall"] is True
    assert called_kwargs["include_comments"] is False
    assert called_kwargs["tei_validation"] is True
    assert called_kwargs["target_language"] == "de"
    assert called_kwargs["include_tables"] is False
    assert called_kwargs["include_images"] is True
    assert called_kwargs["include_formatting"] is True
    assert called_kwargs["include_links"] is True
    assert called_kwargs["deduplicate"] is True
    assert called_kwargs["date_extraction_params"] == {"some_param": 123}
    assert called_kwargs["url_blacklist"] == {"https://spam-site.com"}
    assert called_kwargs["author_blacklist"] == {"Author A"}
    assert called_kwargs["prune_xpath"] == ["//div", "//span"]
    assert called_kwargs["url"] == "https://example.com/german-article"
