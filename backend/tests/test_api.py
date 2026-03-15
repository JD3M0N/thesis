from pathlib import Path
import time

from fastapi.testclient import TestClient
import httpx
from sqlmodel import Session, select

from app.config import Settings
from app.main import create_app
from app.models import Story, StoryAgentRun
from app.services.gemini import GeminiClient, GeminiRateLimitError


class FakeGeminiClient:
    def __init__(self, fail_on: str | None = None, inconsistent_dependency: bool = False) -> None:
        self.fail_on = fail_on
        self.inconsistent_dependency = inconsistent_dependency

    async def generate_json(self, prompt: str) -> dict:
        if self.fail_on and self.fail_on in prompt:
            raise RuntimeError("Synthetic agent failure")

        if "The Architect" in prompt:
            return {
                "premise": "Una aprendiz encuentra un reloj que abre grietas temporales.",
                "beats": [
                    {
                        "title": "La llamada",
                        "purpose": "Introducir el artefacto y la mision",
                        "stakes": "El tiempo local empieza a deshacerse",
                    }
                ],
                "climax": "La protagonista decide romper el reloj para salvar a su mentora.",
                "resolution": "La ciudad sobrevive pero ella pierde el ultimo recuerdo de su padre.",
            }
        if "The World Builder" in prompt:
            return {
                "characters": [
                    {
                        "name": "Ayla",
                        "role": "aprendiz",
                        "description": "Joven precisa y obsesionada con el orden",
                        "desire": "Salvar la ciudad",
                        "fear": "Repetir el fracaso de su padre",
                    }
                ],
                "locations": [
                    {
                        "name": "Archivo del Reloj",
                        "description": "Una torre silenciosa con mecanismos y polvo brillante",
                        "mood": "solemne",
                    }
                ],
                "objects": [
                    {"name": "Reloj umbral", "significance": "Abre fisuras entre momentos cercanos"}
                ],
                "rules": ["Cada uso del reloj borra un recuerdo humano."],
            }
        if "The Drama Coach" in prompt:
            return {
                "revised_beats": [
                    {
                        "title": "Traicion del mentor",
                        "purpose": "Subir el conflicto emocional",
                        "stakes": "Ayla duda de su mision",
                    }
                ],
                "tension_notes": ["La mentora intenta quedarse con el reloj."],
                "character_arc_notes": ["Ayla aprende a aceptar la perdida."],
            }
        if "The Dependency Manager" in prompt:
            if self.inconsistent_dependency:
                return {
                    "is_consistent": False,
                    "issues": ["El objeto crucial desaparece antes del climax."],
                    "fixes_applied": [],
                    "narrator_guidance": ["No narrar hasta resolver la contradiccion."],
                }
            return {
                "is_consistent": True,
                "issues": [],
                "fixes_applied": ["Se mantiene la regla de perdida de memoria."],
                "narrator_guidance": ["Mantener tono melancolico y preciso."],
            }
        if "The Narrator" in prompt:
            return {
                "title": "El reloj de la torre muda",
                "summary": "Ayla intenta salvar su ciudad mientras cada uso del reloj le cuesta un recuerdo.",
                "story_text": "Ayla subio la torre al anochecer y descubrio que el tiempo tambien podia sangrar.",
            }
        raise AssertionError("Prompt desconocido")


def create_test_client(
    tmp_path: Path,
    fail_on: str | None = None,
    inconsistent_dependency: bool = False,
) -> TestClient:
    settings = Settings(
        database_url=f"sqlite:///{tmp_path / 'test.db'}",
        jwt_secret="test-secret-with-at-least-thirty-two-characters",
        frontend_origin="http://localhost:3000",
    )
    app = create_app(
        settings=settings,
        llm_client=FakeGeminiClient(
            fail_on=fail_on,
            inconsistent_dependency=inconsistent_dependency,
        ),
    )
    return TestClient(app)


def register_user(client: TestClient, email: str) -> None:
    response = client.post(
        "/auth/register",
        json={"email": email, "password": "supersecure123"},
    )
    assert response.status_code == 201


