# Pipeline Guardrails

## Prompt invariants

- Keep each agent prompt role-specific: Architect, World Builder, Drama Coach, Dependency Manager, Narrator.
- Require strict JSON output in every structured stage.
- Validate each payload with the matching Pydantic model before persisting or advancing.

## Persistence invariants

- `StoryPacket` starts with `input_brief`.
- Persist the packet after architect, world builder, drama coach, dependency manager, and narrator.
- On completion, copy `title`, `summary`, and `story_text` from `final_story` into `Story`.
- Keep failed runs observable through `StoryAgentRun` and `Story.error_message`.

## State invariants

- `pending` before worker processing
- `running` once processing starts
- `completed` only when `final_story` is persisted
- `failed` on any agent or continuity failure

## Test expectations

- Backend tests already cover successful generation, failed agent runs, dependency blocking, and Gemini 429 sanitization.
- Extend `backend/tests/test_api.py` when a behavior change affects route outputs, pipeline states, or failure handling.
