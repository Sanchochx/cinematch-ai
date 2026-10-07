# mcp-server

Servidor MCP de CineMatch AI: expone tools de solo lectura sobre la API de TMDB al agente del
`ai-engine`. Arquitectura general en [`.claude/docs/architecture.md`](../.claude/docs/architecture.md).

## Dependencias
- `requirements.txt` — runtime (lo que instala la imagen Docker):
  - `mcp>=1.30,<2` — SDK oficial de MCP. Se fija la rama **1.x** porque la 2.x renombró `FastMCP`
    a `MCPServer` y cambió otras APIs; migrar es una decisión aparte.
  - `httpx>=0.28,<1` — cliente HTTP async hacia TMDB.
- `requirements-dev.txt` — runtime + `pytest`, `pytest-asyncio` y `respx` (mock de `httpx`).

## Entorno local (Python 3.11)
```bash
cd mcp-server && python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt && python -c "import mcp, httpx"
pytest tests/ -v
```

Sin Python 3.11 en el host, la misma verificación en un contenedor desechable:
```bash
docker run --rm -v "$PWD/mcp-server":/src:ro python:3.11-slim sh -c \
  "python -m venv /tmp/venv && . /tmp/venv/bin/activate && \
   pip install -q -r /src/requirements-dev.txt && pip check && \
   python -c 'import mcp, httpx' && cd /src && pytest -p no:cacheprovider"
```

Los tests nunca llaman a TMDB real: las peticiones se mockean con `respx`. `pytest.ini` activa
`asyncio_mode = auto`, así que los tests `async def` no necesitan decorador.
