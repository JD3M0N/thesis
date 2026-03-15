# Contracts

## Shared types

| Concern | Backend source | Frontend source | Notes |
| --- | --- | --- | --- |
| Character input | `backend/app/schemas.py::CharacterInput` | `frontend/lib/types.ts::CharacterInput` | Name, role, description |
| Story create request | `backend/app/schemas.py::StoryGenerateRequest` | `frontend/lib/types.ts::StoryGenerateRequest` | Characters, style, plot, length, language |
| Story job response | `backend/app/schemas.py::StoryJobCreated` | `frontend/lib/types.ts::StoryJobCreated` | `id`, `status` |
| Story list item | `backend/app/schemas.py::StoryListItem` | `frontend/lib/types.ts::StoryListItem` | List payload from `/stories` |
| Story detail | `backend/app/schemas.py::StoryDetail` | `frontend/lib/types.ts::StoryDetail` | Detail payload from `/stories/{id}` |
| Auth response | `backend/app/schemas.py::AuthResponse` | `frontend/lib/types.ts::AuthResponse` | Wraps `user` |

## Shared status values

| Status | Backend usage | Frontend usage |
| --- | --- | --- |
| `pending` | Initial story state before processing | Displayed and polled |
| `running` | Worker is processing the story | Displayed and polled |
| `completed` | Final story persisted | Stops polling, story readable |
| `failed` | Pipeline or dependency failure | Stops polling, show error |

## Route map

| Route | Backend file | Frontend caller | Response shape |
| --- | --- | --- | --- |
| `GET /auth/me` | `backend/app/routers/auth.py` | `frontend/components/dashboard.tsx` | `AuthResponse` |
| `POST /auth/register` | `backend/app/routers/auth.py` | `frontend/components/auth-panel.tsx` | `AuthResponse` |
| `POST /auth/login` | `backend/app/routers/auth.py` | `frontend/components/auth-panel.tsx` | `AuthResponse` |
| `POST /auth/logout` | `backend/app/routers/auth.py` | `frontend/components/dashboard.tsx` | `204 No Content` |
| `GET /stories` | `backend/app/routers/stories.py` | `frontend/components/dashboard.tsx` | `StoryListItem[]` |
| `GET /stories/{story_id}` | `backend/app/routers/stories.py` | story detail route/components | `StoryDetail` |
| `POST /stories/generate` | `backend/app/routers/stories.py` | `frontend/components/story-composer.tsx` | `StoryJobCreated` |

## Sync workflow

1. Update backend schema or route source of truth.
2. Update frontend `lib/types.ts` and `lib/api.ts` if needed.
3. Update affected components and tests.
4. Run backend and frontend tests relevant to the changed boundary.

## Guardrails

- Do not rename or add status values on one side only.
- Do not change response shape in a router without updating `frontend/lib/types.ts`.
- If auth cookie, error format, or fetch status handling changes, review `frontend/lib/api.ts` explicitly.
