from dataclasses import dataclass
import json
import requests

@dataclass(eq=True, repr=True)
class Genre:
  id: int
  name: str

@dataclass(eq=True, repr=True)
class Movie:
  id: int
  title: str
  year: int
  genres: list[Genre]

@dataclass(eq=True, repr=True)
class Rating:
  movie_id: int
  rate: int
  favorite: bool
  view_date: int

@dataclass(eq=True, repr=True)
class UserDetails:
  id: int
  name: str
  display_name: str | None


def fetch_movie_details(movie_id: int, jwt: str) -> Movie:
    movie_details = fetch(f"/film/{movie_id}/preview", jwt)

    return Movie(
      movie_id,
      movie_details["title"]["title"] if "title" in movie_details else movie_details["originalTitle"]["title"],
      movie_details["year"],
      list(Genre(genre["id"], genre["name"]["text"]) for genre in movie_details["genres"])
    )

def fetch_user_ratings(jwt: str) -> list[Rating]:
  movies: list[Rating] = []
  page = 1
  while (True):
    response = fetch(f"/logged/vote/title/film?page={page}", jwt)
    if (type(response) != list or len(response) == 0):
      break
      
    page = page + 1

    for score in response:
      movie = Rating(
        score["entity"],
        score["rate"],
        score["favorite"] if "favorite" in score else False,
        score["viewDate"]
      )

      movies.append(movie)
  
  print(f"Found ${len(movies)} scored movies!")

  return movies

def fetch_user_details(jwt: str) -> UserDetails:
  response = fetch("/logged/info", jwt)

  user_details = UserDetails(
    response["id"],
    response["name"],
    f"{response["personalData"]["firstname"]} {response["personalData"]["surname"]}" if "personalData" in response else None
  )

  print(f"User details: {user_details}")

  return user_details


def fetch(path: str, jwt: str):
    headers = {
        "X-Locale": "pl_PL"
    }
    cookies = {
       "JWT": jwt
    }

    url = f"https://www.filmweb.pl/api/v1{path}"

    response = requests.get(url, headers=headers, cookies=cookies, timeout=5)
    if not response.ok:
        raise FilmwebError(response.text)
    return response.json()


class FilmwebError(Exception):
    """Error raised when Filmweb requests fails"""

    def __init__(self, message: str):
        super().__init__()
        self.message = message

    def __str__(self) -> str:
        return repr(self.message)
