# claude-project-template

Plantilla base para proyectos con Claude Code. Incluye estructura de memoria, skills reutilizables y hooks de validación que se adaptan automáticamente al stack del proyecto (Python, Node.js, Go, Rust, Java, .NET, Ruby, PHP u otros vía configuración).

## Uso rápido

```bash
# Clonar el template
git clone https://github.com/TU_USUARIO/claude-project-template.git mi-proyecto
cd mi-proyecto

# Desconectar del template y conectar a tu repo
rm -rf .git
git init
git remote add origin https://github.com/TU_USUARIO/mi-proyecto.git

# Hacer el hook ejecutable (Linux/Mac; en Windows usa Git Bash o WSL)
chmod +x .claude/hooks/pre-commit.sh
```

Luego edita `.claude/CLAUDE.md` con el contexto de tu proyecto y ya puedes usar Claude Code. El hook de pre-commit ya viene registrado en `settings.json` y detecta tu stack automáticamente, sin configuración adicional.

**Requisitos del hook**: `bash` y `git`. `jq` es opcional (mejora el parseo del comando).

## Qué incluye

```
claude-project-template/
└── .claude/
    ├── CLAUDE.md                      ← memoria principal (editar por proyecto)
    ├── settings.json                  ← configuración compartida (hooks)
    ├── settings.local.json            ← permisos locales, no versionar cambios aquí a la ligera
    ├── docs/
    │   ├── architecture.md            ← plantilla de arquitectura
    │   └── decisions/                 ← registro de decisiones (ADRs)
    ├── context/
    │   ├── IMPLEMENTATION_PLAN.md     ← plantilla de plan por épicas/historias de usuario
    │   └── TASK_EXECUTION.md          ← workflow de ejecución paso a paso para la IA
    ├── hooks/
    │   └── pre-commit.sh              ← tests + lint (autodetecta el stack) antes de commitear
    ├── commands/
    │   └── frontend.md                ← comando /frontend para construir UI
    └── skills/
        ├── audit/SKILL.md             ← reporte de estado antes de limpiar
        ├── cleanup/SKILL.md           ← limpieza de archivos y dependencias
        ├── code-review/SKILL.md       ← revisión de código
        ├── dead-code/SKILL.md         ← eliminar código muerto dentro de archivos
        ├── new-endpoint/SKILL.md      ← crear endpoints completos
        ├── write-tests/SKILL.md       ← generar tests
        └── refactor/SKILL.md          ← refactorizar código
```

## Skills disponibles

### Audit
```
Usa el skill audit en el proyecto completo
```
Genera un reporte de estado (código muerto, archivos huérfanos, etc.) sin modificar nada. Correr siempre antes de `dead-code` o `cleanup`.

### Dead code
```
Usa el skill dead-code en src/services/users.py
```
Elimina código que definitivamente no se usa dentro de archivos, basándose en el reporte de `audit`.

### Cleanup
```
Usa el skill cleanup en el proyecto completo
```
Limpia archivos y dependencias completas que ya no se usan. Complementa a `dead-code`.

### Code review
```
Usa el skill code-review en src/api/users.py
```
Revisa seguridad, calidad, tests y estructura. Devuelve APROBADO/RECHAZADO con lista de issues por severidad.

### Nuevo endpoint
```
Usa el skill new-endpoint para crear POST /api/invoices que registre una factura
```
Genera modelo → servicio → ruta → test siguiendo las convenciones del proyecto.

### Escribir tests
```
Usa el skill write-tests para src/services/invoice_service.py
```
Genera casos feliz, datos inválidos, casos límite y mocks para servicios externos.

### Refactorizar
```
Usa el skill refactor en src/api/orders.py
```
Identifica problemas (funciones largas, duplicación, N+1, magic numbers) y refactoriza sin cambiar el comportamiento.

## Comandos disponibles

### /frontend
```
/frontend crea un componente de listado de facturas con paginación
```
Construye un componente o página frontend (Angular/React/Vue) siguiendo estándares de accesibilidad, performance y tipado estricto.

## Hook pre-commit

El hook es agnóstico de tecnología: detecta los stacks presentes por sus archivos marcadores y corre tests y lint con las herramientas que tengas instaladas (si falta una herramienta, la omite).

| Stack | Detectado por | Checks |
|---|---|---|
| Python | `requirements*.txt`, `pyproject.toml`, `setup.py`, `Pipfile` | pytest, ruff / flake8 |
| Node.js / TS | `package.json` (npm, pnpm, yarn o bun según el lockfile) | scripts `test` y `lint`, `tsc --noEmit` |
| Go | `go.mod` | `go test`, `go vet` |
| Rust | `Cargo.toml` | `cargo test`, `cargo clippy` |
| Java / Kotlin | `pom.xml`, `build.gradle(.kts)` | `mvn test` / `gradle test` |
| .NET | `*.sln`, `*.csproj` | `dotnet test` |
| Ruby | `Gemfile` | rspec / rake test, rubocop |
| PHP | `composer.json` | phpunit |

Además, en cualquier lenguaje, revisa las líneas **añadidas** en el commit buscando credenciales hardcodeadas (passwords, API keys, claves privadas, tokens de AWS/GitHub).

Se activa cada vez que Claude intenta hacer un commit (registrado en `settings.json`).

### Personalización

- **Otro stack o comandos propios**: exporta `HOOK_TEST_CMD` y/o `HOOK_LINT_CMD` (reemplazan la autodetección).
- **Desactivar un stack**: `HOOK_SKIP_STACKS="node python"` (valores: `python node go rust java dotnet ruby php`).
- **Checks extra**: crea `.claude/hooks/project-checks.sh`; si existe, se ejecuta siempre y un exit distinto de 0 bloquea el commit.

## Adaptar a tu proyecto

1. **Editar `.claude/CLAUDE.md`** — cambiar nombre, stack, comandos, convenciones específicas
2. **Editar `.claude/docs/architecture.md`** — documentar tu arquitectura real
3. **Completar `.claude/context/IMPLEMENTATION_PLAN.md`** — definir épicas e historias de usuario reales
4. **Agregar skills propios** — crear carpetas en `.claude/skills/tu-skill/SKILL.md`
5. **Ajustar el hook** — normalmente no hace falta editarlo: usa las variables `HOOK_*` o `project-checks.sh` (ver [Personalización](#personalización))

## Stack soportado por los skills

El hook de pre-commit funciona con cualquier stack (ver tabla arriba). Los skills y ejemplos de esta plantilla están pensados, por defecto, para:

| Tecnología | Code review | Endpoints | Tests | Refactor |
|---|---|---|---|---|
| Python / Flask | ✓ | ✓ | pytest | ✓ |
| Node.js / Express | ✓ | ✓ | Jest | ✓ |
| PostgreSQL | ✓ | ✓ | — | ✓ |
| MySQL | ✓ | ✓ | — | ✓ |

---

Hecho por [Tu nombre] · Basado en la metodología de Claude Code Project Structure
