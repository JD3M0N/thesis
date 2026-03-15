# Story Writers Agent Guide

Mantener este archivo corto. Usarlo para routing y reglas globales; cargar detalle solo desde skills o archivos fuente.

## Arquitectura minima

- `backend/`: FastAPI + SQLModel + SQLite + worker local + pipeline multiagente con Gemini.
- `frontend/`: Next.js 15 + React 19 con auth local, composer, biblioteca, detalle y polling.
- Fuentes de verdad del dominio: `backend/app/` para backend, `frontend/lib/` y `frontend/components/` para frontend.

## Aclaracion importante

- Las skills en `.codex/skills/` son para Codex como agente de desarrollo.
- No forman parte del runtime del backend ni sustituyen a los agentes narrativos del proyecto.
- Los agentes reales del creador de historias viven en `backend/app/services/agents.py` y se orquestan desde `backend/app/services/orchestrator.py`.

## Routing de skills

- Usar `story-backend-pipeline` para cambios puros de FastAPI, SQLModel, auth, Gemini, worker u orquestacion.
- Usar `story-frontend-ui` para cambios puros de Next.js, componentes, formularios, polling, estados visuales o tests Vitest.
- Usar `story-contract-sync` cuando cambien requests, responses, `StoryStatus`, rutas `/auth` o `/stories`, o tipos compartidos backend/frontend.
- Si una tarea cruza backend y frontend, activar primero `story-contract-sync` y despues la skill del lado que se vaya a modificar.

## Reglas de contexto

- Leer primero archivos fuente de verdad; no inferir contratos desde README o HOW_TO_RUN si el codigo responde la duda.
- No cargar documentacion general del proyecto salvo que la tarea sea operativa o de arranque local.
- Evitar leer todo el repo. Abrir solo entrypoints, tipos, rutas y tests relacionados con la tarea.
- Mantener cambios de instrucciones cortos y sin duplicacion entre raiz, `backend/`, `frontend/` y skills.
