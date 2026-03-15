---
name: story-contract-sync
description: Cross-stack contract workflow for Story Writers. Use when Codex changes API routes, request or response payloads, shared status values, auth/session behavior, or any backend/frontend type boundary that must stay synchronized. Usar cuando una tarea toque contratos compartidos entre FastAPI y Next.js.
---

# Story Contract Sync

Seguir este skill cuando una tarea cruce backend y frontend por contratos, tipos o estados. Cargar detalle desde `references/contracts.md` y mantener el cuerpo corto.

## Flujo

- Leer `references/contracts.md` antes de editar codigo.
- Actualizar primero la fuente de verdad del contrato en backend, luego los tipos/adaptadores del frontend y despues los componentes afectados.
- Verificar que rutas `/auth` y `/stories`, payloads y estados sigan alineados.
- Si el cambio tambien altera logica interna compleja, combinar despues con `story-backend-pipeline` o `story-frontend-ui`.

## Reglas

- Tratar `backend/app/schemas.py` y `frontend/lib/types.ts` como definiciones primarias de payloads.
- Revisar `frontend/lib/api.ts` si cambia manejo de errores, cookies o codigos de respuesta.
- Mantener consistentes los valores de `StoryStatus`: `pending`, `running`, `completed`, `failed`.
- Reflejar cambios de contrato en tests backend o frontend cuando el comportamiento observable cambie.

## Referencias

- `references/contracts.md`
