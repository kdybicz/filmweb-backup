import logging
import requests
import time

from .data import Director, Genre, Movie, MovieRating, UserDetails, UserRating

class FilmwebAPI:
  def __init__(self):
    self.logger = logging.getLogger("filmweb.api")


  def fetch_movie_details(self, movie_id: int) -> Movie:
      movie_details = self.fetch(f"/film/{movie_id}/preview")

      self.logger.debug(f"Got movie details for movie id {movie_id}")

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


  def fetch_movie_rating(self, movie_id: int) -> MovieRating:
      movie_rating = self.fetch(f"/film/{movie_id}/rating")

      self.logger.debug(f"Got rating details for movie id {movie_id}")

      return MovieRating(
        movie_id = movie_id,
        count = movie_rating["count"] if "count" in movie_rating else 0,
        rate = movie_rating["rate"] if "rate" in movie_rating else 0.0,
        countWantToSee = movie_rating["countWantToSee"] if "countWantToSee" in movie_rating else 0,
        countVote1 = movie_rating["countVote1"] if "countVote1" in movie_rating else 0,
        countVote2 = movie_rating["countVote2"] if "countVote2" in movie_rating else 0,
        countVote3 = movie_rating["countVote3"] if "countVote3" in movie_rating else 0,
        countVote4 = movie_rating["countVote4"] if "countVote4" in movie_rating else 0,
        countVote5 = movie_rating["countVote5"] if "countVote5" in movie_rating else 0,
        countVote6 = movie_rating["countVote6"] if "countVote6" in movie_rating else 0,
        countVote7 = movie_rating["countVote7"] if "countVote7" in movie_rating else 0,
        countVote8 = movie_rating["countVote8"] if "countVote8" in movie_rating else 0,
        countVote9 = movie_rating["countVote9"] if "countVote9" in movie_rating else 0,
        countVote10 = movie_rating["countVote10"] if "countVote10" in movie_rating else 0,
      )


  def fetch_user_ratings(self, jwt: str) -> list[UserRating]:
    movies: list[UserRating] = []
    page = 1
    while (True):
      response = self.fetch(f"/logged/vote/title/film?page={page}", jwt)
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

    self.logger.info(f"Found {len(movies)} scored movies!")

    return movies


  def fetch_user_details(self, jwt: str) -> UserDetails:
    response = self.fetch("/logged/info", jwt)

    user_details = UserDetails(
      id = response["id"],
      name = response["name"],
      display_name = f"{response["personalData"]["firstname"]} {response["personalData"]["surname"]}" if "personalData" in response else None
    )

    self.logger.debug(f"Got user details for user {user_details.name}")

    return user_details


  def fetch_user_friends(self, jwt: str) -> list[UserDetails]:
    response = self.fetch(f"/logged/friends", jwt)

    friends_details: list[UserDetails] = []
    for id, details in response.items():
      display_name = None
      if "firstname" in details or "surname" in details:
        display_name = f"{details["firstname"] if "firstname" in details else ""} {details["surname"] if "surname" in details else ""}".strip()

      friend_details = UserDetails(
        id = int(id),
        name = details["name"],
        display_name = display_name,
      )
      friends_details.append(friend_details)

    self.logger.info(f"Found {len(friends_details)} friends!")

    return friends_details


  def fetch_friend_ratings(self, friend_name: str, jwt: str) -> list[UserRating]:
    movies: list[UserRating] = []
    page = 1
    while (True):
      response = self.fetch(f"/logged/friend/{friend_name}/vote/title/film?page={page}", jwt)
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

    self.logger.info(f"Found {len(movies)} movies scored by {friend_name}!")

    return movies


  def fetch(self, path: str, jwt: str | None = None):
    headers = {
      "X-Locale": "pl_PL"
    }

    cookies = {}
    if jwt is not None:
      cookies["JWT"] = jwt

    url = f"https://www.filmweb.pl/api/v1{path}"

    time.sleep(0.1) # TODO: remove, rethink

    retry = 0
    while retry < 3:
      if retry > 0:
        self.logger.warning(f"{retry} retry to fetch {url}")
        time.sleep(1)
      retry += 1

      try:
        response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        response.raise_for_status()

        if response.status_code == 204:
            return None

        return response.json()
      except requests.exceptions.Timeout:
        continue
      except requests.exceptions.RequestException:
        raise FilmwebException(f"Failed to fetch data - {response.status_code}: {response.text.strip()}")

    raise FilmwebException(f"Failed to fetch data after {retry} retries!")


class FilmwebException(Exception):
  """Error raised when Filmweb requests fails"""
  pass
