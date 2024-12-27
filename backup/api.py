import json
import requests

def fetch_movie_details(movie_id: int, jwt: str):
    movie_details = fetch(f"/film/{movie_id}/preview", jwt);
    return {
      "movie_id": movie_id,
      "title": movie_details["title"]["title"] if "title" in movie_details else movie_details["originalTitle"]["title"],
      "year": movie_details["year"],
      "genres": ", ".join(genre["name"]["text"] for genre in movie_details["genres"]),
    }

def fetch_user_ratings(jwt: str):
  movies = []
  page = 1
  while (True):
    response = fetch(f"/logged/vote/title/film?page={page}", jwt)
    if (type(response) != list or len(response) == 0):
      break
      
    page = page + 1

    for score in response:
      print(json.dumps(score))
      movie = {
        "movie_id": score["entity"],
        "rate": score["rate"],
        "favorite": score["favorite"] if "favorite" in score else False,
        "view_date": score["viewDate"],
      }

      movies.append(movie)
  
  print(f"Found ${len(movies)} scored movies!")

  return movies

def fetch_user_details(jwt: str) -> json:
  response = fetch("/logged/info", jwt)

  user_details = {
    "id": response["id"],
    "name": response["name"],
    "display_name": f"{response["personalData"]["firstname"]} {response["personalData"]["surname"]}" if "personalData" in response else response["name"],
  }

  print(f"User details: {json.dumps(user_details)}")

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
