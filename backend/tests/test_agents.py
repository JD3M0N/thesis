import asyncio

import pytest

from app.schemas import ArchitectOutline, DependencyReview, DramaRevision, FinalStory, StoryPacket, WorldBible
from app.services.agents import StoryAgents

from .fakes import (
    ARCHITECT_PROMPT,
    DEPENDENCY_MANAGER_PROMPT,
    DRAMA_COACH_PROMPT,
    NARRATOR_PROMPT,
    WORLD_BUILDER_PROMPT,
    FakeGeminiClient,
    build_story_request,
)
def build_packet() -> StoryPacket:
    from app.schemas import StoryGenerateRequest

    request = StoryGenerateRequest.parse_obj(build_story_request())
    return StoryPacket.parse_obj({"input_brief": request.to_input_brief()})


@pytest.mark.parametrize(
    ("method_name", "expected_type", "expected_value"),
    [
        ("run_architect", ArchitectOutline, "Una aprendiz encuentra un reloj"),
        ("run_world_builder", WorldBible, "Archivo del Reloj"),
        ("run_drama_coach", DramaRevision, "Traicion del mentor"),
        ("run_dependency_manager", DependencyReview, True),
        ("run_narrator", FinalStory, "El reloj de la torre muda"),
    ],
)
def test_story_agents_return_structured_models(
    method_name: str,
    expected_type: type,
    expected_value,
) -> None:
    agents = StoryAgents(FakeGeminiClient())
    packet = build_packet()

    result = asyncio.run(getattr(agents, method_name)(packet))

    assert isinstance(result, expected_type)
    if isinstance(expected_value, bool):
        assert result.is_consistent is expected_value
    elif hasattr(result, "title"):
        assert result.title == expected_value
    elif hasattr(result, "locations"):
        assert result.locations[0].name == expected_value
    elif hasattr(result, "revised_beats"):
        assert result.revised_beats[0].title == expected_value
    else:
        assert result.premise.startswith(expected_value)


@pytest.mark.parametrize(
    ("prompt_marker", "method_name", "model_name"),
    [
        (ARCHITECT_PROMPT, "run_architect", "ArchitectOutline"),
        (WORLD_BUILDER_PROMPT, "run_world_builder", "WorldBible"),
        (DRAMA_COACH_PROMPT, "run_drama_coach", "DramaRevision"),
        (DEPENDENCY_MANAGER_PROMPT, "run_dependency_manager", "DependencyReview"),
        (NARRATOR_PROMPT, "run_narrator", "FinalStory"),
    ],
)
def test_story_agents_reject_invalid_payloads(
    prompt_marker: str,
    method_name: str,
    model_name: str,
) -> None:
    agents = StoryAgents(FakeGeminiClient(invalid_payload_for=prompt_marker))
    packet = build_packet()

    with pytest.raises(RuntimeError, match=f"Invalid payload for {model_name}"):
        asyncio.run(getattr(agents, method_name)(packet))
