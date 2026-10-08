"""Géneros de películas: resolución de nombres (español/inglés) a ids de TMDB.

Los ids de género de TMDB son estables. La tabla estática aporta los nombres en inglés y los
alias; los nombres en el idioma configurado vienen de `/genre/movie/list` (o de esta misma
tabla en modo mock).
"""

import unicodedata
from collections.abc import Mapping

# id → (nombre en español, nombre en inglés)
GENRE_NAMES: Mapping[int, tuple[str, str]] = {
    28: ("Acción", "Action"),
    12: ("Aventura", "Adventure"),
    16: ("Animación", "Animation"),
    35: ("Comedia", "Comedy"),
    80: ("Crimen", "Crime"),
    99: ("Documental", "Documentary"),
    18: ("Drama", "Drama"),
    10751: ("Familia", "Family"),
    14: ("Fantasía", "Fantasy"),
    36: ("Historia", "History"),
    27: ("Terror", "Horror"),
    10402: ("Música", "Music"),
    9648: ("Misterio", "Mystery"),
    10749: ("Romance", "Romance"),
    878: ("Ciencia ficción", "Science Fiction"),
    10770: ("Película de TV", "TV Movie"),
    53: ("Suspense", "Thriller"),
    10752: ("Bélica", "War"),
    37: ("Western", "Western"),
}

GENRE_ALIASES: Mapping[str, int] = {
    "sci-fi": 878,
    "scifi": 878,
    "suspenso": 53,
    "guerra": 10752,
}

SPANISH_GENRES: Mapping[int, str] = {genre_id: es for genre_id, (es, _) in GENRE_NAMES.items()}


def normalize_text(text: str) -> str:
    """Minúsculas, sin tildes y con espacios colapsados, para comparar sin distinguir forma."""
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join(stripped.casefold().split())


def resolve_genre_id(name: str, names_by_id: Mapping[int, str]) -> int | None:
    """Id del género `name`, o None si no existe.

    Acepta el nombre en el idioma de `names_by_id`, en español, en inglés y los alias.
    """
    wanted = normalize_text(name)
    candidates: dict[str, int] = {}
    # Orden de menor a mayor prioridad: los nombres del proveedor pisan al resto.
    for alias, genre_id in GENRE_ALIASES.items():
        candidates[normalize_text(alias)] = genre_id
    for genre_id, (spanish, english) in GENRE_NAMES.items():
        candidates[normalize_text(spanish)] = genre_id
        candidates[normalize_text(english)] = genre_id
    for genre_id, provider_name in names_by_id.items():
        candidates[normalize_text(provider_name)] = genre_id
    return candidates.get(wanted)
