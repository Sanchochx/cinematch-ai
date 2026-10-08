"""Proveedor mock: catálogo en memoria para desarrollar sin TMDB_API_KEY.

Los ids coinciden con los de TMDB para que el comportamiento sea el mismo al activar la key.
Títulos y géneros van en español, como los devuelve TMDB con `language=es-ES`.
"""

from typing import TypedDict

from providers.base import CastMember, MovieDetails, MovieSummary, ProviderSource
from providers.errors import MovieNotFoundError, UnknownGenreError
from providers.genres import SPANISH_GENRES, normalize_text, resolve_genre_id


class MockMovie(TypedDict):
    """Registro con la unión de campos de MovieSummary y MovieDetails."""

    id: int
    title: str
    overview: str
    release_date: str
    genres: list[str]
    vote_average: float
    poster_path: str | None
    director: str
    cast: list[CastMember]
    runtime: int


def _cast(*pairs: tuple[str, str]) -> list[CastMember]:
    return [CastMember(name=name, character=character) for name, character in pairs]


MOCK_MOVIES: tuple[MockMovie, ...] = (
    MockMovie(
        id=157336,
        title="Interstellar",
        overview="Un grupo de exploradores viaja a través de un agujero de gusano en busca de un nuevo hogar para la humanidad.",
        release_date="2014-11-05",
        genres=["Aventura", "Drama", "Ciencia ficción"],
        vote_average=8.4,
        poster_path=None,
        director="Christopher Nolan",
        cast=_cast(("Matthew McConaughey", "Cooper"), ("Anne Hathaway", "Brand"), ("Jessica Chastain", "Murph")),
        runtime=169,
    ),
    MockMovie(
        id=238,
        title="El padrino",
        overview="El patriarca de una familia de la mafia neoyorquina cede el control de su imperio a su hijo menor.",
        release_date="1972-03-14",
        genres=["Drama", "Crimen"],
        vote_average=8.7,
        poster_path=None,
        director="Francis Ford Coppola",
        cast=_cast(("Marlon Brando", "Vito Corleone"), ("Al Pacino", "Michael Corleone"), ("James Caan", "Sonny Corleone")),
        runtime=175,
    ),
    MockMovie(
        id=129,
        title="El viaje de Chihiro",
        overview="Una niña queda atrapada en un mundo de espíritus y debe trabajar en una casa de baños para salvar a sus padres.",
        release_date="2001-07-20",
        genres=["Animación", "Familia", "Fantasía"],
        vote_average=8.5,
        poster_path=None,
        director="Hayao Miyazaki",
        cast=_cast(("Rumi Hiiragi", "Chihiro"), ("Miyu Irino", "Haku"), ("Mari Natsuki", "Yubaba")),
        runtime=125,
    ),
    MockMovie(
        id=496243,
        title="Parásitos",
        overview="Una familia sin recursos se infiltra poco a poco en la vida de una familia adinerada.",
        release_date="2019-05-30",
        genres=["Comedia", "Suspense", "Drama"],
        vote_average=8.5,
        poster_path=None,
        director="Bong Joon-ho",
        cast=_cast(("Song Kang-ho", "Kim Ki-taek"), ("Choi Woo-shik", "Kim Ki-woo"), ("Park So-dam", "Kim Ki-jung")),
        runtime=133,
    ),
    MockMovie(
        id=155,
        title="El caballero oscuro",
        overview="Batman se enfrenta al Joker, un criminal que pretende sumir Gotham en el caos.",
        release_date="2008-07-16",
        genres=["Drama", "Acción", "Crimen", "Suspense"],
        vote_average=8.5,
        poster_path=None,
        director="Christopher Nolan",
        cast=_cast(("Christian Bale", "Bruce Wayne"), ("Heath Ledger", "Joker"), ("Aaron Eckhart", "Harvey Dent")),
        runtime=152,
    ),
    MockMovie(
        id=862,
        title="Toy Story",
        overview="Los juguetes de Andy cobran vida cuando nadie los ve, y la llegada de Buzz Lightyear pone a prueba a Woody.",
        release_date="1995-11-22",
        genres=["Animación", "Aventura", "Familia", "Comedia"],
        vote_average=8.0,
        poster_path=None,
        director="John Lasseter",
        cast=_cast(("Tom Hanks", "Woody (voz)"), ("Tim Allen", "Buzz Lightyear (voz)"), ("Don Rickles", "Mr. Potato (voz)")),
        runtime=81,
    ),
    MockMovie(
        id=680,
        title="Pulp Fiction",
        overview="Las historias de dos sicarios, un boxeador y una pareja de atracadores se entrelazan en Los Ángeles.",
        release_date="1994-09-10",
        genres=["Suspense", "Crimen", "Comedia"],
        vote_average=8.5,
        poster_path=None,
        director="Quentin Tarantino",
        cast=_cast(("John Travolta", "Vincent Vega"), ("Samuel L. Jackson", "Jules Winnfield"), ("Uma Thurman", "Mia Wallace")),
        runtime=154,
    ),
    MockMovie(
        id=419430,
        title="Déjame salir",
        overview="Un joven visita a la familia de su novia y descubre que su amable acogida esconde algo inquietante.",
        release_date="2017-02-24",
        genres=["Misterio", "Suspense", "Terror"],
        vote_average=7.6,
        poster_path=None,
        director="Jordan Peele",
        cast=_cast(("Daniel Kaluuya", "Chris Washington"), ("Allison Williams", "Rose Armitage"), ("Catherine Keener", "Missy Armitage")),
        runtime=104,
    ),
    MockMovie(
        id=694,
        title="El resplandor",
        overview="Un escritor acepta cuidar un hotel aislado durante el invierno y empieza a perder la cordura.",
        release_date="1980-05-23",
        genres=["Terror", "Suspense"],
        vote_average=8.2,
        poster_path=None,
        director="Stanley Kubrick",
        cast=_cast(("Jack Nicholson", "Jack Torrance"), ("Shelley Duvall", "Wendy Torrance"), ("Danny Lloyd", "Danny Torrance")),
        runtime=144,
    ),
    MockMovie(
        id=313369,
        title="La ciudad de las estrellas (La La Land)",
        overview="Una aspirante a actriz y un pianista de jazz se enamoran mientras persiguen sus sueños en Los Ángeles.",
        release_date="2016-11-29",
        genres=["Comedia", "Drama", "Romance", "Música"],
        vote_average=7.9,
        poster_path=None,
        director="Damien Chazelle",
        cast=_cast(("Ryan Gosling", "Sebastian"), ("Emma Stone", "Mia"), ("John Legend", "Keith")),
        runtime=128,
    ),
    MockMovie(
        id=76341,
        title="Mad Max: Furia en la carretera",
        overview="En un desierto postapocalíptico, Max y Furiosa huyen de un tirano a bordo de un camión de guerra.",
        release_date="2015-05-13",
        genres=["Acción", "Aventura", "Ciencia ficción"],
        vote_average=7.6,
        poster_path=None,
        director="George Miller",
        cast=_cast(("Tom Hardy", "Max Rockatansky"), ("Charlize Theron", "Imperator Furiosa"), ("Nicholas Hoult", "Nux")),
        runtime=121,
    ),
    MockMovie(
        id=194,
        title="Amélie",
        overview="Una joven camarera de Montmartre decide cambiar en secreto la vida de quienes la rodean.",
        release_date="2001-04-25",
        genres=["Comedia", "Romance"],
        vote_average=7.9,
        poster_path=None,
        director="Jean-Pierre Jeunet",
        cast=_cast(("Audrey Tautou", "Amélie Poulain"), ("Mathieu Kassovitz", "Nino Quincampoix"), ("Rufus", "Raphaël Poulain")),
        runtime=122,
    ),
)


