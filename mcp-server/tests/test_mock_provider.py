import pytest

from providers.base import CastMember, MovieDetails, MovieSummary
from providers.errors import MovieNotFoundError
from providers.mock import MOCK_MOVIES, MockProvider, to_details, to_summary


def test_catalog_has_at_least_ten_movies_with_varied_genres():
    genres = {genre for movie in MOCK_MOVIES for genre in movie["genres"]}

    assert len(MOCK_MOVIES) >= 10
    assert len({movie["id"] for movie in MOCK_MOVIES}) == len(MOCK_MOVIES)
    assert len(genres) >= 8


@pytest.mark.parametrize("movie", MOCK_MOVIES, ids=lambda movie: movie["title"])
def test_every_movie_has_director_and_cast(movie):
    assert movie["director"]
    assert len(movie["cast"]) >= 3
    assert all(member["name"] and member["character"] for member in movie["cast"])


@pytest.mark.parametrize("movie", MOCK_MOVIES, ids=lambda movie: movie["title"])
def test_summary_matches_normalized_schema(movie):
    summary = to_summary(movie)

    assert summary.keys() == MovieSummary.__annotations__.keys()
    assert isinstance(summary["release_year"], int)
    assert isinstance(summary["vote_average"], float)


@pytest.mark.parametrize("movie", MOCK_MOVIES, ids=lambda movie: movie["title"])
def test_details_match_normalized_schema(movie):
    details = to_details(movie)

    assert details.keys() == MovieDetails.__annotations__.keys()
    assert all(member.keys() == CastMember.__annotations__.keys() for member in details["cast"])


def test_conversions_do_not_share_mutable_state_with_catalog():
    movie = MOCK_MOVIES[0]

    to_details(movie)["genres"].append("Otro")
    to_details(movie)["cast"][0]["name"] = "Otro"

    assert "Otro" not in movie["genres"]
    assert movie["cast"][0]["name"] != "Otro"


def test_provider_identifies_itself_as_mock():
    assert MockProvider().source == "mock"


def test_get_movie_by_id():
    provider = MockProvider()

    assert provider.get_movie(157336)["title"] == "Interstellar"
    assert len(provider.all_movies()) == len(MOCK_MOVIES)


def test_get_unknown_movie_raises_not_found():
    with pytest.raises(MovieNotFoundError):
        MockProvider().get_movie(1)
