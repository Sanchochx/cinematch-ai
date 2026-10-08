class LlmError(Exception):
    """Fallo del proveedor de LLM (auth, rate limit, timeout...). El mensaje nunca incluye secretos."""
