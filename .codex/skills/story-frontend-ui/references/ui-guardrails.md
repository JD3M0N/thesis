# UI Guardrails

## Data flow

- Keep `apiRequest` as the central place for `fetch`, JSON serialization, cookies, and error parsing.
- Do not hardcode backend payload shapes inside components when `lib/types.ts` can express them.
- Prefer fetching fresh stories after auth or story creation instead of optimistic local reconstruction.

## State behavior

- `Dashboard` owns bootstrap auth loading and polling control.
- Poll only while the user is authenticated and at least one story remains `pending` or `running`.
- Preserve visible error handling in forms when `ApiError` or network failures happen.

## Testing patterns

- Use Vitest plus Testing Library for behavior, not implementation details.
- Cover changed interactions such as add/remove character, submit, error display, and conditional polling logic.

## Contract boundary

- If a change touches route payloads, status names, or auth/session response shapes, stop and load `story-contract-sync`.
