import asyncio
from contextlib import suppress
from datetime import datetime, timezone

from sqlmodel import Session

from app.logging_utils import get_logger
from app.models import Story, StoryAgentRun
from app.schemas import StoryPacket
from app.services.agents import StoryAgents


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class StoryOrchestrator:
    def __init__(self, engine, llm_client) -> None:
        self.engine = engine
        self.agents = StoryAgents(llm_client)
        self.logger = get_logger("orchestrator")

    async def process_story(self, story_id: str) -> None:
        with Session(self.engine) as session:
            story = session.get(Story, story_id)
            if not story:
                return

            story.status = "running"
            story.updated_at = utc_now()
            session.add(story)
            session.commit()
            self.logger.info("story_started story_id=%s user_id=%s", story.id, story.user_id)

        try:
            await self._run_pipeline(story_id)
        except Exception as exc:
            self.logger.exception("story_failed story_id=%s error=%s", story_id, exc)
            with Session(self.engine) as session:
                story = session.get(Story, story_id)
                if story:
                    story.status = "failed"
                    if not story.error_message:
                        story.error_message = str(exc)
                    story.updated_at = utc_now()
                    session.add(story)
                    session.commit()

    async def _run_pipeline(self, story_id: str) -> None:
        with Session(self.engine) as session:
            story = session.get(Story, story_id)
            if not story:
                return
            packet = StoryPacket.parse_obj(story.story_packet or {"input_brief": story.input_brief})

        architect = await self._run_agent(story_id, "architect", packet, self.agents.run_architect)
        packet.architect_outline = architect
        await self._persist_packet(story_id, packet)

        world = await self._run_agent(story_id, "world_builder", packet, self.agents.run_world_builder)
        packet.world_bible = world
        await self._persist_packet(story_id, packet)

        drama = await self._run_agent(story_id, "drama_coach", packet, self.agents.run_drama_coach)
        packet.drama_revision = drama
        await self._persist_packet(story_id, packet)

        dependency = await self._run_agent(
            story_id,
            "dependency_manager",
            packet,
            self.agents.run_dependency_manager,
        )
        packet.dependency_review = dependency
        await self._persist_packet(story_id, packet)
        if not dependency.is_consistent and not dependency.fixes_applied:
            raise RuntimeError("dependency_manager: unresolved continuity issues")

        final_story = await self._run_agent(story_id, "narrator", packet, self.agents.run_narrator)
        packet.final_story = final_story
        await self._persist_packet(story_id, packet, completed=True)

    async def _run_agent(self, story_id: str, agent_name: str, packet: StoryPacket, runner):
        with Session(self.engine) as session:
            run = StoryAgentRun(
                story_id=story_id,
                agent_name=agent_name,
                status="running",
                input_snapshot=packet.dict(),
                started_at=utc_now(),
            )
            session.add(run)
            session.commit()
            session.refresh(run)

        try:
            output = await runner(packet)
        except Exception as exc:
            with Session(self.engine) as session:
                run = session.get(StoryAgentRun, run.id)
                if run:
                    run.status = "failed"
                    run.error_message = str(exc)
                    run.finished_at = utc_now()
                    session.add(run)
                story = session.get(Story, story_id)
                if story:
                    story.status = "failed"
                    story.error_message = f"{agent_name}: {exc}"
                    story.updated_at = utc_now()
                    session.add(story)
                session.commit()
            raise

        with Session(self.engine) as session:
            run = session.get(StoryAgentRun, run.id)
            if run:
                run.status = "completed"
                run.output_snapshot = output.dict()
                run.finished_at = utc_now()
                session.add(run)
                session.commit()

        return output

    async def _persist_packet(self, story_id: str, packet: StoryPacket, completed: bool = False) -> None:
        with Session(self.engine) as session:
            story = session.get(Story, story_id)
            if not story:
                return

            story.story_packet = packet.dict()
            story.updated_at = utc_now()
            if completed and packet.final_story:
                story.status = "completed"
                story.title = packet.final_story.title
                story.summary = packet.final_story.summary
                story.story_text = packet.final_story.story_text
                story.error_message = None
                self.logger.info("story_completed story_id=%s title=%s", story.id, story.title)
            session.add(story)
            session.commit()


class StoryWorker:
    def __init__(self, orchestrator: StoryOrchestrator) -> None:
        self.orchestrator = orchestrator
        self.queue: asyncio.Queue[str] = asyncio.Queue()
        self.task: asyncio.Task | None = None
        self.logger = get_logger("worker")

    async def start(self) -> None:
        if self.task is None:
            self.task = asyncio.create_task(self._run_loop())

    async def stop(self) -> None:
        if self.task is None:
            return
        self.task.cancel()
        with suppress(asyncio.CancelledError):
            await self.task
        self.task = None

    async def enqueue(self, story_id: str) -> None:
        await self.queue.put(story_id)
        self.logger.info("story_enqueued story_id=%s queue_size=%s", story_id, self.queue.qsize())

    async def _run_loop(self) -> None:
        while True:
            story_id = await self.queue.get()
            try:
                self.logger.info("story_dequeued story_id=%s queue_size=%s", story_id, self.queue.qsize())
                await self.orchestrator.process_story(story_id)
            finally:
                self.queue.task_done()
