import unittest
from unittest.mock import MagicMock, Mock, call, patch

import requests

from backup.api import FilmwebAPI, FilmwebError
from backup.data import (
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


class TestFilmwebAPI(unittest.TestCase):
    @patch("backup.api.requests.post")
    def setUp(self, mock_requests: Mock):
        mock_response = MagicMock()
        mock_response.cookies.get.return_value = "jwt"
        mock_requests.return_value = mock_response

        self.api = FilmwebAPI("secret")

    @patch("backup.api.requests.post")
    def test_fetch_token(self, mock_requests: Mock):
        # given
        mock_response = MagicMock()
        mock_response.cookies.get.return_value = "jwt"
        mock_requests.return_value = mock_response
        # and
        api = FilmwebAPI("secret")

        # when
        result = api.fetch_token()
        # then
        self.assertEqual(result, "jwt")
        # and
        self.assertEqual(mock_requests.call_count, 2)
        mock_requests.assert_called_with(
            "https://www.filmweb.pl/api/v1/jwt",
            cookies={"_artuser_prm": "secret"},
            timeout=10,
        )

    @patch("backup.api.requests.get")
    def test_fetch_fails(self, mock_requests: Mock):
        # given
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_response.raise_for_status.side_effect = requests.HTTPError(
            "401 Client Error: Unauthorized for url: https://example.com"
        )
        mock_requests.return_value = mock_response
        # expect
        with self.assertRaises(FilmwebError) as e:
            self.api.fetch("/test", True)
        self.assertEqual(
            e.exception.args[0], "Failed to fetch data due to unhandled exception"
        )
        self.assertEqual(
            e.exception.__cause__.args[0],
            "401 Client Error: Unauthorized for url: https://example.com",
        )
        # and
        mock_requests.assert_called_once()

    @patch("backup.api.requests.get")
    @patch("backup.api.FilmwebAPI.fetch_token")
    def test_fetch_fails_updates_jwt_token(
        self, mock_fetch_token: Mock, mock_requests: Mock
    ):
        # given
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"status": "ok"}
        mock_response.raise_for_status.side_effect = [
            requests.HTTPError(f"400 Client Error"),
            None,
        ]
        mock_requests.return_value = mock_response
        # and
        mock_fetch_token.return_value = "new-jwt"

        # when
        self.api.fetch("/test", True)
        # then
        self.assertEqual(mock_requests.call_count, 2)
        mock_requests.assert_has_calls(
            [
                call(
                    "https://www.filmweb.pl/api/v1/test",
                    headers={"X-Locale": "pl_PL"},
                    cookies={"JWT": "jwt"},
                    timeout=10,
                ),
                call().raise_for_status(),
                call(
                    "https://www.filmweb.pl/api/v1/test",
                    headers={"X-Locale": "pl_PL"},
                    cookies={"JWT": "new-jwt"},
                    timeout=10,
                ),
                call().raise_for_status(),
                call().json(),
            ]
        )
        # and
        mock_fetch_token.assert_called_once()

    @patch("backup.api.requests.get")
    def test_fetch_204(self, mock_requests: Mock):
        # given
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_response.text = ""
        mock_requests.return_value = mock_response

        # when
        result = self.api.fetch("/test", True)
        # then
        self.assertIsNone(result)
        # and
        mock_requests.assert_called_once_with(
            "https://www.filmweb.pl/api/v1/test",
            headers={"X-Locale": "pl_PL"},
            cookies={"JWT": "jwt"},
            timeout=10,
        )

    @patch("backup.api.requests.get")
    def test_fetch_succeeds(self, mock_requests: Mock):
        # given
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.return_value = mock_response

        # when
        result = self.api.fetch("/test", True)
        # then
        self.assertEqual(result, {"status": "ok"})
        # and
        mock_requests.assert_called_once_with(
            "https://www.filmweb.pl/api/v1/test",
            headers={"X-Locale": "pl_PL"},
            cookies={"JWT": "jwt"},
            timeout=10,
        )

    @patch("backup.api.FilmwebAPI.fetch")
    def test_fetch_user_details_with_name(self, mock_fetch: Mock):
        # given
        mock_details = {
            "id": 1234567,
            "name": "johndoe",
            "personalData": {
                "firstname": "John",
                "surname": "Doe",
            },
        }
        mock_fetch.return_value = mock_details

        # when
        result = self.api.fetch_user_details()
        # then
        self.assertEqual(result, UserDetails(1234567, "johndoe", "John Doe"))
        # and
        mock_fetch.assert_called_once_with("/logged/info", True)

    @patch("backup.api.FilmwebAPI.fetch")
    def test_fetch_user_details_without_name(self, mock_fetch: Mock):
        # given
        mock_details = {
            "id": 1234567,
            "name": "johndoe",
        }
        mock_fetch.return_value = mock_details

        # when
        result = self.api.fetch_user_details()
        # then
        self.assertEqual(result, UserDetails(1234567, "johndoe", None))
        # and
        mock_fetch.assert_called_once_with("/logged/info", True)

    @patch("backup.api.FilmwebAPI.fetch")
    def test_fetch_user_ratings(self, mock_fetch: Mock):
        # given
        mock_fetch.side_effect = [
            [
                {
                    "rate": 8,
                    "entity": 743825,
                    "favorite": True,
                    "viewDate": 20231220,
                    "timestamp": 1725664955310,
                }
            ],
            [
                {
                    "rate": 8,
                    "entity": 875717,
                    "viewDate": 20221218,
                    "timestamp": 1729188998841,
                }
            ],
            [],
        ]

        # when
        result = self.api.fetch_user_ratings()
        # then
        self.assertEqual(
            result,
            [
                UserRating(743825, 8, True, 20231220),
                UserRating(875717, 8, False, 20221218),
            ],
        )
        # and
        self.assertEqual(mock_fetch.call_count, 3)
        mock_fetch.assert_has_calls(
            [
                call("/logged/vote/title/film?page=1", True),
                call("/logged/vote/title/film?page=2", True),
                call("/logged/vote/title/film?page=3", True),
            ]
        )

    @patch("backup.api.FilmwebAPI.fetch")
    def test_fetch_user_friends(self, mock_fetch: Mock):
        # given
        mock_details = {
            "1234567": {
                "name": "johndoe",
            },
            "12345678": {"name": "janedoe", "firstname": "Jane"},
            "123456789": {"name": "joedoe", "firstname": "Joe", "surname": "Doe"},
        }
        mock_fetch.return_value = mock_details

        # when
        result = self.api.fetch_user_friends()
        # then
        self.assertEqual(
            result,
            [
                UserDetails(1234567, "johndoe", None),
                UserDetails(12345678, "janedoe", "Jane"),
                UserDetails(123456789, "joedoe", "Joe Doe"),
            ],
        )
        # and
        mock_fetch.assert_called_once_with("/logged/friends", True)

    @patch("backup.api.FilmwebAPI.fetch")
    def test_fetch_user_friends_similarities(self, mock_fetch: Mock):
        # given
        mock_details = [[1, 72.16858, 332], [2, 71.22369, 96], [3, 54.450515, 79]]
        mock_fetch.return_value = mock_details

        # when
        result = self.api.fetch_user_friends_similarities()
        # then
        self.assertEqual(
            result,
            [
                UserSimilarity(id=1, similarity=72.16858, movies=332),
                UserSimilarity(id=2, similarity=71.22369, movies=96),
                UserSimilarity(id=3, similarity=54.450515, movies=79),
            ],
        )
        # and
        mock_fetch.assert_called_once_with("/logged/friends/similarities", True)

    @patch("backup.api.FilmwebAPI.fetch")
    def test_fetch_friend_ratings(self, mock_fetch: Mock):
        # given
        mock_fetch.side_effect = [
            [
                {
                    "rate": 8,
                    "entity": 743825,
                    "favorite": True,
                    "viewDate": 20231220,
                    "timestamp": 1725664955310,
                }
            ],
            [
                {
                    "rate": 8,
                    "entity": 875717,
                    "viewDate": 20221218,
                    "timestamp": 1729188998841,
                }
            ],
            [],
        ]

        # when
        result = self.api.fetch_friend_ratings("johndoe")
        # then
        self.assertEqual(
            result,
            [
                UserRating(743825, 8, True, 20231220),
                UserRating(875717, 8, False, 20221218),
            ],
        )
        # and
        self.assertEqual(mock_fetch.call_count, 3)
        mock_fetch.assert_has_calls(
            [
                call("/logged/friend/johndoe/vote/title/film?page=1", True),
                call("/logged/friend/johndoe/vote/title/film?page=2", True),
                call("/logged/friend/johndoe/vote/title/film?page=3", True),
            ]
        )

    @patch("backup.api.FilmwebAPI.fetch")
    def test_fetch_movie_details_title(self, mock_fetch: Mock):
        # given
        mock_details = {
            "year": 2006,
            "title": {"title": "Renaissance", "country": "PL", "lang": "pl"},
            "originalTitle": {
                "title": "Renaissance",
                "country": "FR",
                "lang": "fr",
                "original": True,
            },
            "genres": [
                {"id": 24, "name": {"text": "Thriller"}, "nameKey": "24"},
                {"id": 77, "name": {"text": "Animacja dla dorosłych"}, "nameKey": "77"},
            ],
            "duration": 96,
            "directors": [{"id": 1161002, "name": "Sergio Pablos"}],
            "mainCast": [{"id": 46520, "name": "Jason Schwartzman"}],
            "countries": [{"id": 20, "code": "ES"}],
        }
        mock_fetch.return_value = mock_details

        # when
        result = self.api.fetch_movie_details(743825)
        # then
        self.assertEqual(
            result,
            Movie(
                id=743825,
                title="Renaissance",
                originalTitle="Renaissance",
                internationalTitle=None,
                year=2006,
                genres=[Genre(24, "Thriller"), Genre(77, "Animacja dla dorosłych")],
                directors=[Director(1161002, "Sergio Pablos")],
                duration=96,
                countries=[Country(20, "ES")],
                cast=[Cast(46520, "Jason Schwartzman")],
            ),
        )
        # and
        mock_fetch.assert_called_once_with("/film/743825/preview")

    @patch("backup.api.FilmwebAPI.fetch")
    def test_fetch_movie_details_original_title(self, mock_fetch: Mock):
        # given
        mock_details = {
            "year": 2006,
            "originalTitle": {
                "title": "Renaissance",
                "country": "FR",
                "lang": "fr",
                "original": True,
            },
            "genres": [
                {"id": 24, "name": {"text": "Thriller"}, "nameKey": "24"},
                {"id": 77, "name": {"text": "Animacja dla dorosłych"}, "nameKey": "77"},
            ],
            "duration": 96,
            "directors": [{"id": 1161002, "name": "Sergio Pablos"}],
            "mainCast": [{"id": 46520, "name": "Jason Schwartzman"}],
            "countries": [{"id": 20, "code": "ES"}],
        }
        mock_fetch.return_value = mock_details

        # when
        result = self.api.fetch_movie_details(743825)
        # then
        self.assertEqual(
            result,
            Movie(
                id=743825,
                title=None,
                originalTitle="Renaissance",
                internationalTitle=None,
                year=2006,
                genres=[Genre(24, "Thriller"), Genre(77, "Animacja dla dorosłych")],
                directors=[Director(1161002, "Sergio Pablos")],
                duration=96,
                countries=[Country(20, "ES")],
                cast=[Cast(46520, "Jason Schwartzman")],
            ),
        )
        # and
        mock_fetch.assert_called_once_with("/film/743825/preview")

    @patch("backup.api.FilmwebAPI.fetch")
    def test_fetch_movie_rating(self, mock_fetch: Mock):
        # given
        mock_details = {
            "count": 429,
            "rate": 6.00699,
            "countWantToSee": 1284,
            "countVote2": 6,
            "countVote3": 27,
            "countVote4": 46,
            "countVote5": 62,
            "countVote6": 93,
            "countVote7": 84,
            "countVote8": 70,
            "countVote9": 18,
            "countVote10": 11,
        }
        mock_fetch.return_value = mock_details

        # when
        result = self.api.fetch_movie_rating(743825)
        # then
        self.assertEqual(
            result,
            MovieRating(
                movie_id=743825,
                count=429,
                rate=6.00699,
                countWantToSee=1284,
                countVote1=0,
                countVote2=6,
                countVote3=27,
                countVote4=46,
                countVote5=62,
                countVote6=93,
                countVote7=84,
                countVote8=70,
                countVote9=18,
                countVote10=11,
            ),
        )
        # and
        mock_fetch.assert_called_once_with("/film/743825/rating")
