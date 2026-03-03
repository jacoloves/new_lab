# Repository Guidelines

## Project Structure & Module Organization
- `index.html` bootstraps the UI and loads `main.js`; keep DOM containers (e.g., `#container`) declared here.
- `main.ts` is the TypeScript source of the point counter logic; transpiled output is tracked in `main.js` for quick browser runs.
- Static assets belong alongside the page in the repo root; create `assets/` for images or data files so imports stay relative to `index.html`.

## Build, Test, and Development Commands
- `npx tsc main.ts --target ES2020 --outFile main.js` rebuilds the browser-ready script; run it after editing TypeScript.
- `npx tsc --watch main.ts --outFile main.js` keeps the compiler running during development.
- `npx serve .` (or any static HTTP server) launches a local preview so you can refresh `index.html` without browser security warnings.

## Coding Style & Naming Conventions
- Stick to TypeScript + DOM APIs; prefer ES modules only if you also adjust `index.html` script loading.
- Use 2-space indentation, single quotes for strings, and descriptive camelCase identifiers (`updateScoreBoard`).
- Keep DOM IDs kebab-cased (`#point-list`) and co-locate lightweight helpers inside `main.ts` until they justify a new module.

## Testing Guidelines
- Manual verification is expected today: rebuild, run `npx serve .`, and confirm workflows in Chrome + Firefox private windows.
- When adding automated tests, favor browser-driven harnesses (Playwright or Vitest + jsdom) and name specs after the feature, e.g., `counter.spec.ts`.
- Break changes should include scenario notes in PRs describing reproduction steps so others can re-run them locally.

## Commit & Pull Request Guidelines
- Follow the existing log style: short, imperative, lower-case summaries (`add scoring widget`).
- Squash work-in-progress commits before review, reference related issue IDs in the body, and describe user-facing impact plus screenshots for UI tweaks.
- Every PR should list build/test commands that were executed and highlight any new configuration knobs or environment assumptions.

## Security & Configuration Tips
- This app runs entirely in the browser, so never check in secrets or API keys; mock data locally when needed.
- Validate any new third-party scripts before inclusion and pin their versions to avoid silent regressions.
