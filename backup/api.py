import logging
import random
import time

import requests

from .data import (
    Cast,
    Country,
    Director,
    Genre,
    Movie,
    MovieRating,
    UserDetails,
    UserRating,
    UserSimilarity,
)


class FilmwebAPI:
    def __init__(self, secret: str):
        self.logger = logging.getLogger("filmweb.api")

        self.__secret__ = secret
        self.__token__ = self.fetch_token()

    def fetch_movie_details(self, movie_id: int) -> Movie:
        movie_details = self.fetch(f"/film/{movie_id}/preview")

        self.logger.debug(f"Got movie details for movie id {movie_id}")

        return Movie(
            id=movie_id,
            title=movie_details["title"]["title"] if "title" in movie_details else None,
            originalTitle=movie_details["originalTitle"]["title"],
            internationalTitle=(
                movie_details["internationalTitle"]["title"]
                if "internationalTitle" in movie_details
                else None
            ),
            year=movie_details["year"],
            genres=(
                list(
                    Genre(genre["id"], genre["name"]["text"])
                    for genre in movie_details["genres"]
                )
                if "genres" in movie_details
                else []
            ),
            duration=movie_details["duration"] if "duration" in movie_details else None,
            directors=(
                list(
                    Director(director["id"], director["name"])
                    for director in movie_details["directors"]
                )
                if "directors" in movie_details
                else []
            ),
            cast=(
                list(
                    Cast(cast["id"], cast["name"]) for cast in movie_details["mainCast"]
                )
                if "mainCast" in movie_details
                else []
            ),
            countries=(
                list(
                    Country(country["id"], country["code"])
                    for country in movie_details["countries"]
                )
                if "countries" in movie_details
                else []
            ),
        )

    def fetch_movie_rating(self, movie_id: int) -> MovieRating:
        movie_rating = self.fetch(f"/film/{movie_id}/rating")

        self.logger.debug(f"Got rating details for movie id {movie_id}")

        return MovieRating(
            movie_id=movie_id,
            count=movie_rating["count"] if "count" in movie_rating else 0,
            rate=movie_rating["rate"] if "rate" in movie_rating else 0.0,
            countWantToSee=(
                movie_rating["countWantToSee"]
                if "countWantToSee" in movie_rating
                else 0
            ),
            countVote1=(
                movie_rating["countVote1"] if "countVote1" in movie_rating else 0
            ),
            countVote2=(
                movie_rating["countVote2"] if "countVote2" in movie_rating else 0
            ),
            countVote3=(
                movie_rating["countVote3"] if "countVote3" in movie_rating else 0
            ),
            countVote4=(
                movie_rating["countVote4"] if "countVote4" in movie_rating else 0
            ),
            countVote5=(
                movie_rating["countVote5"] if "countVote5" in movie_rating else 0
            ),
            countVote6=(
                movie_rating["countVote6"] if "countVote6" in movie_rating else 0
            ),
            countVote7=(
                movie_rating["countVote7"] if "countVote7" in movie_rating else 0
            ),
            countVote8=(
                movie_rating["countVote8"] if "countVote8" in movie_rating else 0
            ),
            countVote9=(
                movie_rating["countVote9"] if "countVote9" in movie_rating else 0
            ),
            countVote10=(
                movie_rating["countVote10"] if "countVote10" in movie_rating else 0
            ),
        )

    def fetch_user_ratings(self) -> list[UserRating]:
        movies: list[UserRating] = []
        page = 1
        while True:
            response = self.fetch(f"/logged/vote/title/film?page={page}", True)
            if type(response) != list or len(response) == 0:
                break

            page = page + 1

            for score in response:
                movie = UserRating(
                    score["entity"],
                    score["rate"],
                    score["favorite"] if "favorite" in score else False,
                    score["viewDate"],
                )

                movies.append(movie)

        self.logger.info(f"Found {len(movies)} scored movies!")

        return movies

    def fetch_user_details(self) -> UserDetails:
        response = self.fetch("/logged/info", True)

        user_details = UserDetails(
            id=response["id"],
            name=response["name"],
            display_name=(
                f"{response["personalData"]["firstname"]} {response["personalData"]["surname"]}"
                if "personalData" in response
                else None
            ),
        )

        self.logger.debug(f"Got user details for user {user_details.name}")

        return user_details

    def fetch_user_friends(self) -> list[UserDetails]:
        response = self.fetch(f"/logged/friends", True)

        friends_details: list[UserDetails] = []
        for id, details in response.items():
            display_name = None
            if "firstname" in details or "surname" in details:
                display_name = f"{details["firstname"] if "firstname" in details else ""} {details["surname"] if "surname" in details else ""}".strip()

            friend_details = UserDetails(
                id=int(id),
                name=details["name"],
                display_name=display_name,
            )
            friends_details.append(friend_details)

        self.logger.info(f"Found {len(friends_details)} friends!")

        return friends_details

    def fetch_user_friends_similarities(self) -> list[UserSimilarity]:
        response = self.fetch(f"/logged/friends/similarities", True)

        friends_similarities: list[UserSimilarity] = []
        for similarities in response:
            friend_similarity = UserSimilarity(
                id=similarities[0],
                similarity=similarities[1],
                movies=similarities[2],
            )
            friends_similarities.append(friend_similarity)

        self.logger.info(
            f"Found {len(friends_similarities)} friends with similar taste!"
        )

        return friends_similarities

    def fetch_friend_ratings(self, friend_name: str) -> list[UserRating]:
        movies: list[UserRating] = []
        page = 1
        while True:
            response = self.fetch(
                f"/logged/friend/{friend_name}/vote/title/film?page={page}", True
            )
            if type(response) != list or len(response) == 0:
                break

            page = page + 1

            for score in response:
                movie = UserRating(
                    score["entity"],
                    score["rate"],
                    score["favorite"] if "favorite" in score else False,
                    score["viewDate"],
                )

                movies.append(movie)

        self.logger.info(f"Found {len(movies)} movies scored by {friend_name}!")

        return movies

    def fetch_token(self) -> str:
        cookies = {"_artuser_prm": self.__secret__}

        try:
            url = "https://www.filmweb.pl/api/v1/jwt"
            response = requests.post(url, cookies=cookies, timeout=10)
            response.raise_for_status()

            self.logger.debug(f"Got the JWT token!")

            return response.cookies.get("JWT")
        except requests.exceptions.RequestException:
            raise FilmwebInvalidTokenError("Failed to fetch JWT token!")

    def fetch(self, path: str, authenticate: bool = False):
        headers = {"X-Locale": "pl_PL"}

        url = f"https://www.filmweb.pl/api/v1{path}"

        time.sleep(random.uniform(0.1, 0.35))  # TODO: remove, rethink

        retry = 0
        while retry < 3:
            if retry > 0:
                self.logger.warning(f"Attempt no. {retry} to fetch {url}")
                time.sleep(1)
            retry += 1

            cookies = {}
            if authenticate is True:
                cookies["JWT"] = self.__token__

            response = None
            try:
                response = requests.get(
                    url, headers=headers, cookies=cookies, timeout=10
                )
                response.raise_for_status()

                if response.status_code == 204:
                    return None

                return response.json()
            except requests.exceptions.Timeout as e:
                if retry == 3:
                    self.logger.error(
                        f"All {retry} attempts to fetch {url} have failed!",
                        e,
                        exc_info=True,
                    )
                continue
            except requests.exceptions.RequestException as e:
                if response is not None and response.status_code == 400:
                    self.__token__ = self.fetch_token()
                    continue
                else:
                    raise FilmwebError(
                        f"Failed to fetch data due to unhandled exception"
                    ) from e

        raise FilmwebError(f"Failed to fetch data after {retry} retries!")


class FilmwebError(Exception):
    pass


class FilmwebInvalidTokenError(FilmwebError):
    pass
