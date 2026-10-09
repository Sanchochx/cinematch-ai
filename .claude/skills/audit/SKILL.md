---
name: audit
description: Genera un reporte de estado del proyecto (código muerto, archivos huérfanos, dependencias sin uso) sin modificar nada. Usar antes de dead-code o cleanup, o cuando se pida auditar el proyecto.
---

# Skill: Audit

## Objetivo
Generar un reporte completo del estado del proyecto antes de hacer cualquier
limpieza. No modifica nada — solo analiza y reporta. Siempre corre este
skill antes de usar dead-code o cleanup.

## Cómo activar
```
Usa el skill audit en el proyecto completo
Usa el skill audit en src/
```

## Qué analiza

### Código
- Funciones y métodos declarados pero nunca llamados
- Variables declaradas pero nunca usadas
- Imports / requires que no se usan en el archivo
- Parámetros de funciones que nunca se leen
- Bloques comentados de más de 3 líneas (posible código muerto)
- `console.log`, `print`, `debugger` de debug olvidados

### Archivos
- Archivos sin ninguna referencia desde el resto del proyecto
- Archivos con nombres como `_old`, `_backup`, `_copy`, `bak`, `tmp`
- Archivos duplicados con contenido idéntico o casi idéntico
- Carpetas vacías o con solo un `.gitkeep`

### Dependencias
- Paquetes en `package.json` (dependencies / devDependencies) no importados en ningún archivo
- Librerías en `requirements.txt` no importadas en ningún archivo `.py`
- Dependencias instaladas pero no listadas en el manifest

### Calidad general
- Archivos con más de 300 líneas (candidatos a dividir)
- Funciones con más de 40 líneas (candidatos a refactorizar)
- Archivos con TODO / FIXME sin resolver
- Rutas de API sin tests asociados

## Formato de respuesta

```
# Reporte de Audit — [Nombre del proyecto]
Fecha: [fecha]
Archivos analizados: [N]

---

## CÓDIGO MUERTO
| Tipo | Archivo | Línea | Descripción | Riesgo al eliminar |
|------|---------|-------|-------------|-------------------|
| Función | src/utils.py | 45 | `formatear_fecha()` sin llamadas | BAJO |
| Import | src/api/users.js | 3 | `lodash` importado, no usado | BAJO |
| Variable | src/models/invoice.py | 12 | `TAX_OLD = 0.16` sin uso | BAJO |

## ARCHIVOS SOSPECHOSOS
| Archivo | Razón | Acción sugerida |
|---------|-------|-----------------|
| src/utils_old.py | Nombre indica versión vieja | Verificar y eliminar |
| src/temp.js | Sin referencias | Verificar y eliminar |

## DEPENDENCIAS SIN USO
| Paquete | Archivo | Acción sugerida |
|---------|---------|-----------------|
| moment | package.json | Desinstalar si no se usa |
| requests | requirements.txt | Verificar antes de eliminar |

## ARCHIVOS GRANDES (candidatos a dividir)
| Archivo | Líneas | Sugerencia |
|---------|--------|------------|
| src/api/routes.js | 450 | Dividir por módulo |

## TODOs SIN RESOLVER
| Archivo | Línea | Comentario |
|---------|-------|------------|
| src/services/auth.py | 78 | TODO: implementar refresh token |

---

## RESUMEN
- Código muerto encontrado: [N items]
- Archivos sospechosos: [N]
- Dependencias sin uso: [N]
- TODOs pendientes: [N]

## PRÓXIMOS PASOS SUGERIDOS
1. Revisar la tabla de código muerto y confirmar cuáles eliminar
2. Correr: `Usa el skill dead-code en src/` para eliminar lo confirmado
3. Correr: `Usa el skill cleanup en el proyecto` para limpiar archivos y deps
```

## Reglas importantes
- NO modificar ningún archivo durante el audit
- Si una función parece sin uso pero tiene nombre genérico (ej: `handle`, `process`),
  marcarla como riesgo MEDIO — puede estar siendo llamada dinámicamente
- Marcar como riesgo ALTO todo lo relacionado con auth, pagos o seguridad
- Incluir siempre el número de línea para facilitar la verificación manual
