def test_health_check_success(client):
    """
    Test that the /health endpoint is public, returns 200 OK,
    and performs the extraction self-test successfully.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "extraction self-test succeeded" in data["message"]
