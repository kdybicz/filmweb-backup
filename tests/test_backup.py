import unittest
from unittest.mock import MagicMock, Mock, call, patch

from backup.backup import FilmwebBackup
from backup.data import UserDetails


class TestFilmwebBackup(unittest.TestCase):
  def test_backup_movie_no_update_needed(self):
    # given
    mock_api = MagicMock()
    mock_db = MagicMock()
    mock_db.should_update_movie.return_value = False
    mock_db.should_update_movie_rating.return_value = False
    # and
    backup = FilmwebBackup(mock_db, mock_api)

    # when
    backup.backup_movie(1)
    # then
    mock_db.should_update_movie.assert_called_once_with(1)
    mock_db.should_update_movie_rating.assert_called_once_with(1)
    # and
    mock_api.fetch_movie_details.assert_not_called()
    mock_db.upsert_movie.assert_not_called()
    mock_api.fetch_movie_rating.assert_not_called()
    mock_db.upsert_movie_rating.assert_not_called()

  def test_backup_movie_update_needed(self):
    # given
    mock_api = MagicMock()
    mock_movie_details = MagicMock()
    mock_api.fetch_movie_details.return_value = mock_movie_details
    mock_movie_rating = MagicMock()
    mock_api.fetch_movie_rating.return_value = mock_movie_rating
    # and
    mock_db = MagicMock()
    mock_db.should_update_movie.return_value = True
    mock_db.should_update_movie_rating.return_value = True
    # and
    backup = FilmwebBackup(mock_db, mock_api)

    # when
    backup.backup_movie(1)
    # then
    mock_db.should_update_movie.assert_called_once_with(1)
    mock_db.should_update_movie_rating.assert_called_once_with(1)
    # and
    mock_api.fetch_movie_details.assert_called_once_with(1)
    mock_db.upsert_movie.assert_called_once_with(mock_movie_details)
    mock_api.fetch_movie_rating.assert_called_once_with(1)
    mock_db.upsert_movie_rating.assert_called_once_with(mock_movie_rating)

  @patch("backup.backup.FilmwebBackup.backup_movie")
  def test_backup_user(self, mock_backup_movie: Mock):
    # given
    mock_user_details = MagicMock()
    mock_user_details.id = 1
    mock_user_rating = MagicMock()
    mock_user_rating.movie_id = 2
    mock_user_similarity = MagicMock()
    mock_friend_details = MagicMock()
    mock_friend_details.id = 3
    mock_friend_details.name = "johndoe"
    mock_friend_rating = MagicMock()
    mock_friend_rating.movie_id = 2
    mock_movie_rating = MagicMock()
    # and
    mock_api = MagicMock()
    mock_api.fetch_user_ratings.return_value = [mock_user_rating]
    mock_api.fetch_user_friends.return_value = [mock_friend_details]
    mock_api.fetch_user_friends_similarities.return_value = [mock_user_similarity]
    mock_api.fetch_friend_ratings.return_value = [mock_friend_rating]
    mock_api.fetch_movie_rating.return_value = mock_movie_rating
    # and
    mock_db = MagicMock()
    mock_db.should_update_user.return_value = True
    # and
    backup = FilmwebBackup(mock_db, mock_api)

    # when
    backup.backup_user(mock_user_details)
    # then
    mock_api.fetch_user_friends_similarities.assert_called_once()
    mock_api.fetch_user_ratings.assert_called_once()
    mock_api.fetch_friend_ratings.assert_called_once_with(mock_friend_details.name)
    # and
    mock_db.should_update_user.assert_has_calls([
      call(mock_user_details.id, 60),
      call(mock_friend_details.id)
    ])
    mock_db.upsert_user_details.assert_has_calls([
      call(mock_user_details),
      call(mock_friend_details)
    ])
    mock_db.upsert_ratings.assert_has_calls([
      call(mock_user_details.id, [mock_user_rating]),
      call(mock_friend_details.id, [mock_friend_rating])
    ])
    mock_db.upsert_similar_users.assert_called_once_with(mock_user_details.id, [mock_user_similarity])
    # and
    mock_backup_movie.assert_has_calls([
      call(mock_user_rating.movie_id),
      call(mock_friend_rating.movie_id),
    ])
