import json

import httpx
import pytest
from mcp.shared.memory import create_connected_server_and_client_session

from config import Settings
from providers.mock import MockProvider
from server import create_server

GENRES_JSON = {
    "genres": [
        {"id": 28, "name": "Acción"},
        {"id": 878, "name": "Ciencia ficción"},
        {"id": 27, "name": "Terror"},
    ]
}


def tmdb_item(movie_id: int, title: str, genre_ids: list[int], release_date: str = "2014-11-05") -> dict:
    return {
        "id": movie_id,
        "title": title,
        "release_date": release_date,
        "overview": f"Sinopsis de {title}",
        "genre_ids": genre_ids,
        "vote_average": 8.4,
        "poster_path": "/poster.jpg",
    }


INTERSTELLAR = tmdb_item(157336, "Interstellar", [12, 18, 878])
MAD_MAX = tmdb_item(76341, "Mad Max", [28, 878], "2015-05-13")
GLADIATOR = tmdb_item(98, "Gladiator", [28, 18], "")


async def call_search(provider, arguments: dict | None = None):
    mcp = create_server(Settings(), provider)
    async with create_connected_server_and_client_session(mcp) as client:
        return await client.call_tool("search_movies", arguments or {})


def payload(result) -> dict:
    assert not result.isError, result.content
    return json.loads(result.content[0].text)


@pytest.fixture
def genres_route(tmdb_mock):
    return tmdb_mock.get("/genre/movie/list").respond(200, json=GENRES_JSON)


async def test_tool_is_listed_with_schema_and_description(tmdb_provider):
    mcp = create_server(Settings(), tmdb_provider)
    async with create_connected_server_and_client_session(mcp) as client:
        tools = {tool.name: tool for tool in (await client.list_tools()).tools}

    tool = tools["search_movies"]
    assert "género" in tool.description and "palabra clave" in tool.description
    schema = tool.inputSchema
    assert set(schema["properties"]) == {"genre", "keyword", "limit"}
    assert "required" not in schema
    assert schema["properties"]["limit"]["minimum"] == 1
    assert schema["properties"]["limit"]["maximum"] == 20
    assert schema["properties"]["keyword"]["anyOf"][0]["maxLength"] == 100


async def test_keyword_only_uses_search_and_respects_limit(tmdb_mock, tmdb_provider, genres_route):
    route = tmdb_mock.get("/search/movie").respond(200, json={"results": [INTERSTELLAR, MAD_MAX]})

    data = payload(await call_search(tmdb_provider, {"keyword": "espacio", "limit": 1}))

    assert route.calls.last.request.url.params["query"] == "espacio"
    assert data["source"] == "tmdb"
    assert [m["title"] for m in data["results"]] == ["Interstellar"]


async def test_genre_only_resolves_id_and_uses_discover(tmdb_mock, tmdb_provider, genres_route):
    route = tmdb_mock.get("/discover/movie").respond(200, json={"results": [MAD_MAX]})

    data = payload(await call_search(tmdb_provider, {"genre": "ciencia ficción"}))

    params = route.calls.last.request.url.params
    assert params["with_genres"] == "878"
    assert params["sort_by"] == "popularity.desc"
    assert [m["id"] for m in data["results"]] == [76341]


async def test_genre_and_keyword_search_then_filter_by_genre(tmdb_mock, tmdb_provider, genres_route):
    tmdb_mock.get("/search/movie").respond(200, json={"results": [GLADIATOR, INTERSTELLAR, MAD_MAX]})
    discover = tmdb_mock.get("/discover/movie")

    data = payload(await call_search(tmdb_provider, {"genre": "Science Fiction", "keyword": "x"}))

    assert [m["title"] for m in data["results"]] == ["Interstellar", "Mad Max"]
    assert not discover.called


async def test_no_parameters_returns_popular_movies(tmdb_mock, tmdb_provider, genres_route):
    route = tmdb_mock.get("/movie/popular").respond(200, json={"results": [MAD_MAX]})

    data = payload(await call_search(tmdb_provider))

    assert route.called
    assert len(data["results"]) == 1


async def test_results_are_normalized(tmdb_mock, tmdb_provider, genres_route):
    # 12 y 18 no están en el mapa de géneros devuelto por TMDB: se omiten, no rompen.
    tmdb_mock.get("/movie/popular").respond(200, json={"results": [INTERSTELLAR, GLADIATOR]})

    data = payload(await call_search(tmdb_provider))

    assert data["results"][0] == {
        "id": 157336,
        "title": "Interstellar",
        "release_year": 2014,
        "overview": "Sinopsis de Interstellar",
        "genres": ["Ciencia ficción"],
        "vote_average": 8.4,
        "poster_path": "/poster.jpg",
    }
    assert data["results"][1]["release_year"] is None
    assert data["results"][1]["genres"] == ["Acción"]


@pytest.mark.parametrize("name", ["TERROR", "terror", "Horror", " horror "])
async def test_genre_matching_ignores_case_and_accepts_both_languages(tmdb_mock, tmdb_provider, genres_route, name):
    route = tmdb_mock.get("/discover/movie").respond(200, json={"results": []})

    payload(await call_search(tmdb_provider, {"genre": name}))

    assert route.calls.last.request.url.params["with_genres"] == "27"


