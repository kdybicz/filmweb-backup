import json
import sys

from api import fetch_movie_details, fetch_user_details, fetch_user_ratings
from db import FilmwebDB

def main() -> int:
  jwt = "<ENTER_JWT_HERE>"

  db = FilmwebDB()
  
  user_details = fetch_user_details(jwt)
  db.set_user_details(user_details)
  print(user_details)

  ratings = fetch_user_ratings(jwt)
  db.upsert_ratings(ratings)
  print(ratings)

  for rating in ratings:
    movie_id = rating.movie_id
    if db.has_movie(movie_id) is False:
      movie_details = fetch_movie_details(movie_id, jwt)
      db.insert_movie(movie_details)
      print(movie_details)

  return 0

if __name__ == '__main__':
  sys.exit(main())
