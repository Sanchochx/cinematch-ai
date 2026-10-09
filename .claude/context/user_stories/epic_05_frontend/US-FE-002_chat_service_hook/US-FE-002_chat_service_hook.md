# US-FE-002: Feature `chat` — modelos, servicio HTTP y hook `useChat`

**Épica:** 05 — Frontend
**Prioridad:** CRÍTICA
**Estimación:** 3 pts
**Dependencias:** US-FE-001 (contrato de US-GW-002)

## Historia de usuario
**Como** usuario,
**quiero** que mis mensajes se envíen al backend junto con el contexto de la conversación,
**para** recibir recomendaciones coherentes con lo que ya dije.

## Contexto técnico
- Separación de responsabilidades: **servicio** (HTTP puro) → **hook** (estado y lógica) → componentes (US-FE-003).
- Archivos: `features/chat/models/chat.ts`, `services/chatService.ts`, `hooks/useChat.ts`, `index.ts` (barrel).
- Solo se llama a `POST ${API_URL}/api/chat` (el frontend nunca habla con ai-engine ni mcp-server).
- Modelos: `ChatMessage { id, role: 'user' | 'assistant', content, status? }`, `ChatRequest`, `ChatResponse { reply }`,
  `ChatErrorKind` (unión: `network | validation | rate_limited | unavailable | timeout | unknown`).
- Validación del mensaje **en el modelo** (no en el JSX): `validateMessage(text)` → trim, no vacío, ≤ 2000 caracteres.

## Criterios de aceptación
- [x] `chatService.sendMessage({ message, history }, signal)` hace `POST /api/chat` con JSON y devuelve `ChatResponse`
  validada con un *type guard* (`unknown` → `ChatResponse`; sin `any`).
- [x] Mapea errores HTTP a `ChatError` tipado: `400→validation`, `429→rate_limited`, `502/503→unavailable`,
  `504→timeout`, fallo de red/CORS→`network`, otro→`unknown`. Los mensajes visibles al usuario están en español y no exponen detalles técnicos.
- [x] Soporta cancelación con `AbortSignal` (al desmontar o al reenviar no quedan peticiones colgadas ni *state updates* tardíos).
- [x] `useChat()` devuelve `{ messages, isLoading, error, send, retry }` con tipos de retorno explícitos.
- [x] `send(text)`: valida, añade el mensaje del usuario de forma optimista, bloquea envíos concurrentes mientras `isLoading`,
  y añade la respuesta del asistente al recibirla.
- [x] El `history` enviado excluye el mensaje actual, se recorta a los **últimos 20** ítems y solo contiene `role`/`content`.
- [x] En error, el mensaje del usuario se conserva y `retry()` reenvía el último intento sin duplicarlo en el historial.
- [x] Estado inmutable (nunca se muta el array de mensajes).
- [x] Tests (Vitest, `fetch` mockeado): éxito, cada mapeo de error, validación (vacío / >2000), recorte de historial,
  cancelación, `retry`, y no-concurrencia.

## Fuera de alcance
- Componentes visuales (US-FE-003), persistencia del historial, streaming.

## Definition of Done
- Criterios marcados `[x]`; `npm run lint`, `npm test`, `npm run build` en verde.
- Cero `any`; tipos de retorno explícitos en el hook y el servicio.
- Verificado contra el gateway real o contra un mock que replica el contrato de US-GW-002.
- Plan de implementación actualizado.
