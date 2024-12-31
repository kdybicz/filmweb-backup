import csv
import sys

from api import fetch_movie_details, fetch_movie_rating, fetch_user_details, fetch_user_ratings
from db import FilmwebDB

def main() -> int:
  jwt = ""

  db = FilmwebDB()
  
  user_details = fetch_user_details(jwt)
  db.set_user_details(user_details)
  print(user_details)

  ratings = fetch_user_ratings(jwt)[:10]
  db.upsert_ratings(user_details.id, ratings)
  print(ratings)

  for rating in ratings:
    movie_id = rating.movie_id
    if db.has_movie(movie_id) is False:
      movie_details = fetch_movie_details(movie_id)
      db.insert_movie(movie_details)
      print(movie_details)

      movie_rating = fetch_movie_rating(movie_id)
      db.upsert_movie_rating(movie_rating)
      print(movie_rating)

  ratings_export = db.get_user_rating(user_details.id)
  print(ratings_export)

  with open('filmweb.csv', 'w', newline='') as csv_file:
    export_file = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    export_file.writerow(['title', 'year', 'rate', 'favorite', 'view_date', 'genres'])
    export_file.writerows(list([re.title, re.year, re.rate, re.favorite, re.view_date, re.genres] for re in ratings_export))
    # https://www.filmweb.pl/film/Klaus-2019-743825
    # https://www.filmweb.pl/api/v1/film/743825/rating


  return 0

if __name__ == '__main__':
  sys.exit(main())
