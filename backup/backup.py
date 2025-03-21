import csv
import logging
import re

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

    @classmethod
    def from_db_api(cls, db: FilmwebDB, api: FilmwebAPI):
        return cls(db, api)

    def backup_movie(self, movie_id: int) -> None:
        if self.db.should_update_movie(movie_id) is True:
            movie_details = self.api.fetch_movie_details(movie_id)
            self.db.upsert_movie(movie_details)
        else:
            self.logger.debug("Movie %s details are up-to-date", movie_id)

        if self.db.should_update_movie_rating(movie_id) is True:
            movie_rating = self.api.fetch_movie_rating(movie_id)
            self.db.upsert_movie_rating(movie_rating)
        else:
            self.logger.debug("Movie rating for movie %s are up-to-date", movie_id)

    def backup_user(self, user: UserDetails) -> None:
        if (
            self.db.should_update_user(user.id, 60) is False
        ):  # TODO: change or remove TTL
            self.logger.debug("User %s details are up-to-date", user.name)
            return None

        ratings = self.api.fetch_user_ratings()
        self.db.upsert_ratings(user.id, ratings)

        for rating in ratings:
            self.backup_movie(rating.movie_id)

        friends = self.api.fetch_user_friends()
        if len(friends) > 0:
            for friend in friends:
                if (
                    self.db.should_update_user(friend.id) is False
                ):  # TODO: change or remove TTL
                    self.logger.debug("Friend %s details are up-to-date", friend.name)
                    continue

                friend_ratings = self.api.fetch_friend_ratings(friend.name)
                self.db.upsert_ratings(friend.id, friend_ratings)

                for rating in friend_ratings:
                    self.backup_movie(rating.movie_id)

                self.db.upsert_user_details(friend)

            similar_users = self.api.fetch_user_friends_similarities()
            self.db.upsert_similar_users(user.id, similar_users)

        self.db.upsert_user_details(user)

    def backup(self) -> UserDetails:
        user_details = self.api.fetch_user_details()

        self.backup_user(user_details)

        return user_details

    def export(self, user_details: UserDetails) -> None:
        ratings_export = self.db.get_user_rating(user_details.id)

        safe_user_name = self.__get_valid_filename__(user_details.name)
        with open(f"export/filmweb-{safe_user_name}.csv", "w", newline="") as csv_file:
            export_file = csv.writer(
                csv_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
            )
            export_file.writerow(
                [
                    "original_title",
                    "international_title",
                    "title",
                    "year",
                    "rate",
                    "my_rate",
                    "favorite",
                    "view_date",
                    "duration",
                    "genres",
                    "directors",
                    "cast",
                    "countries",
                ]
            )
            export_file.writerows(
                list(
                    [
                        re.original_title,
                        re.international_title,
                        re.title,
                        re.year,
                        re.rate,
                        re.my_rate,
                        re.favorite,
                        re.view_date,
                        re.duration,
                        re.genres,
                        re.directors,
                        re.cast,
                        re.countries,
                    ]
                    for re in ratings_export
                )
            )

        self.logger.info(
            f"Exported information about {len(ratings_export)} movies for user {user_details.name}"
        )

    def export_all(self) -> None:
        users = self.db.get_all_users()

        for user_details in users:
            self.export(user_details)

        self.logger.info(
            f"Exported information about movies for all {len(users)} users completed!"
        )

    def __get_valid_filename__(self, name: str) -> str:
        s = str(name).strip().replace(" ", "_")
        s = re.sub(r"(?u)[^-\w.]", "", s)
        return s
