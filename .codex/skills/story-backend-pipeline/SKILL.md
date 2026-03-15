---
name: story-backend-pipeline
description: Backend FastAPI/SQLModel/Gemini workflow for Story Writers. Use when Codex changes Python backend behavior, auth, routers, database models, Gemini integration, worker execution, StoryPacket persistence, or the multi-agent story pipeline. Usar cuando la tarea sea de backend puro y no requiera coordinar contratos con el frontend.
---

# Story Backend Pipeline

Seguir este skill para cambios puros del backend. Mantener el cuerpo corto y cargar detalle desde `references/` solo si hace falta.

## Flujo

- Leer primero `references/backend-map.md` para ubicar entrypoints, comandos y archivos fuente de verdad.
- Leer `references/pipeline-guardrails.md` antes de tocar prompts, `StoryPacket`, estados o persistencia del pipeline.
- Si cambian payloads HTTP, tipos compartidos o estados consumidos por el frontend, cambiar a `story-contract-sync` antes de seguir.

## Reglas

- Tratar `app/schemas.py`, `app/models.py`, `app/routers/`, `app/services/orchestrator.py`, `app/services/agents.py` y `tests/test_api.py` como fuentes de verdad.
- Mantener prompts de agentes con salida JSON estricta y validacion Pydantic.
- Persistir `StoryPacket` despues de cada etapa completada; no saltar actualizaciones intermedias sin motivo.
- Preservar la semantica de estados `pending`, `running`, `completed`, `failed`.
- Preferir cambios minimos con pruebas en `backend/tests/test_api.py` cuando la conducta cambie.

## Referencias

- `references/backend-map.md`
- `references/pipeline-guardrails.md`
