import json

import httpx
import pytest
from mcp.shared.memory import create_connected_server_and_client_session

from config import Settings
from providers.mock import MockProvider
from server import create_server

MOVIE_ID = 157336


def credits_cast(count: int) -> list[dict]:
    return [{"name": f"Actor {i}", "character": f"Personaje {i}", "order": i} for i in range(count)]


def tmdb_movie(**overrides) -> dict:
    movie = {
        "id": MOVIE_ID,
        "title": "Interstellar",
        "overview": "Un grupo de exploradores viaja a través de un agujero de gusano.",
        "runtime": 169,
        "genres": [{"id": 12, "name": "Aventura"}, {"id": 18, "name": "Drama"}],
        "release_date": "2014-11-05",
        "credits": {
            "cast": credits_cast(8),
            "crew": [
                {"name": "Hans Zimmer", "job": "Original Music Composer"},
                {"name": "Christopher Nolan", "job": "Director"},
            ],
        },
    }
    movie.update(overrides)
    return movie


async def call_details(provider, arguments: dict):
    mcp = create_server(Settings(), provider)
    async with create_connected_server_and_client_session(mcp) as client:
        return await client.call_tool("get_movie_details", arguments)


def payload(result) -> dict:
    assert not result.isError, result.content
    return json.loads(result.content[0].text)


def movie_of(result) -> dict:
    return payload(result)["movie"]


async def test_tool_is_listed_with_required_movie_id(tmdb_provider):
    mcp = create_server(Settings(), tmdb_provider)
    async with create_connected_server_and_client_session(mcp) as client:
        tools = {tool.name: tool for tool in (await client.list_tools()).tools}

    tool = tools["get_movie_details"]
    assert "director" in tool.description and "cast" in tool.description
    assert tool.inputSchema["required"] == ["movie_id"]
    assert tool.inputSchema["properties"]["movie_id"]["type"] == "integer"
    assert tool.annotations.readOnlyHint is True


async def test_happy_path_makes_a_single_request_with_credits(tmdb_mock, tmdb_provider):
    route = tmdb_mock.get(f"/movie/{MOVIE_ID}").respond(200, json=tmdb_movie())

    data = payload(await call_details(tmdb_provider, {"movie_id": MOVIE_ID}))

    assert tmdb_mock.calls.call_count == 1
    assert route.calls.last.request.url.params["append_to_response"] == "credits"
    assert data["source"] == "tmdb"
    assert data["movie"] == {
        "id": MOVIE_ID,
        "title": "Interstellar",
        "overview": "Un grupo de exploradores viaja a través de un agujero de gusano.",
        "director": "Christopher Nolan",
        "cast": [{"name": f"Actor {i}", "character": f"Personaje {i}"} for i in range(5)],
        "runtime": 169,
        "genres": ["Aventura", "Drama"],
        "release_date": "2014-11-05",
    }


async def test_empty_overview_stays_empty(tmdb_mock, tmdb_provider):
    tmdb_mock.get(f"/movie/{MOVIE_ID}").respond(200, json=tmdb_movie(overview=""))

    assert movie_of(await call_details(tmdb_provider, {"movie_id": MOVIE_ID}))["overview"] == ""


async def test_movie_without_director_has_null_director(tmdb_mock, tmdb_provider):
    credits = {"cast": credits_cast(1), "crew": [{"name": "Hans Zimmer", "job": "Producer"}]}
    tmdb_mock.get(f"/movie/{MOVIE_ID}").respond(200, json=tmdb_movie(credits=credits))

    assert movie_of(await call_details(tmdb_provider, {"movie_id": MOVIE_ID}))["director"] is None


async def test_multiple_directors_are_joined(tmdb_mock, tmdb_provider):
    crew = [
        {"name": "Lana Wachowski", "job": "Director"},
        {"name": "Joel Silver", "job": "Producer"},
        {"name": "Lilly Wachowski", "job": "Director"},
    ]
    tmdb_mock.get(f"/movie/{MOVIE_ID}").respond(
        200, json=tmdb_movie(credits={"cast": [], "crew": crew})
    )

    director = movie_of(await call_details(tmdb_provider, {"movie_id": MOVIE_ID}))["director"]

    assert director == "Lana Wachowski, Lilly Wachowski"


