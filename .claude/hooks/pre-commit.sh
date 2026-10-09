#!/bin/bash
# .claude/hooks/pre-commit.sh
# Se ejecuta en cada PreToolUse de Bash en Claude Code.
# Solo actúa cuando el comando es un git commit.
#
# Agnóstico de tecnología: detecta los stacks presentes por sus archivos
# marcadores y corre tests + lint con las herramientas que estén instaladas.
# Para stacks no cubiertos o comandos propios, ver "Personalización" en el README:
#   - Variables de entorno: HOOK_TEST_CMD, HOOK_LINT_CMD, HOOK_SKIP_STACKS
#   - Script opcional: .claude/hooks/project-checks.sh (exit != 0 = falla)

INPUT=$(cat)

# Extraer el comando del JSON (jq si existe; si no, fallback con sed)
if command -v jq &> /dev/null; then
  COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
else
  COMMAND=$(echo "$INPUT" | sed -n 's/.*"command"[[:space:]]*:[[:space:]]*"\(\([^"\\]\|\\.\)*\)".*/\1/p' | head -1)
fi
if ! echo "$COMMAND" | grep -Eq '(^|[;&|[:space:]])git[[:space:]]+commit'; then
  exit 0
fi

# Ejecutar desde la raíz del repo
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" || exit 0

echo ""
echo "======================================="
echo "  Checks pre-commit"
echo "======================================="

ERRORS=0
DETECTED=0

has_file() { # has_file patrón...  (admite globs)
  local f
  for f in "$@"; do compgen -G "$f" > /dev/null && return 0; done
  return 1
}

stack_enabled() { [[ " $HOOK_SKIP_STACKS " != *" $1 "* ]]; }

# run_check "<etiqueta>" <comando...>
run_check() {
  local label="$1"; shift
  echo "  $label..."
  if "$@" 2>&1; then
    echo "  ✓ $label OK"
  else
    echo "  ✗ $label falló"
    ERRORS=$((ERRORS + 1))
  fi
}

# run_sh "<etiqueta>" "<comando como string>"  (para comandos del usuario)
run_sh() { run_check "$1" bash -c "$2"; }

begin_stack() { DETECTED=$((DETECTED + 1)); echo ""; echo "▶ Stack detectado: $1"; }

# ─── Comandos definidos por el usuario (reemplazan a la autodetección) ───
if [ -n "$HOOK_TEST_CMD" ] || [ -n "$HOOK_LINT_CMD" ]; then
  begin_stack "personalizado"
  [ -n "$HOOK_TEST_CMD" ] && run_sh "Tests" "$HOOK_TEST_CMD"
  [ -n "$HOOK_LINT_CMD" ] && run_sh "Lint" "$HOOK_LINT_CMD"
