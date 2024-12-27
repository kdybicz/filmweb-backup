import unittest
from unittest.mock import call, patch, MagicMock

from backup.api import FilmwebError, fetch, fetch_user_details, fetch_user_ratings

class TestApi(unittest.TestCase):
  @patch("backup.api.requests")
  def test_fetch_fails(self, mock_requests):
    # given
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    mock_requests.get.return_value = mock_response

    # expect
    with self.assertRaises(FilmwebError):
      fetch('/test', 'jwt')

  @patch("backup.api.requests")
  def test_fetch_succeeds(self, mock_requests):
    # given
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "ok"}
    mock_requests.get.return_value = mock_response

    # when
    result = fetch('/test', 'jwt')
    # then
    self.assertEqual(result, {"status": "ok"})
    # and
    mock_requests.get.assert_called_once_with(
      "https://www.filmweb.pl/api/v1/test",
      headers={'X-Locale': 'pl_PL'},
      cookies={ "JWT": "jwt" },
      timeout=5
    )

  @patch("backup.api.fetch")
  def test_fetch_user_details_with_name(self, mock_fetch):
    # given
    mock_details = {
      "id": 1234567,
      "name": "johndoe",
      "email": "john.doe@example.com",
      "facebookId": "randomfacebookid",
      "personalData": {
        "firstname": "John",
        "surname": "Doe",
        "birthdateInt": 19700000,
        "sex": "M",
        "regulationsAcceptanceDate": "2018-06-01T00:00:00",
        "targetedAdvertisingConsent": True,
        "targetedAdvertisingLastChange": "2018-06-02T00:00:00",
        "filmwebMarketingConsent": False,
        "filmwebMarketingLastChange": "2018-06-03T00:00:00",
        "marketingConsent": False,
        "marketingLastChange": "2018-06-04T00:00:00",
        "productInformationConsent": False,
        "productInformationLastChange": "2018-06-05T00:00:00",
        "plusMarketingConsent": False
      },
      "prefs": {
          "city": 7
      }
    }
    mock_fetch.return_value = mock_details

    # when
    result = fetch_user_details('jwt')
    # then
    self.assertEqual(result, {'display_name': 'John Doe', 'id': 1234567, 'name': 'johndoe'})
    # and
    mock_fetch.assert_called_once_with('/logged/info', 'jwt')

  @patch("backup.api.fetch")
  def test_fetch_user_details_without_name(self, mock_fetch):
    # given
    mock_details = {
      "id": 1234567,
      "name": "johndoe",
      "email": "john.doe@example.com",
      "facebookId": "randomfacebookid",
      "prefs": {
          "city": 7
      }
    }
    mock_fetch.return_value = mock_details

    # when
    result = fetch_user_details('jwt')
    # then
    self.assertEqual(result, {'display_name': 'johndoe', 'id': 1234567, 'name': 'johndoe'})
    # and
    mock_fetch.assert_called_once_with('/logged/info', 'jwt')

  @patch("backup.api.fetch")
  def test_fetch_user_ratings(self, mock_fetch):
    # given
    mock_fetch.side_effect = [
      [
        {
            "rate": 8,
            "entity": 743825,
            "favorite": True,
            "viewDate": 20231220,
            "timestamp": 1725664955310
        },
        {
            "rate": 8,
            "entity": 875717,
            "viewDate": 20221218,
            "timestamp": 1729188998841
        }
      ],
      []
    ]

    # when
    result = fetch_user_ratings('jwt')
    # then
    self.assertEqual(result, [
        {
            "rate": 8,
            "movie_id": 743825,
            "favorite": True,
            "view_date": 20231220
        },
        {
            "rate": 8,
            "movie_id": 875717,
            "favorite": False,
            "view_date": 20221218
        }
      ]
    )
    # and
    mock_fetch.assert_has_calls([
      call('/logged/vote/title/film?page=1', 'jwt'),
      call('/logged/vote/title/film?page=2', 'jwt')
    ])

if __name__ == "__main__":
    unittest.main()
