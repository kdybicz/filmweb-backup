import csv
import logging

from .api import FilmwebAPI
from .data import UserDetails
from .db import FilmwebDB

class FilmwebBackup:
  def __init__(self, db: FilmwebDB, api: FilmwebAPI):
    self.logger = logging.getLogger("filmweb.backup")

    self.db = db
    self.api = api


  @classmethod
  def from_secret(cls, secret: str):
    db = FilmwebDB()
    api = FilmwebAPI(secret)

    return cls(db, api)


  def backup_movie(self, movie_id: int) -> None:
    if self.db.should_update_movie(movie_id) is True:
      movie_details = self.api.fetch_movie_details(movie_id)
      self.db.upsert_movie(movie_details)

      movie_rating = self.api.fetch_movie_rating(movie_id)
      self.db.upsert_movie_rating(movie_rating)


  def backup_user(self, user: UserDetails) -> None:
    self.db.set_user_details(user)

    ratings = self.api.fetch_user_ratings()
    self.db.upsert_ratings(user.id, ratings)

    for rating in ratings:
      self.backup_movie(rating.movie_id)

    friends = self.api.fetch_user_friends()
    for friend in friends:
      self.db.set_user_details(friend)

      friend_ratings = self.api.fetch_friend_ratings(friend.name)
      self.db.upsert_ratings(friend.id, friend_ratings)

      for rating in friend_ratings:
        self.backup_movie(rating.movie_id)


  def backup(self) -> UserDetails:
    user_details = self.api.fetch_user_details()

    self.backup_user(user_details)

    return user_details


  def export(self, user_id: int):
    ratings_export = self.db.get_user_rating(user_id)

    with open("filmweb.csv", "w", newline="") as csv_file:
      export_file = csv.writer(csv_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
      export_file.writerow(["title", "year", "rate", "favorite", "view_date", "genres"])
      export_file.writerows(list([re.title, re.year, re.rate, re.favorite, re.view_date, re.genres] for re in ratings_export))

    self.logger.info(f"Exported information about {len(ratings_export)} movies for user {user_id}")
