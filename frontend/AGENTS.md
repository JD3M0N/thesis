# Frontend Agent Guide

Usar este archivo solo para enrutamiento local de frontend. El detalle vive en `story-frontend-ui` y `story-contract-sync`.

## Fuentes de verdad

- `lib/types.ts`
- `lib/api.ts`
- `components/dashboard.tsx`
- `components/story-composer.tsx`
- `components/story-library.tsx`
- `components/story-detail-view.tsx`
- `components/*.test.tsx`

## Checklist breve

- Mantener `apiRequest` como adaptador central de fetch y errores.
- Conservar el polling basado en historias con estado `pending` o `running`.
- Alinear formularios y vistas con `lib/types.ts`, no con respuestas inferidas manualmente.
- Si cambia cualquier response del backend, request compartido o valor de estado, activar `story-contract-sync` antes de editar ambos lados.