async def test_genre_matching_ignores_accents(tmdb_mock, tmdb_provider, genres_route):
    route = tmdb_mock.get("/discover/movie").respond(200, json={"results": []})

    payload(await call_search(tmdb_provider, {"genre": "accion"}))
    payload(await call_search(tmdb_provider, {"genre": "CIENCIA FICCION"}))

    assert [c.request.url.params["with_genres"] for c in route.calls] == ["28", "878"]


async def test_genres_list_is_fetched_once(tmdb_mock, tmdb_provider, genres_route):
    tmdb_mock.get("/discover/movie").respond(200, json={"results": []})

    await call_search(tmdb_provider, {"genre": "terror"})
    await call_search(tmdb_provider, {"genre": "acción"})

    assert genres_route.call_count == 1


async def test_unknown_genre_lists_valid_ones_without_calling_discover(tmdb_mock, tmdb_provider, genres_route):
    discover = tmdb_mock.get("/discover/movie")
    search = tmdb_mock.get("/search/movie")

    result = await call_search(tmdb_provider, {"genre": "telenovela", "keyword": "amor"})

    assert result.isError
    text = result.content[0].text
    assert "telenovela" in text
    assert "Acción" in text and "Ciencia ficción" in text and "Terror" in text
    assert not discover.called and not search.called


@pytest.mark.parametrize(
    "arguments",
    [
        {"limit": 0},
        {"limit": 21},
        {"limit": -3},
        {"keyword": ""},
        {"keyword": "   "},
        {"keyword": "a" * 101},
        {"genre": "  "},
    ],
)
async def test_invalid_arguments_are_rejected_before_calling_tmdb(tmdb_mock, tmdb_provider, arguments):
    result = await call_search(tmdb_provider, arguments)

    assert result.isError
    assert not any(route.called for route in tmdb_mock.routes)


async def test_keyword_of_exactly_100_chars_and_limit_bounds_are_valid(tmdb_mock, tmdb_provider, genres_route):
    tmdb_mock.get("/search/movie").respond(200, json={"results": [INTERSTELLAR]})
    tmdb_mock.get("/movie/popular").respond(200, json={"results": [INTERSTELLAR]})

    for arguments in ({"keyword": "a" * 100}, {"limit": 1}, {"limit": 20}):
        payload(await call_search(tmdb_provider, arguments))


async def test_no_results_is_not_an_error(tmdb_mock, tmdb_provider, genres_route):
    tmdb_mock.get("/search/movie").respond(200, json={"results": []})

    data = payload(await call_search(tmdb_provider, {"keyword": "zzzz"}))

    assert data == {"source": "tmdb", "results": []}


@pytest.mark.parametrize(
    ("response", "expected"),
    [
        (httpx.Response(429, headers={"Retry-After": "3"}), "reintenta en 3 s"),
        (httpx.Response(500), "TMDB no está disponible"),
        (httpx.Response(503), "TMDB no está disponible"),
    ],
)
async def test_tmdb_failures_become_readable_tool_errors(tmdb_mock, tmdb_provider, genres_route, response, expected):
    tmdb_mock.get("/search/movie").mock(return_value=response)

    result = await call_search(tmdb_provider, {"keyword": "matrix"})

    assert result.isError
    assert expected in result.content[0].text
    assert "api_key" not in result.content[0].text


async def test_genre_list_failure_is_a_tool_error(tmdb_mock, tmdb_provider):
    tmdb_mock.get("/genre/movie/list").respond(429)

    result = await call_search(tmdb_provider, {"keyword": "matrix"})

    assert result.isError
    assert "Límite de peticiones" in result.content[0].text


# --- modo mock -----------------------------------------------------------------------------


async def test_mock_mode_without_filters_returns_catalog_top_rated():
    data = payload(await call_search(MockProvider()))

    assert data["source"] == "mock"
    assert len(data["results"]) == 10
    ratings = [m["vote_average"] for m in data["results"]]
    assert ratings == sorted(ratings, reverse=True)


async def test_mock_mode_filters_by_genre_in_either_language():
    spanish = payload(await call_search(MockProvider(), {"genre": "Ciencia Ficción"}))
    english = payload(await call_search(MockProvider(), {"genre": "science fiction"}))

    assert spanish == english
    assert {m["title"] for m in spanish["results"]} == {"Interstellar", "Mad Max: Furia en la carretera"}
    assert all("Ciencia ficción" in m["genres"] for m in spanish["results"])


async def test_mock_mode_filters_by_keyword_ignoring_accents():
    data = payload(await call_search(MockProvider(), {"keyword": "DEJAME"}))

    assert [m["title"] for m in data["results"]] == ["Déjame salir"]


async def test_mock_mode_combines_genre_and_keyword_and_applies_limit():
    both = payload(await call_search(MockProvider(), {"genre": "terror", "keyword": "hotel"}))
    limited = payload(await call_search(MockProvider(), {"genre": "drama", "limit": 2}))

    assert [m["title"] for m in both["results"]] == ["El resplandor"]
    assert len(limited["results"]) == 2


async def test_mock_mode_no_match_and_unknown_genre():
    empty = payload(await call_search(MockProvider(), {"keyword": "zzzz"}))
    unknown = await call_search(MockProvider(), {"genre": "telenovela"})

    assert empty == {"source": "mock", "results": []}
    assert unknown.isError and "Ciencia ficción" in unknown.content[0].text
