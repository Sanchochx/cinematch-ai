---
name: dead-code
description: Elimina código no usado dentro de archivos (funciones, imports, variables) según el reporte de audit, sin borrar archivos ni dependencias. Usar cuando se pida quitar código muerto.
---

# Skill: Dead Code

## Objetivo
Eliminar código que definitivamente no se usa, basándose en el reporte
previo del skill audit. Opera solo sobre código dentro de archivos —
no elimina archivos completos ni dependencias (eso es tarea de cleanup).

## Prerequisito
Correr primero el skill audit y revisar su reporte antes de usar este skill.

## Cómo activar
```
Usa el skill dead-code en [archivo o carpeta]
Usa el skill dead-code en src/services/users.py
Usa el skill dead-code en src/
```

## Qué elimina (riesgo BAJO por defecto)

### Siempre seguro eliminar
- Imports / requires declarados pero no usados en ese archivo
- Variables locales asignadas pero nunca leídas
- Parámetros de funciones privadas nunca usados
- Bloques de código comentado de más de 3 líneas sin explicación
- `console.log()`, `console.debug()`, `print()`, `debugger` de debug

### Eliminar con confirmación previa
- Funciones privadas (prefijo `_` en Python, no exportadas en JS) sin llamadas detectadas
- Constantes definidas pero sin uso
- Clases sin instancias ni herencia detectada

### Nunca eliminar sin aprobación explícita
- Funciones exportadas / públicas (pueden usarse desde fuera del proyecto)
- Cualquier cosa relacionada con auth, seguridad o pagos
- Código con comentarios que expliquen por qué está ahí
- Funciones con nombres genéricos que podrían llamarse dinámicamente
- Anything marcado como riesgo ALTO o MEDIO en el audit

## Proceso

1. Leer el reporte del audit (o hacer un análisis rápido si no existe)
2. Listar exactamente qué va a eliminar antes de hacerlo
3. Pedir confirmación para items de riesgo MEDIO
4. Eliminar solo los de riesgo BAJO sin preguntar
5. Verificar que el proyecto sigue funcionando después de cada eliminación

## Formato de respuesta

```
## Dead Code — Plan de eliminación
Basado en: audit del [fecha] / análisis nuevo

### Eliminaré automáticamente (riesgo BAJO):
- [ ] `src/utils.py:45` — función `formatear_fecha_old()` sin llamadas
- [ ] `src/api/users.js:3` — import `lodash` sin uso
- [ ] `src/models/invoice.py:78` — `console.log('debug invoice')` olvidado

### Necesito confirmación (riesgo MEDIO):
- [ ] `src/services/auth.py:102` — función `_legacy_hash()` sin llamadas detectadas
      ¿Confirmas eliminar? Puede estar siendo llamada dinámicamente.

---
[después de confirmación]

### Eliminado:
- ✓ `src/utils.py:45` — `formatear_fecha_old()` eliminada
- ✓ `src/api/users.js:3` — import `lodash` eliminado

### Tests después de limpieza:
[correr tests para confirmar que nada se rompió]

### Resultado: [N] items eliminados, [N] líneas menos
```

## Reglas
- Siempre mostrar el plan antes de ejecutar
- Nunca eliminar más de lo que está en el plan confirmado
- Si los tests fallan después de eliminar algo, revertir ese cambio específico
- Documentar en un comentario git qué se eliminó y por qué