def to_summary(movie: MockMovie) -> MovieSummary:
    return MovieSummary(
        id=movie["id"],
        title=movie["title"],
        release_year=int(movie["release_date"][:4]),
        overview=movie["overview"],
        genres=list(movie["genres"]),
        vote_average=movie["vote_average"],
        poster_path=movie["poster_path"],
    )


def to_details(movie: MockMovie) -> MovieDetails:
    return MovieDetails(
        id=movie["id"],
        title=movie["title"],
        overview=movie["overview"],
        director=movie["director"],
        cast=[CastMember(**member) for member in movie["cast"]],
        runtime=movie["runtime"],
        genres=list(movie["genres"]),
        release_date=movie["release_date"],
    )


class MockProvider:
    def __init__(self, movies: tuple[MockMovie, ...] = MOCK_MOVIES) -> None:
        self._movies = {movie["id"]: movie for movie in movies}

    @property
    def source(self) -> ProviderSource:
        return "mock"

    async def aclose(self) -> None:
        """Nada que liberar: los datos viven en memoria."""

    def all_movies(self) -> list[MockMovie]:
        return list(self._movies.values())

    def get_movie(self, movie_id: int) -> MockMovie:
        try:
            return self._movies[movie_id]
        except KeyError:
            raise MovieNotFoundError(movie_id) from None

    async def search_movies(
        self, *, genre: str | None, keyword: str | None, limit: int
    ) -> list[MovieSummary]:
        """Aplica sobre el catálogo los mismos filtros que haría TMDB."""
        movies = self.all_movies()
        if genre is not None:
            genre_id = resolve_genre_id(genre, SPANISH_GENRES)
            if genre_id is None:
                raise UnknownGenreError(genre, list(SPANISH_GENRES.values()))
            genre_name = normalize_text(SPANISH_GENRES[genre_id])
            movies = [m for m in movies if genre_name in map(normalize_text, m["genres"])]
        if keyword is not None:
            wanted = normalize_text(keyword)
            movies = [m for m in movies if wanted in normalize_text(f"{m['title']} {m['overview']}")]
        if genre is None and keyword is None:
            # Equivalente a /movie/popular: sin filtros, las mejor valoradas primero.
            movies.sort(key=lambda m: m["vote_average"], reverse=True)
        return [to_summary(movie) for movie in movies[:limit]]

    async def get_movie_details(self, *, movie_id: int) -> MovieDetails:
        return to_details(self.get_movie(movie_id))
