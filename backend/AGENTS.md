# Backend Agent Guide

Usar este archivo solo para enrutamiento local de backend. El detalle vive en `story-backend-pipeline` y `story-contract-sync`.

## Fuentes de verdad

- `app/schemas.py`
- `app/models.py`
- `app/routers/auth.py`
- `app/routers/stories.py`
- `app/services/orchestrator.py`
- `app/services/agents.py`
- `app/services/gemini.py`
- `tests/test_api.py`

## Checklist breve

- Mantener prompts de agentes con salida JSON estricta y validar contra Pydantic.
- Persistir `StoryPacket` despues de cada etapa relevante del pipeline.
- Respetar estados `pending`, `running`, `completed`, `failed`.
- Si cambia cualquier payload, schema, ruta o flujo de estados que afecta al frontend, activar `story-contract-sync` antes de editar ambos lados.
