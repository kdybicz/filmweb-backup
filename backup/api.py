import logging
import requests

from data import Director, Genre, Movie, MovieRating, UserDetails, UserRating

logger = logging.getLogger("filmweb.api")

def fetch_movie_details(movie_id: int) -> Movie:
    movie_details = fetch(f"/film/{movie_id}/preview")

    logger.debug(f"Got movie details for movie id {movie_id}")

    return Movie(
      id = movie_id,
      title = movie_details["title"]["title"] if "title" in movie_details else None,
      originalTitle = movie_details["originalTitle"]["title"],
      internationalTitle = movie_details["internationalTitle"]["title"] if "internationalTitle" in movie_details else None,
      year = movie_details["year"],
      genres = list(Genre(genre["id"], genre["name"]["text"]) for genre in movie_details["genres"]),
      duration = movie_details["duration"],
      directors = list(Director(director["id"], director["name"]) for director in movie_details["directors"]),
    )


def fetch_movie_rating(movie_id: int) -> MovieRating:
    movie_rating = fetch(f"/film/{movie_id}/rating")

    logger.debug(f"Got rating details for movie id {movie_id}")

    return MovieRating(
      movie_id = movie_id,
      count = movie_rating["count"],
      rate = movie_rating["rate"],
      countWantToSee = movie_rating["countWantToSee"],
      countVote1 = movie_rating["countVote1"],
      countVote2 = movie_rating["countVote2"],
      countVote3 = movie_rating["countVote3"],
      countVote4 = movie_rating["countVote4"],
      countVote5 = movie_rating["countVote5"],
      countVote6 = movie_rating["countVote6"],
      countVote7 = movie_rating["countVote7"],
      countVote8 = movie_rating["countVote8"],
      countVote9 = movie_rating["countVote9"],
      countVote10 = movie_rating["countVote10"],
    )


def fetch_user_ratings(jwt: str) -> list[UserRating]:
  movies: list[UserRating] = []
  page = 1
  while (True):
    response = fetch(f"/logged/vote/title/film?page={page}", jwt)
    if (type(response) != list or len(response) == 0):
      break
      
    page = page + 1

    for score in response:
      movie = UserRating(
        score["entity"],
        score["rate"],
        score["favorite"] if "favorite" in score else False,
        score["viewDate"]
      )

      movies.append(movie)
  
  logger.info(f"Found {len(movies)} scored movies!")

  return movies


def fetch_user_details(jwt: str) -> UserDetails:
  response = fetch("/logged/info", jwt)

  user_details = UserDetails(
    response["id"],
    response["name"],
    f"{response["personalData"]["firstname"]} {response["personalData"]["surname"]}" if "personalData" in response else None
  )

  logger.debug(f"Got user details for user {user_details.name}")

  return user_details


def fetch(path: str, jwt: str | None = None):
    headers = {
        "X-Locale": "pl_PL"
    }

    cookies = {}
    if jwt is not None:
      cookies["JWT"] = jwt

    url = f"https://www.filmweb.pl/api/v1{path}"

    response = requests.get(url, headers=headers, cookies=cookies, timeout=5)
    if not response.ok:
      logger.error(f"{response.status_code}: {response.text}")
      raise FilmwebError(response.text)
    return response.json()


class FilmwebError(Exception):
    """Error raised when Filmweb requests fails"""

    def __init__(self, message: str):
        super().__init__()
        self.message = message

    def __str__(self) -> str:
        return repr(self.message)
