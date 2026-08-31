from fastapi.testclient import TestClient

from net_tools_app.main import app


def test_search_restun_relevant_results() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/search",
            json={
                "query": "How do I troubleshoot firewall connectivity",
                "top_k": 5,
            }
        )

        assert response.status_code == 200

        body = response.json()

        assert "results" in body
        assert len(body["results"]) == 5

        for result in body["results"]:
            assert result["content"]
            assert result["source"]
            assert isinstance(result["chunk_index"], int)
            assert isinstance(result["metadata"], dict)

