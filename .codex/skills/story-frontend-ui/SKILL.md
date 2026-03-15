---
name: story-frontend-ui
description: Frontend Next.js/React workflow for Story Writers. Use when Codex changes UI behavior, auth screens, dashboard flow, story composer, library/detail components, polling, fetch helpers, or Vitest coverage in the frontend. Usar cuando la tarea sea de frontend puro y no requiera cambiar contratos compartidos.
---

# Story Frontend Ui

Seguir este skill para cambios puros de interfaz y comportamiento del frontend. Mantener el contexto corto y cargar detalle desde `references/` solo cuando la tarea lo exija.

## Flujo

- Leer primero `references/frontend-map.md` para ubicar el flujo `auth/me -> stories -> polling -> detail`, tipos y componentes.
- Leer `references/ui-guardrails.md` antes de tocar formularios, errores, polling o tests.
- Si cambian request/response, estados o tipos compartidos con backend, cambiar a `story-contract-sync` antes de seguir.

## Reglas

- Tratar `lib/types.ts`, `lib/api.ts`, `components/dashboard.tsx`, `components/story-composer.tsx`, `components/story-library.tsx`, `components/story-detail-view.tsx` y tests Vitest como fuentes de verdad.
- Mantener `apiRequest` como adaptador central de fetch, cookies y errores.
- Conservar el polling solo mientras existan historias `pending` o `running`.
- Alinear formularios y vistas con los tipos de `lib/types.ts`.
- Cubrir cambios de comportamiento con tests Vitest cuando el flujo visible cambie.

## Referencias

- `references/frontend-map.md`
- `references/ui-guardrails.md`
