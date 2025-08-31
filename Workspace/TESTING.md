# Frontend Testing Guide

## Overview
We use Vitest + React Testing Library to provide fast, framework-aligned unit/integration (component) tests.

## Commands
- `pnpm test` / `npm run test` – run test suite once
- `pnpm test:watch` – watch mode during development
- `pnpm test:ui` – experimental Vitest UI

## Structure
Tests live next to source (e.g. `src/pages/__tests__`) to keep context local. A global setup file `src/test/setupTests.ts` configures jsdom, jest-dom matchers, and helper utilities.

## Auth Simulation
`renderApp({ withAuth: true })` sets a temporary `access_token` in `localStorage` so protected routes pass the `ProtectedRoute` gate.

## Theme Toggle Rollback
The theme toggle is feature-flagged by `VITE_ENABLE_THEME_TOGGLE` (default enabled). To rollback / disable without code removal:
1. Set `.env` (or `.env.local`) value: `VITE_ENABLE_THEME_TOGGLE=false`
2. Rebuild or restart dev server. The toggle component renders `null` when disabled, preserving previous styling.

## Adding New Tests
1. Identify user-facing invariant (text, role, aria-label) to assert.
2. Prefer `getByRole` or `findByRole` for accessibility alignment.
3. Use `userEvent` for interactions, not `fireEvent` (more realistic sequences).
4. Keep each test focused (1-3 expectations). Complex multi-step flows should be split.

## Coverage
Run with coverage: `vitest run --coverage`. Reports emitted to `coverage/` (text + HTML). Aim to steadily raise line & branch coverage. Focus first on critical routing & interaction surfaces.

## Mocking Network
For future API interaction tests, introduce `msw` handlers in `src/test/server.ts` and import them in `setupTests.ts`. (Handler scaffolding intentionally deferred until API interaction tests are added.)

## Troubleshooting
- Missing matcher: ensure `@testing-library/jest-dom` is imported in setup file.
- Failing due to navigation: confirm route is in `<App />`. For dynamic params, include path (e.g., `/campaigns/123/edit`).
- Component using `useEffect` data fetch: if immediate assertion fails, switch to `findBy*` async query.

## Next Steps (Suggested)
- Add MSW-powered tests for media upload happy/error paths.
- Add boundary tests for menu editor drag & drop ordering logic.
- Add analytics chart rendering assertions (presence of SVG elements, dataset lengths).

---
Generated automatically. Update as the testing surface evolves.
