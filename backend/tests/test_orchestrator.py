import asyncio

from .fakes import DRAMA_COACH_PROMPT, FakeGeminiClient
from .support import create_story_record, create_test_engine, create_user_record, get_story, list_agent_runs
from app.services.orchestrator import StoryOrchestrator


def test_orchestrator_completes_story_and_records_all_runs(db_path) -> None:
    engine = create_test_engine(db_path)
    user = create_user_record(engine, "orchestrator@example.com")
    story = create_story_record(engine, user.id)
    orchestrator = StoryOrchestrator(engine=engine, llm_client=FakeGeminiClient())

    asyncio.run(orchestrator.process_story(story.id))

    stored_story = get_story(engine, story.id)
    runs = list_agent_runs(engine, story.id)

    assert stored_story.status == "completed"
    assert stored_story.story_text is not None
    assert [run.agent_name for run in runs] == [
        "architect",
        "world_builder",
        "drama_coach",
        "dependency_manager",
        "narrator",
    ]
    assert all(run.status == "completed" for run in runs)
    assert all(run.output_snapshot for run in runs)


def test_orchestrator_marks_story_failed_when_agent_raises(db_path) -> None:
    engine = create_test_engine(db_path)
    user = create_user_record(engine, "failure@example.com")
    story = create_story_record(engine, user.id)
    orchestrator = StoryOrchestrator(
        engine=engine,
        llm_client=FakeGeminiClient(fail_on=DRAMA_COACH_PROMPT),
    )

    asyncio.run(orchestrator.process_story(story.id))

    stored_story = get_story(engine, story.id)
    runs = list_agent_runs(engine, story.id)

    assert stored_story.status == "failed"
    assert stored_story.error_message == "drama_coach: Synthetic agent failure"
    assert [run.agent_name for run in runs] == ["architect", "world_builder", "drama_coach"]
    assert [run.status for run in runs] == ["completed", "completed", "failed"]


def test_orchestrator_blocks_story_when_dependency_review_is_inconsistent(db_path) -> None:
    engine = create_test_engine(db_path)
    user = create_user_record(engine, "continuity@example.com")
    story = create_story_record(engine, user.id)
    orchestrator = StoryOrchestrator(
        engine=engine,
        llm_client=FakeGeminiClient(inconsistent_dependency=True),
    )

    asyncio.run(orchestrator.process_story(story.id))

    stored_story = get_story(engine, story.id)
    runs = list_agent_runs(engine, story.id)

    assert stored_story.status == "failed"
    assert stored_story.error_message == "dependency_manager: unresolved continuity issues"
    assert [run.agent_name for run in runs] == [
        "architect",
        "world_builder",
        "drama_coach",
        "dependency_manager",
    ]
    assert all(run.status == "completed" for run in runs)