async def test_cast_with_fewer_than_five_members(tmdb_mock, tmdb_provider):
    credits = {"cast": credits_cast(2), "crew": []}
    tmdb_mock.get(f"/movie/{MOVIE_ID}").respond(200, json=tmdb_movie(credits=credits))

    cast = movie_of(await call_details(tmdb_provider, {"movie_id": MOVIE_ID}))["cast"]

    assert [member["name"] for member in cast] == ["Actor 0", "Actor 1"]


async def test_cast_is_sorted_by_order_before_truncating(tmdb_mock, tmdb_provider):
    unsorted = [{"name": f"Actor {i}", "character": "X", "order": i} for i in (6, 0, 5, 1, 4, 2, 3)]
    credits = {"cast": unsorted, "crew": []}
    tmdb_mock.get(f"/movie/{MOVIE_ID}").respond(200, json=tmdb_movie(credits=credits))

    cast = movie_of(await call_details(tmdb_provider, {"movie_id": MOVIE_ID}))["cast"]

    assert [member["name"] for member in cast] == [f"Actor {i}" for i in range(5)]


async def test_unknown_runtime_and_release_date_are_null(tmdb_mock, tmdb_provider):
    tmdb_mock.get(f"/movie/{MOVIE_ID}").respond(200, json=tmdb_movie(runtime=0, release_date=""))

    movie = movie_of(await call_details(tmdb_provider, {"movie_id": MOVIE_ID}))

    assert movie["runtime"] is None
    assert movie["release_date"] is None


@pytest.mark.parametrize("movie_id", [0, -1, "157336", "abc", 1.5, 157336.0, True, None])
async def test_invalid_movie_id_is_rejected_before_calling_tmdb(tmdb_mock, tmdb_provider, movie_id):
    result = await call_details(tmdb_provider, {"movie_id": movie_id})

    assert result.isError
    assert not any(route.called for route in tmdb_mock.routes)


async def test_missing_movie_id_is_rejected(tmdb_mock, tmdb_provider):
    result = await call_details(tmdb_provider, {})

    assert result.isError
    assert tmdb_mock.calls.call_count == 0


async def test_unknown_movie_returns_not_found_error(tmdb_mock, tmdb_provider):
    tmdb_mock.get("/movie/999999999").respond(404, json={"status_code": 34})

    result = await call_details(tmdb_provider, {"movie_id": 999999999})

    assert result.isError
    assert "No se encontró la película con id 999999999" in result.content[0].text


@pytest.mark.parametrize(
    ("response", "expected"),
    [
        (httpx.Response(401, json={"status_message": "Invalid API key"}), "credenciales de TMDB inválidas"),
        (httpx.Response(500), "TMDB no está disponible"),
        (httpx.Response(503), "TMDB no está disponible"),
    ],
)
async def test_tmdb_failures_become_readable_tool_errors(tmdb_mock, tmdb_provider, response, expected):
    tmdb_mock.get(f"/movie/{MOVIE_ID}").mock(return_value=response)

    result = await call_details(tmdb_provider, {"movie_id": MOVIE_ID})

    assert result.isError
    text = result.content[0].text
    assert expected in text
    assert "api_key" not in text


# --- modo mock -----------------------------------------------------------------------------


async def test_mock_mode_returns_the_mock_movie():
    data = payload(await call_details(MockProvider(), {"movie_id": MOVIE_ID}))

    assert data["source"] == "mock"
    assert data["movie"]["title"] == "Interstellar"
    assert data["movie"]["director"] == "Christopher Nolan"
    assert data["movie"]["cast"][0] == {"name": "Matthew McConaughey", "character": "Cooper"}
    assert data["movie"]["runtime"] == 169
    assert data["movie"]["release_date"] == "2014-11-05"


async def test_mock_mode_unknown_movie_returns_the_same_error():
    result = await call_details(MockProvider(), {"movie_id": 1})

    assert result.isError
    assert "No se encontró la película con id 1" in result.content[0].text
