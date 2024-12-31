import csv
from dataclasses import asdict
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
  db.upsert_ratings(user_details.id, ratings)
  print(ratings)

  for rating in ratings:
    movie_id = rating.movie_id
    if db.has_movie(movie_id) is False:
      movie_details = fetch_movie_details(movie_id, jwt)
      db.insert_movie(movie_details)
      print(movie_details)

  ratings_export = db.get_user_rating(user_details.id)
  print(ratings_export)

  with open('filmweb.csv', 'w', newline='') as csv_file:
    export_file = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    export_file.writerow(['title', 'year', 'rate', 'favorite', 'view_date', 'genres'])
    export_file.writerows(list([re.title, re.year, re.rate, re.favorite, re.view_date, re.genres] for re in ratings_export))

  return 0

if __name__ == '__main__':
  sys.exit(main())
