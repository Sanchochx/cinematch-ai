"""Tools MCP de solo lectura sobre el catálogo de películas."""

from mcp.types import ToolAnnotations

# Todas las tools consultan datos y nunca modifican nada, ni en TMDB ni en el servidor.
READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=True)
