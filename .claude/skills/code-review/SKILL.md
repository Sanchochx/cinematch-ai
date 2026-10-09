---
name: code-review
description: Revisa código (seguridad, calidad, tests, estructura) y devuelve APROBADO/RECHAZADO con issues por severidad. Usar antes de hacer merge o cuando se pida revisar un archivo o carpeta.
---

# Skill: Code Review

## Objetivo
Revisar código antes de hacer merge o subir a producción. Aplica para Python/Flask y Node.js/Express.

## Cómo activar
```
Usa el skill code-review en [archivo o carpeta]
```

## Checklist general

### Seguridad
- [ ] No hay credenciales hardcodeadas
- [ ] Los inputs del usuario se validan antes de usarlos
- [ ] Los queries usan parámetros (no concatenación de strings)
- [ ] Los endpoints protegidos verifican autenticación/autorización

### Calidad de código
- [ ] Las funciones hacen una sola cosa
- [ ] Los nombres son descriptivos y en inglés
- [ ] No hay código comentado sin explicación
- [ ] No hay `print()` o `console.log()` de debug olvidados
- [ ] El manejo de errores es explícito (no `except: pass`)

### Base de datos
- [ ] Las queries están optimizadas (evitar N+1)
- [ ] Se usa transacción donde se necesita consistencia
- [ ] Los índices necesarios están definidos en el modelo

### Tests
- [ ] Existe al menos un test para la funcionalidad nueva
- [ ] Los casos edge están cubiertos (vacío, null, límites)
- [ ] Los tests son independientes entre sí

### API / Endpoints
- [ ] Los códigos HTTP son correctos (200, 201, 400, 401, 404, 500)
- [ ] Las respuestas tienen estructura consistente
- [ ] Los errores devuelven mensajes útiles (no stack traces)

## Formato de respuesta

```
RESULTADO: APROBADO / RECHAZADO / APROBADO CON OBSERVACIONES

PROBLEMAS CRÍTICOS (bloquean el merge):
- [descripción + línea + sugerencia de fix]

ADVERTENCIAS (revisar pronto):
- [descripción + línea + sugerencia]

SUGERENCIAS (mejoras opcionales):
- [descripción + línea]

RESUMEN: [2-3 líneas con lo más importante]
```

## Notas
- Un CRÍTICO es suficiente para rechazar el PR
- Siempre incluir el número de línea cuando sea posible
- Si el archivo tiene más de 300 líneas, revisar por secciones
