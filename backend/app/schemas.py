from typing import Any, Literal

from pydantic import BaseModel, EmailStr, Field, conlist


StoryLength = Literal["short", "medium", "long"]
StoryStatus = Literal["pending", "running", "completed", "failed"]


class CharacterInput(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    role: str = Field(min_length=1, max_length=80)
    description: str = Field(min_length=1, max_length=300)


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserRead(BaseModel):
    id: str
    email: EmailStr

    class Config:
        orm_mode = True


class AuthResponse(BaseModel):
    user: UserRead


class StoryGenerateRequest(BaseModel):
    characters: conlist(CharacterInput, min_items=1, max_items=6)
    style: str = Field(min_length=2, max_length=80)
    plot: str = Field(min_length=12, max_length=1500)
    length: StoryLength
    language: str = Field(default="es", min_length=2, max_length=16)

    def to_input_brief(self) -> dict[str, Any]:
        return {
            "characters": [character.dict() for character in self.characters],
            "style": self.style,
            "plot": self.plot,
            "length": self.length,
            "language": self.language,
        }


class StoryJobCreated(BaseModel):
    id: str
    status: StoryStatus


class StoryListItem(BaseModel):
    id: str
    title: str | None
    summary: str | None
    style: str
    plot: str
    length: StoryLength
    language: str
    status: StoryStatus
    created_at: str
    updated_at: str


class StoryDetail(BaseModel):
    id: str
    title: str | None
    summary: str | None
    style: str
    plot: str
    length: StoryLength
    language: str
    status: StoryStatus
    story_text: str | None
    error_message: str | None
    created_at: str
    updated_at: str


class StoryBeat(BaseModel):
    title: str
    purpose: str
    stakes: str


class CharacterProfile(BaseModel):
    name: str
    role: str
    description: str
    desire: str
    fear: str


class LocationProfile(BaseModel):
    name: str
    description: str
    mood: str


class ObjectProfile(BaseModel):
    name: str
    significance: str


class ArchitectOutline(BaseModel):
    premise: str
    beats: list[StoryBeat]
    climax: str
    resolution: str


class WorldBible(BaseModel):
    characters: list[CharacterProfile]
    locations: list[LocationProfile]
    objects: list[ObjectProfile]
    rules: list[str]


class DramaRevision(BaseModel):
    revised_beats: list[StoryBeat]
    tension_notes: list[str]
    character_arc_notes: list[str]


class DependencyReview(BaseModel):
    is_consistent: bool
    issues: list[str]
    fixes_applied: list[str]
    narrator_guidance: list[str]


class FinalStory(BaseModel):
    title: str
    summary: str
    story_text: str


class StoryPacket(BaseModel):
    input_brief: dict[str, Any]
    architect_outline: ArchitectOutline | None = None
    world_bible: WorldBible | None = None
    drama_revision: DramaRevision | None = None
    dependency_review: DependencyReview | None = None
    final_story: FinalStory | None = None
