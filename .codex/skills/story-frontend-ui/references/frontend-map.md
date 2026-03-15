# Frontend Map

## Entrypoints

- App shell: `frontend/app/page.tsx`
- Layout and global styles: `frontend/app/layout.tsx`, `frontend/app/globals.css`
- Fetch adapter: `frontend/lib/api.ts`
- Shared UI types: `frontend/lib/types.ts`
- Dashboard flow: `frontend/components/dashboard.tsx`
- Story composer: `frontend/components/story-composer.tsx`
- Story library: `frontend/components/story-library.tsx`
- Story detail: `frontend/components/story-detail-view.tsx`
- Frontend tests: `frontend/components/story-composer.test.tsx`

## Source of truth order

1. `frontend/lib/types.ts` for frontend payload shapes
2. `frontend/lib/api.ts` for request and error behavior
3. `frontend/components/*.tsx` for visible UX and data flow
4. Vitest files for expected behavior

## Runtime flow

1. `Dashboard` calls `/auth/me`
2. If authenticated, load `/stories`
3. Poll every 3 seconds while any story is `pending` or `running`
4. `StoryComposer` posts `/stories/generate`
5. Library and detail views render returned state

## Commands

- Install frontend deps: `cd frontend && npm install`
- Run dev server: `cd frontend && npm run dev`
- Run tests: `cd frontend && npm test`

## Task routing

- Pure UI, copy, auth screen, dashboard, composer, library, reader, or polling changes stay in this skill.
- Shared API shape or status changes must switch to `story-contract-sync`.
