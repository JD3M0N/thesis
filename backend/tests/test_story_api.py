from fastapi.testclient import TestClient

from .fakes import build_story_request
from .support import register_user, wait_for_story_completion


def test_generate_story_and_read_it(client: TestClient) -> None:
    register_user(client, "writer@example.com")

    response = client.post("/stories/generate", json=build_story_request())
    assert response.status_code == 202
    story_id = response.json()["id"]

    final_story = wait_for_story_completion(client, story_id)
    assert final_story["status"] == "completed"
    assert "Ayla" in final_story["story_text"]

    list_response = client.get("/stories")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    detail_response = client.get(f"/stories/{story_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == story_id
    assert detail_response.json()["status"] == "completed"


def test_story_routes_are_isolated_per_user(client: TestClient) -> None:
    register_user(client, "writer@example.com")

    creation = client.post("/stories/generate", json=build_story_request())
    assert creation.status_code == 202
    story_id = creation.json()["id"]
    final_story = wait_for_story_completion(client, story_id)
    assert final_story["status"] == "completed"

    client.post("/auth/logout")
    register_user(client, "other@example.com")

    empty_list = client.get("/stories")
    assert empty_list.status_code == 200
    assert empty_list.json() == []

    missing_detail = client.get(f"/stories/{story_id}")
    assert missing_detail.status_code == 404
    assert missing_detail.json()["detail"] == "Story not found"


def test_generate_story_requires_authentication(client: TestClient) -> None:
    response = client.post("/stories/generate", json=build_story_request())
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
