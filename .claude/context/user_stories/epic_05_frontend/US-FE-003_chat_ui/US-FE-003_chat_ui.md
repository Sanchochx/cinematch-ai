# US-FE-003: UI de chat accesible con recomendaciones

**Épica:** 05 — Frontend
**Prioridad:** CRÍTICA
**Estimación:** 5 pts
**Dependencias:** US-FE-002

## Historia de usuario
**Como** aficionado al cine,
**quiero** una ventana de chat clara donde escribo qué me apetece ver y leo las recomendaciones del asistente,
**para** descubrir películas sin tener que buscar manualmente.

## Contexto técnico
- Componentes (cada uno ≤ ~150 líneas, UI pura, lógica en `useChat`) dentro de `features/chat/components/`:
  `ChatWindow`, `MessageList`, `MessageBubble`, `ChatComposer` (formulario), `TypingIndicator`, `ErrorBanner`, `EmptyState`.
- Estilos con **CSS Modules**, mobile-first, `clamp()` para tamaños, Grid para el layout (cabecera / lista / compositor).
- Las respuestas del asistente llegan como texto (`reply`). Se renderizan **sin `dangerouslySetInnerHTML`**: párrafos, saltos de
  línea y listas simples (`-`, `1.`) convertidos a elementos React. Cualquier HTML en la respuesta se muestra como texto.
- Textos de UI en español; nombres de código en inglés.

## Criterios de aceptación
**Funcionalidad**
- [ ] Estado vacío con bienvenida y 3 *prompts* sugeridos clicables que rellenan/envían el mensaje.
- [ ] El usuario escribe en un `<textarea>` y envía con botón o `Enter` (`Shift+Enter` = salto de línea).
- [ ] Burbujas diferenciadas usuario/asistente; la lista hace *scroll* automático al último mensaje sin saltos de layout.
- [ ] Mientras `isLoading` se muestra `TypingIndicator` y se deshabilita el envío (no se pierde el texto escrito).
- [ ] Contador/validación de longitud (≤ 2000) con mensaje de error asociado vía `aria-describedby`; no se envía vacío.
- [ ] En error: `ErrorBanner` con mensaje en español según `ChatErrorKind` y botón **Reintentar** (`retry`).
- [ ] La respuesta del asistente muestra la recomendación formateada (párrafos/listas); el HTML crudo nunca se interpreta.

**Accesibilidad (no negociable)**
- [ ] Todo es operable con teclado (`Tab`, `Enter`/`Space`); orden de foco lógico; tras enviar, el foco vuelve al `textarea`.
- [ ] `<label>` asociada al textarea (puede ser visualmente oculta, no solo `placeholder`).
- [ ] La lista de mensajes es una región `role="log"` con `aria-live="polite"`; el estado de carga se anuncia ("El asistente está escribiendo").
- [ ] `:focus-visible` visible en todos los controles; nunca `outline: none` sin reemplazo.
- [ ] Contraste AA (4.5:1 texto normal, 3:1 grande) verificado; objetivos táctiles ≥ 44px.
- [ ] `prefers-reduced-motion` respetado; animaciones solo con `transform`/`opacity` (150–200 ms).
- [ ] HTML semántico (`<main>`, `<header>`, `<form>`, `<button>`); un único `<h1>`.

**Rendimiento y calidad**
- [ ] Layout responsivo probado a 320px, 768px y 1280px sin scroll horizontal; CLS = 0 (alturas reservadas).
- [ ] Ruta/feature cargada con `React.lazy` + `Suspense` (*bundle splitting* por feature).
- [ ] Sin `any`, sin `console.log`; ESLint/Prettier sin warnings.
- [ ] Tests (Vitest + Testing Library): cada componente tiene al menos un test de renderizado; flujos: enviar con Enter,
  Shift+Enter no envía, vacío bloqueado, estado de carga, error + reintentar, escape de HTML en respuestas, prompts sugeridos.
- [ ] Revisión automática de a11y (p. ej. `jest-axe`/`vitest-axe`) sin violaciones en el estado vacío, con mensajes y con error.

## Fuera de alcance
- Fichas con póster/metadatos (requiere ampliar el contrato `{reply, movies[]}`), streaming de tokens, modo oscuro,
  persistencia del chat tras recargar, Playwright E2E.

## Definition of Done
- Criterios marcados `[x]`; `npm run lint`, `npm test`, `npm run build` en verde.
- Demostración manual contra el stack completo: conversación de 3+ turnos con recomendaciones reales; error simulado
  (parando `ai-engine`) muestra el banner y `Reintentar` funciona al volver.
- Verificado con teclado y con un lector de pantalla (al menos revisión del árbol de accesibilidad en DevTools).
- Lighthouse (móvil): Accesibilidad ≥ 95 y Best Practices ≥ 95.
- Revisado con el skill `code-review`.
- Plan de implementación actualizado.
