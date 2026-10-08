# US-FE-001: Proyecto Vite + React 19 + TypeScript strict, tokens y tooling

**Épica:** 05 — Frontend
**Prioridad:** CRÍTICA
**Estimación:** 2 pts
**Dependencias:** Ninguna

## Historia de usuario
**Como** desarrollador del equipo,
**quiero** un proyecto React 19 con Vite, TypeScript estricto, design tokens y herramientas de calidad,
**para** construir la UI sobre una base que cumple los Frontend Standards desde el primer commit.

## Contexto técnico
- Reemplaza el stub `frontend/index.js`. Estructura por feature (según `CLAUDE.md`):
  ```
  frontend/
  ├── package.json · package-lock.json · vite.config.ts · tsconfig*.json · index.html
  ├── src/
  │   ├── main.tsx · App.tsx
  │   ├── styles/tokens.css · global.css       ← variables en :root, reset
  │   ├── config/env.ts                         ← lee y valida import.meta.env.VITE_API_URL
  │   └── features/chat/{components,services,models,hooks}/ + index.ts
  └── tests/ (o colocados junto al código; setup de Vitest en tests/setup.ts)
  ```
- Design tokens (en `:root`): spacing base 4px, escala tipográfica con `clamp()`, `--color-*`, `--radius-*`, `--shadow-*`.
- `VITE_API_URL` (por defecto `http://localhost:3000`) es la única variable; no es secreto.

## Criterios de aceptación
- [x] `package.json` con React 19, TypeScript, Vite y scripts `dev`, `build`, `preview`, `lint`, `test`.
- [x] `tsconfig` con `"strict": true`; `npm run build` ejecuta `tsc --noEmit` sin errores y **sin `any`** (regla ESLint activa).
- [x] ESLint + Prettier configurados; `npm run lint` sin warnings.
- [x] `styles/tokens.css` define spacing (múltiplos de 4px), tipografía fluida con `clamp()`, colores `--color-*`,
  radios y sombras; los colores de texto/fondo cumplen contraste WCAG AA (4.5:1).
- [x] Reset/base global con `:focus-visible` estilizado y `@media (prefers-reduced-motion: reduce)` que anula animaciones.
- [x] `config/env.ts` expone `API_URL` tipada; si falta usa el valor por defecto y no se leen otras variables.
- [x] `index.html` con `lang="es"`, `<title>` descriptivo, `meta viewport` y `meta description`.
- [x] Vitest + Testing Library configurados (`jsdom`); existe un test de renderizado de `App` en verde.
- [x] `npm run dev` sirve en `localhost:5173` (alineado con `CORS_ORIGIN`) y `npm run build` genera `dist/`.
- [x] No hay `console.log` ni credenciales en el código.

## Fuera de alcance
- Componentes del chat, llamadas HTTP, Dockerfile y compose.

## Definition of Done
- Criterios marcados `[x]`; `npm run lint`, `npm test` y `npm run build` en verde.
- ADR registrado en `docs/decisions/` (Vite + React 19 como stack del frontend).
- `.gitignore` cubre `node_modules/` y `dist/`.
- Plan de implementación actualizado.
