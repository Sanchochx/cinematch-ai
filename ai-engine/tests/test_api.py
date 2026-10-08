# API con agente falso: ni LLM ni mcp-server reales.
import pytest
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage, HumanMessage

from agent import LlmError
from api.routes import get_chat_service
from api.schemas import MAX_HISTORY_ITEMS, MAX_MESSAGE_LENGTH
from config import Settings, load_settings
from main import create_app
from mcp_client import McpConnectionError


class FakeService:
    def __init__(self, reply: str = "Te recomiendo Matrix.", error: Exception | None = None) -> None:
        self.reply, self.error, self.requests = reply, error, []

    async def chat(self, request):
        self.requests.append(request)
        if self.error:
            raise self.error
        return self.reply


def make_client(service: FakeService) -> TestClient:
    app = create_app(Settings())
    app.dependency_overrides[get_chat_service] = lambda: service
    # raise_server_exceptions=False: queremos ver el 500 que recibiría el gateway.
    return TestClient(app, raise_server_exceptions=False)


def test_health():
    response = TestClient(create_app(Settings())).get("/health")
    assert (response.status_code, response.json()) == (200, {"status": "ok"})


def test_chat_ok_con_historial():
    service = FakeService()
    body = {"message": " hola ", "history": [{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"}]}
    response = make_client(service).post("/chat", json=body)
    assert (response.status_code, response.json()) == (200, {"reply": "Te recomiendo Matrix."})
    assert service.requests[0].message == "hola"
    assert [item.role for item in service.requests[0].history] == ["user", "assistant"]


@pytest.mark.parametrize("body", [
    {},
    {"message": ""},
    {"message": "   "},
    {"message": 123},
    {"message": "x" * (MAX_MESSAGE_LENGTH + 1)},
    {"message": "hola", "history": [{"role": "system", "content": "x"}]},
    {"message": "hola", "history": [{"role": "user", "content": ""}]},
    {"message": "hola", "history": [{"role": "user", "content": "x"}] * (MAX_HISTORY_ITEMS + 1)},
])
def test_chat_entrada_invalida_422(body):
    service = FakeService()
    response = make_client(service).post("/chat", json=body)
    assert response.status_code == 422
    assert "detail" in response.json()
    assert service.requests == []


@pytest.mark.parametrize("error, status", [
    (McpConnectionError("http://mcp-server:8000/mcp caído"), 503),
    (LlmError("Fallo del LLM: X"), 502),
    (RuntimeError("secreto sk-123 en /app/x.py"), 500),
])
def test_errores_mapeados_y_genericos(error, status):
    response = make_client(FakeService(error=error)).post("/chat", json={"message": "hola"})
    assert response.status_code == status
    text = response.text
    assert list(response.json()) == ["detail"]
    assert not any(leak in text for leak in ("mcp-server", "sk-123", "/app", "Traceback"))


def test_no_se_loguea_el_mensaje(caplog):
    caplog.set_level("INFO", logger="ai_engine.api")
    make_client(FakeService()).post("/chat", json={"message": "mensaje-privado-xyz"})
    assert "mensaje-privado-xyz" not in caplog.text
    assert "message_chars=19" in caplog.text


def test_docs_desactivadas_por_defecto_y_activables():
    assert TestClient(create_app(Settings())).get("/docs").status_code == 404
    assert TestClient(create_app(load_settings({"ENABLE_DOCS": "true"}))).get("/docs").status_code == 200


async def test_servicio_construye_el_grafo_una_vez_y_convierte_el_historial():
    from api.schemas import ChatRequest
    from api.service import ChatService, to_messages

    builds = []

    class FakeGraph:
        async def ainvoke(self, state, config):
            return {"messages": [AIMessage("ok")]}

    async def factory():
        builds.append(1)
        return FakeGraph()

    service = ChatService(factory)
    request = ChatRequest(message="hola", history=[{"role": "assistant", "content": "x"}])
    assert await service.chat(request) == "ok" and await service.chat(request) == "ok"
    assert builds == [1]
    assert [type(m) for m in to_messages(request)] == [AIMessage, HumanMessage]


async def test_servicio_propaga_fallo_de_descubrimiento_y_reintenta():
    from api.schemas import ChatRequest
    from api.service import ChatService

    attempts = []

    async def factory():
        attempts.append(1)
        raise McpConnectionError("caído")

    service = ChatService(factory)
    for _ in range(2):
        with pytest.raises(McpConnectionError):
            await service.chat(ChatRequest(message="hola"))
    assert len(attempts) == 2