else
  # ─── Python ─────────────────────────────────────────────────
  if stack_enabled python && has_file requirements*.txt setup.py setup.cfg pyproject.toml Pipfile; then
    begin_stack "Python"
    if command -v pytest &> /dev/null && has_file tests test "test_*.py" "*_test.py"; then
      run_check "Tests (pytest)" pytest -q --tb=short
    fi
    if command -v ruff &> /dev/null; then
      run_check "Lint (ruff)" ruff check .
    elif command -v flake8 &> /dev/null; then
      run_check "Lint (flake8)" flake8 . --max-line-length=100 --exclude=venv,.venv,migrations
    fi
  fi

  # ─── Node.js / TypeScript ───────────────────────────────────
  if stack_enabled node && [ -f package.json ]; then
    begin_stack "Node.js"
    PM=npm
    [ -f pnpm-lock.yaml ] && PM=pnpm
    [ -f yarn.lock ] && PM=yarn
    [ -f bun.lockb ] || [ -f bun.lock ] && PM=bun
    if command -v "$PM" &> /dev/null; then
      # Respeta los scripts del proyecto: así sirve para Express, React, Angular, etc.
      if grep -q '"test"[[:space:]]*:' package.json && ! grep -q 'no test specified' package.json; then
        run_check "Tests ($PM test)" "$PM" run test
      fi
      if grep -q '"lint"[[:space:]]*:' package.json; then
        run_check "Lint ($PM run lint)" "$PM" run lint
      fi
      if [ -f tsconfig.json ] && [ -x node_modules/.bin/tsc ]; then
        run_check "Tipos (tsc)" node_modules/.bin/tsc --noEmit
      fi
    fi
  fi

  # ─── Go ─────────────────────────────────────────────────────
  if stack_enabled go && [ -f go.mod ] && command -v go &> /dev/null; then
    begin_stack "Go"
    run_check "Tests (go test)" go test ./...
    run_check "Análisis (go vet)" go vet ./...
  fi

  # ─── Rust ───────────────────────────────────────────────────
  if stack_enabled rust && [ -f Cargo.toml ] && command -v cargo &> /dev/null; then
    begin_stack "Rust"
    run_check "Tests (cargo test)" cargo test --quiet
    run_check "Lint (cargo clippy)" cargo clippy --quiet -- -D warnings
  fi

  # ─── Java / Kotlin ──────────────────────────────────────────
  if stack_enabled java; then
    if [ -f pom.xml ] && command -v mvn &> /dev/null; then
      begin_stack "Java (Maven)"
      run_check "Tests (mvn test)" mvn -q test
    elif has_file build.gradle build.gradle.kts; then
      GRADLE=gradle
      [ -x ./gradlew ] && GRADLE=./gradlew
      if command -v "$GRADLE" &> /dev/null || [ -x ./gradlew ]; then
        begin_stack "Java/Kotlin (Gradle)"
        run_check "Tests (gradle test)" "$GRADLE" -q test
      fi
    fi
  fi

  # ─── .NET ───────────────────────────────────────────────────
  if stack_enabled dotnet && has_file "*.sln" "*.csproj" "*.fsproj" && command -v dotnet &> /dev/null; then
    begin_stack ".NET"
    run_check "Tests (dotnet test)" dotnet test --nologo -v q
  fi

  # ─── Ruby ───────────────────────────────────────────────────
  if stack_enabled ruby && [ -f Gemfile ] && command -v bundle &> /dev/null; then
    begin_stack "Ruby"
    if [ -d spec ]; then
      run_check "Tests (rspec)" bundle exec rspec
    elif [ -d test ]; then
      run_check "Tests (rake test)" bundle exec rake test
    fi
    [ -f .rubocop.yml ] && run_check "Lint (rubocop)" bundle exec rubocop
  fi

  # ─── PHP ────────────────────────────────────────────────────
  if stack_enabled php && [ -f composer.json ]; then
    begin_stack "PHP"
    if [ -x vendor/bin/phpunit ]; then
      run_check "Tests (phpunit)" vendor/bin/phpunit
    fi
  fi
fi

# ─── Script propio del proyecto (opcional) ───────────────────
if [ -f .claude/hooks/project-checks.sh ]; then
  begin_stack "checks del proyecto"
  run_check "project-checks.sh" bash .claude/hooks/project-checks.sh
fi

if [ "$DETECTED" -eq 0 ]; then
  echo ""
  echo "▶ Ningún stack reconocido — se omiten tests y lint."
  echo "  (Define HOOK_TEST_CMD / HOOK_LINT_CMD o .claude/hooks/project-checks.sh)"
fi

# ─── Credenciales hardcodeadas (cualquier lenguaje) ──────────
# Revisa solo las líneas AÑADIDAS en el commit, ignorando tests/ejemplos.
echo ""
echo "▶ Buscando credenciales hardcodeadas en cambios staged..."
SECRET_RE="(password|passwd|secret|api[_-]?key|access[_-]?key|auth[_-]?token|private[_-]?key)[\"']?[[:space:]]*[:=][[:space:]]*[\"'][^\"'\$\{][^\"']{3,}[\"']|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{36,}"
LEAKS=$(git diff --cached -U0 --no-color \
  -- . ':!*test*' ':!*spec*' ':!*example*' ':!*sample*' ':!*.md' ':!*.lock' ':!*lock.json' \
  2>/dev/null | grep -E '^\+[^+]' | grep -Eiv 'os\.environ|process\.env|getenv|\$\{' | grep -Ei "$SECRET_RE")
if [ -n "$LEAKS" ]; then
  echo "$LEAKS" | cut -c1-160
  echo "  ✗ Posibles credenciales hardcodeadas (usa variables de entorno)"
  ERRORS=$((ERRORS + 1))
else
  echo "  ✓ Sin credenciales hardcodeadas"
fi

# ─── Resultado final ─────────────────────────────────────────
echo ""
echo "======================================="
if [ $ERRORS -eq 0 ]; then
  echo "  ✓ Todo OK — procediendo con el commit"
  echo "======================================="
  echo ""
  exit 0
else
  echo "  ✗ $ERRORS problema(s) encontrado(s)"
  echo "  Corrige los errores antes de commitear."
  echo "======================================="
  echo ""
  exit 2
fi