def wait_for_story_completion(client: TestClient, story_id: str) -> dict:
    for _ in range(30):
        response = client.get(f"/stories/{story_id}")
        assert response.status_code == 200
        payload = response.json()
        if payload["status"] in {"completed", "failed"}:
            return payload
        time.sleep(0.05)
    raise AssertionError("Story generation did not finish in time")


def test_register_and_generate_story(tmp_path: Path) -> None:
    with create_test_client(tmp_path) as client:
        register_user(client, "writer@example.com")

        response = client.post(
            "/stories/generate",
            json={
                "characters": [
                    {
                        "name": "Ayla",
                        "role": "aprendiz",
                        "description": "Joven disciplinada que teme perder sus recuerdos",
                    }
                ],
                "style": "fantasia melancolica",
                "plot": "Una aprendiz descubre un reloj que rompe el tiempo y debe elegir entre la ciudad y su memoria.",
                "length": "medium",
                "language": "es",
            },
        )
        assert response.status_code == 202
        story_id = response.json()["id"]

        final_story = wait_for_story_completion(client, story_id)
        assert final_story["status"] == "completed"
        assert "Ayla" in final_story["story_text"]

        list_response = client.get("/stories")
        assert list_response.status_code == 200
        assert len(list_response.json()) == 1

        client.post("/auth/logout")
        register_user(client, "other@example.com")
        empty_list_response = client.get("/stories")
        assert empty_list_response.status_code == 200
        assert empty_list_response.json() == []


def test_failed_agent_run_is_recorded(tmp_path: Path) -> None:
    with create_test_client(tmp_path, fail_on="The Drama Coach") as client:
        register_user(client, "failure@example.com")

        response = client.post(
            "/stories/generate",
            json={
                "characters": [
                    {
                        "name": "Lena",
                        "role": "detective",
                        "description": "Investiga desapariciones ligadas a una estacion abandonada",
                    }
                ],
                "style": "thriller sobrio",
                "plot": "Una detective sigue pistas imposibles mientras su propio pasado se reescribe.",
                "length": "short",
                "language": "es",
            },
        )
        assert response.status_code == 202
        story_id = response.json()["id"]

        final_story = wait_for_story_completion(client, story_id)
        assert final_story["status"] == "failed"
        assert "drama_coach" in final_story["error_message"]

        with Session(client.app.state.engine) as session:
            story = session.exec(select(Story).where(Story.id == story_id)).one()
            runs = session.exec(select(StoryAgentRun).where(StoryAgentRun.story_id == story_id)).all()

        assert story.status == "failed"
        assert any(run.agent_name == "drama_coach" and run.status == "failed" for run in runs)


def test_dependency_manager_can_block_story(tmp_path: Path) -> None:
    with create_test_client(tmp_path, inconsistent_dependency=True) as client:
        register_user(client, "continuity@example.com")

        response = client.post(
            "/stories/generate",
            json={
                "characters": [
                    {
                        "name": "Miro",
                        "role": "mensajero",
                        "description": "Transporta reliquias y miente para sobrevivir",
                    }
                ],
                "style": "aventura contenida",
                "plot": "Un mensajero intenta completar una entrega imposible a traves de una ciudad suspendida.",
                "length": "short",
                "language": "es",
            },
        )
        assert response.status_code == 202

        final_story = wait_for_story_completion(client, response.json()["id"])
        assert final_story["status"] == "failed"
        assert "dependency_manager" in final_story["error_message"]


def test_gemini_429_message_is_sanitized() -> None:
    def handler(request):
        return httpx.Response(
            429,
            json={
                "error": {
                    "message": "Quota exceeded for free tier",
                    "status": "RESOURCE_EXHAUSTED",
                }
            },
            request=request,
        )

    client = GeminiClient(
        api_key="secret-key-should-not-leak",
        model="gemini-2.0-flash",
        max_retries=2,
        retry_base_seconds=0.01,
        transport=httpx.MockTransport(handler),
    )

    import asyncio

    try:
        asyncio.run(client.generate_json("test"))
        raise AssertionError("Expected GeminiRateLimitError")
    except GeminiRateLimitError as exc:
        message = str(exc)
        assert "quota" in message.lower() or "rate limit" in message.lower()
        assert "secret-key-should-not-leak" not in message
