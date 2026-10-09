---
name: cleanup
description: Elimina archivos completos y dependencias que ya no se usan, basándose en el reporte de audit. Usar cuando se pida limpiar el proyecto a nivel de archivos o dependencias.
---

# Skill: Cleanup

## Objetivo
Limpiar el proyecto a nivel de archivos y dependencias. Complementa al
skill dead-code que limpia dentro de archivos. Este skill elimina archivos
completos innecesarios y dependencias no usadas.

## Prerequisito
Correr primero el skill audit. No usar este skill sin haber revisado
el reporte previo.

## Cómo activar
```
Usa el skill cleanup en el proyecto completo
Usa el skill cleanup enfocándote en dependencias
Usa el skill cleanup enfocándote en archivos
```

## Qué limpia

### Archivos (con confirmación siempre)
- Archivos con nombre `*_old.*`, `*_backup.*`, `*_copy.*`, `*.bak`, `*.tmp`
- Archivos de configuración duplicados (ej: dos `.env.example` en distintas rutas)
- Archivos generados automáticamente que deberían estar en `.gitignore`
  (`__pycache__/`, `node_modules/`, `*.pyc`, `dist/`, `build/`)
- Carpetas completamente vacías
- Logs y archivos temporales commiteados por error

### Dependencias — Python
```bash
# Detectar dependencias sin uso
pip install pipreqs
pipreqs . --print   # muestra solo las realmente usadas

# Comparar con requirements.txt actual
# Las que están en requirements.txt pero no en pipreqs → candidatas a eliminar
```

### Dependencias — Node.js
```bash
# Detectar dependencias sin uso
npx depcheck

# Resultado muestra:
# Unused dependencies: [lista]
# Unused devDependencies: [lista]
# Missing dependencies: [lista]
```

### .gitignore
- Verificar que los archivos/carpetas generadas están en `.gitignore`
- Agregar entradas faltantes comunes según el stack detectado

## Proceso

1. Listar todo lo que se va a eliminar o modificar
2. Confirmar con el usuario antes de cualquier eliminación de archivos
3. Para dependencias: mostrar el comando a correr, ejecutarlo, mostrar resultado
4. Actualizar `.gitignore` si es necesario
5. Verificar que el proyecto sigue corriendo después de la limpieza

## Formato de respuesta

```
## Cleanup — Plan completo

### Archivos a eliminar (requieren confirmación):
- [ ] `src/utils_old.py` — versión antigua de utils.py (127 líneas)
- [ ] `config/database_backup.js` — backup manual del 2024-11-03
- [ ] `notes.txt` — notas personales en la raíz del proyecto

### Dependencias sin uso detectadas:

Python (pipreqs):
- [ ] `moment` en requirements.txt — no importado en ningún .py
- [ ] `xlrd` en requirements.txt — no importado en ningún .py

Node.js (depcheck):
- [ ] `underscore` en dependencies — no requerido en ningún .js
- [ ] `mocha` en devDependencies — proyecto usa Jest

### .gitignore — entradas faltantes sugeridas:
- `.env.local`
- `*.log`
- `coverage/`

---
[después de confirmación]

### Ejecutado:
- ✓ Archivos eliminados: [N]
- ✓ Dependencias removidas: pip uninstall moment xlrd / npm uninstall underscore
- ✓ .gitignore actualizado

### Estado final:
- Archivos eliminados: [N]
- Dependencias removidas: [N]
- Tamaño del proyecto antes: [X MB] → después: [Y MB]
```

## Reglas críticas
- Nunca eliminar `node_modules/` o `venv/` si no están en `.gitignore` — primero agregarlos ahí
- Nunca desinstalar dependencias de producción sin confirmar que el proyecto corre después
- Si hay duda sobre un archivo, NO eliminarlo — marcarlo como "revisar manualmente"
- Siempre hacer un commit limpio antes de correr cleanup para poder revertir fácilmente
- Los archivos `.env` reales nunca se eliminan — solo los `.env.example` duplicados
