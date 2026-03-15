import json
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from app.schemas import (
    ArchitectOutline,
    DependencyReview,
    DramaRevision,
    FinalStory,
    StoryPacket,
    WorldBible,
)

T = TypeVar("T", bound=BaseModel)


class StoryAgents:
    def __init__(self, llm_client) -> None:
        self.llm_client = llm_client

    async def run_architect(self, packet: StoryPacket) -> ArchitectOutline:
        prompt = f"""
You are The Architect in a multi-agent story room.
Return strict JSON only.
Build the narrative skeleton from this user brief:
{json.dumps(packet.input_brief, ensure_ascii=False, indent=2)}

Required JSON shape:
{{
  "premise": "string",
  "beats": [{{"title": "string", "purpose": "string", "stakes": "string"}}],
  "climax": "string",
  "resolution": "string"
}}
"""
        return await self._generate_structured(prompt, ArchitectOutline)

    async def run_world_builder(self, packet: StoryPacket) -> WorldBible:
        prompt = f"""
You are The World Builder.
Return strict JSON only.
Expand the story outline with grounded lore, character motivations, locations, objects and world rules.

Current packet:
{json.dumps(packet.dict(), ensure_ascii=False, indent=2)}

Required JSON shape:
{{
  "characters": [
    {{"name": "string", "role": "string", "description": "string", "desire": "string", "fear": "string"}}
  ],
  "locations": [
    {{"name": "string", "description": "string", "mood": "string"}}
  ],
  "objects": [
    {{"name": "string", "significance": "string"}}
  ],
  "rules": ["string"]
}}
"""
        return await self._generate_structured(prompt, WorldBible)

    async def run_drama_coach(self, packet: StoryPacket) -> DramaRevision:
        prompt = f"""
You are The Drama Coach.
Return strict JSON only.
Analyze the current packet and make the story more dramatic without breaking its internal logic.

Current packet:
{json.dumps(packet.dict(), ensure_ascii=False, indent=2)}

Required JSON shape:
{{
  "revised_beats": [{{"title": "string", "purpose": "string", "stakes": "string"}}],
  "tension_notes": ["string"],
  "character_arc_notes": ["string"]
}}
"""
        return await self._generate_structured(prompt, DramaRevision)

    async def run_dependency_manager(self, packet: StoryPacket) -> DependencyReview:
        prompt = f"""
You are The Dependency Manager.
Return strict JSON only.
Review continuity, causality and character consistency. If needed, propose fixes and narrator guidance.

Current packet:
{json.dumps(packet.dict(), ensure_ascii=False, indent=2)}

Required JSON shape:
{{
  "is_consistent": true,
  "issues": ["string"],
  "fixes_applied": ["string"],
  "narrator_guidance": ["string"]
}}
"""
        return await self._generate_structured(prompt, DependencyReview)

    async def run_narrator(self, packet: StoryPacket) -> FinalStory:
        prompt = f"""
You are The Narrator.
Write polished prose in the requested language and style.
Use the packet below as the full source of truth.
Return strict JSON only.

Current packet:
{json.dumps(packet.dict(), ensure_ascii=False, indent=2)}

Required JSON shape:
{{
  "title": "string",
  "summary": "string",
  "story_text": "string"
}}
"""
        return await self._generate_structured(prompt, FinalStory)

    async def _generate_structured(self, prompt: str, model_type: type[T]) -> T:
        payload = await self.llm_client.generate_json(prompt)
        try:
            return model_type.parse_obj(payload)
        except ValidationError as exc:
            raise RuntimeError(f"Invalid payload for {model_type.__name__}: {exc}") from exc
