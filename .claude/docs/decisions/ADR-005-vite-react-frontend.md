# ADR-005: Vite + React 19 + TypeScript strict (servido con nginx) para el frontend

**Fecha:** 2026-10-08
**Estado:** Aceptada
**Historia:** US-FE-001

## Contexto
El frontend debe ofrecer una ventana de chat moderna y sencilla, cumpliendo los Frontend Standards
de `CLAUDE.md` (componentes tipados, hooks, CSS Modules, accesibilidad, tests con Testing Library).

## Decisión
- **Vite + React 19 + TypeScript `strict`**. Estructura por feature (`src/features/chat/...`).
- **CSS Modules + design tokens** en `:root` (sin librerías de UI); estado local con hooks, sin Zustand.
- **Vitest + Testing Library** para tests; ESLint (sin `any`, sin `console`) + Prettier.
- **`VITE_API_URL`** (por defecto `http://localhost:3000`) se inlinea en build time: es la URL del
  gateway vista desde el **navegador**, no resoluble por nombre de servicio Compose.
- **Producción:** build estático servido por `nginxinc/nginx-unprivileged` en el puerto 3000 (US-FE-004).

## Alternativas descartadas
- **HTML/Vanilla JS:** no permite cumplir los estándares de componentes tipados y tests del proyecto.
- **`vite preview` en producción:** no está pensado para ello.

## Consecuencias
- Cambiar la URL del gateway exige reconstruir la imagen (build arg).
- El contrato `{reply: string}` limita la UI a texto; las fichas con póster quedan como deuda técnica.
