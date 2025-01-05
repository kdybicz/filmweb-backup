
import datetime
import unittest

from backup.db import FilmwebDB


class TestFilmwebDB(unittest.TestCase):
  def setUp(self):
    self.db = FilmwebDB("file::memory:")

  def test_trigger_movie_inserted_without_last_updated(self):
    # given
    cur = self.db.con.cursor()
    cur.execute("INSERT INTO movie (id, orig_title, year) VALUES (1, 'title', 2000);")

    # when
    result = cur.execute("SELECT date_created, last_updated FROM movie WHERE id = 1;").fetchone()
    # then
    self.assertLessEqual(
      datetime.datetime.now(datetime.UTC) - datetime.datetime.fromisoformat(result[0]).replace(tzinfo=datetime.UTC),
      datetime.timedelta(minutes=1)
    )
    self.assertLessEqual(
      datetime.datetime.now(datetime.UTC) - datetime.datetime.fromisoformat(result[1]).replace(tzinfo=datetime.UTC),
      datetime.timedelta(minutes=1)
    )

  def test_trigger_movie_inserted_with_last_updated(self):
    # given
    cur = self.db.con.cursor()
    cur.execute("INSERT INTO movie (id, last_updated, orig_title, year) VALUES (1, '2000-01-01 00:00:00', 'title', 2000);")

    # when
    result = cur.execute("SELECT date_created, last_updated FROM movie WHERE id = 1;").fetchone()
    # then
    self.assertIsNone(result[0])
    self.assertEqual(result[1], "2000-01-01 00:00:00")

  def test_trigger_movie_updated_without_last_updated(self):
    # given
    cur = self.db.con.cursor()
    cur.execute("INSERT INTO movie (id, date_created, last_updated, orig_title, year) VALUES (1, '2000-01-01 00:00:00', '2000-01-01 00:00:00', 'title', 2000);")
    # and
    cur.execute("UPDATE movie SET title = 'title' WHERE id = 1;")

    # when
    result = cur.execute("SELECT date_created, last_updated FROM movie WHERE id = 1;").fetchone()
    # then
    self.assertEqual(result[0], "2000-01-01 00:00:00")
    self.assertLessEqual(
      datetime.datetime.now(datetime.UTC) - datetime.datetime.fromisoformat(result[1]).replace(tzinfo=datetime.UTC),
      datetime.timedelta(minutes=1)
    )

  def test_trigger_movie_updated_with_last_updated(self):
    # given
    cur = self.db.con.cursor()
    cur.execute("INSERT INTO movie (id, date_created, last_updated, orig_title, year) VALUES (1, '2000-01-01 00:00:00', '2000-01-01 00:00:00', 'title', 2000);")
    # and
    cur.execute("UPDATE movie SET title = 'title', last_updated = '2001-01-01 00:00:00' WHERE id = 1;")

    # when
    result = cur.execute("SELECT date_created, last_updated FROM movie WHERE id = 1;").fetchone()
    # then
    self.assertEqual(result[0], "2000-01-01 00:00:00")
    self.assertEqual(result[1], "2001-01-01 00:00:00")

  def test_trigger_movie_rating_inserted_without_last_updated(self):
    # given
    cur = self.db.con.cursor()
    cur.execute("INSERT INTO movie_rating (movie_id, count, rate, countWantToSee, countVote1, countVote2, countVote3, countVote4, countVote5, countVote6, countVote7, countVote8, countVote9, countVote10) VALUES (1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);")

    # when
    result = cur.execute("SELECT date_created, last_updated FROM movie_rating WHERE id = 1;").fetchone()
    # then
    self.assertLessEqual(
      datetime.datetime.now(datetime.UTC) - datetime.datetime.fromisoformat(result[0]).replace(tzinfo=datetime.UTC),
      datetime.timedelta(minutes=1)
    )
    self.assertLessEqual(
      datetime.datetime.now(datetime.UTC) - datetime.datetime.fromisoformat(result[1]).replace(tzinfo=datetime.UTC),
      datetime.timedelta(minutes=1)
    )

  def test_trigger_movie_rating_inserted_with_last_updated(self):
    # given
    cur = self.db.con.cursor()
    cur.execute("INSERT INTO movie_rating (movie_id, last_updated, count, rate, countWantToSee, countVote1, countVote2, countVote3, countVote4, countVote5, countVote6, countVote7, countVote8, countVote9, countVote10) VALUES (1, '2000-01-01 00:00:00', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);")

    # when
    result = cur.execute("SELECT date_created, last_updated FROM movie_rating WHERE id = 1;").fetchone()
    # then
    self.assertIsNone(result[0])
    self.assertEqual(result[1], "2000-01-01 00:00:00")

  def test_trigger_movie_rating_updated_without_last_updated(self):
    # given
    cur = self.db.con.cursor()
    cur.execute("INSERT INTO movie_rating (movie_id, date_created, last_updated, count, rate, countWantToSee, countVote1, countVote2, countVote3, countVote4, countVote5, countVote6, countVote7, countVote8, countVote9, countVote10) VALUES (1, '2000-01-01 00:00:00', '2000-01-01 00:00:00', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);")
    # and
    cur.execute("UPDATE movie_rating SET countWantToSee = 1 WHERE id = 1;")

    # when
    result = cur.execute("SELECT date_created, last_updated FROM movie_rating WHERE id = 1;").fetchone()
    # then
    self.assertEqual(result[0], "2000-01-01 00:00:00")
    self.assertLessEqual(
      datetime.datetime.now(datetime.UTC) - datetime.datetime.fromisoformat(result[1]).replace(tzinfo=datetime.UTC),
      datetime.timedelta(minutes=1)
    )

  def test_trigger_movie_rating_updated_with_last_updated(self):
    # given
    cur = self.db.con.cursor()
    cur.execute("INSERT INTO movie_rating (movie_id, date_created, last_updated, count, rate, countWantToSee, countVote1, countVote2, countVote3, countVote4, countVote5, countVote6, countVote7, countVote8, countVote9, countVote10) VALUES (1, '2000-01-01 00:00:00', '2000-01-01 00:00:00', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);")
    # and
    cur.execute("UPDATE movie_rating SET countWantToSee = 1, last_updated = '2001-01-01 00:00:00' WHERE id = 1;")

    # when
    result = cur.execute("SELECT date_created, last_updated FROM movie_rating WHERE id = 1;").fetchone()
    # then
    self.assertEqual(result[0], "2000-01-01 00:00:00")
    self.assertEqual(result[1], "2001-01-01 00:00:00")

  def test_trigger_user_inserted_without_last_updated(self):
    # given
    cur = self.db.con.cursor()
    cur.execute("INSERT INTO user (id, name) VALUES (1, 'johndoe');")

    # when
    result = cur.execute("SELECT date_created, last_updated FROM user WHERE id = 1;").fetchone()
    # then
    self.assertLessEqual(
      datetime.datetime.now(datetime.UTC) - datetime.datetime.fromisoformat(result[0]).replace(tzinfo=datetime.UTC),
      datetime.timedelta(minutes=1)
    )
    self.assertLessEqual(
      datetime.datetime.now(datetime.UTC) - datetime.datetime.fromisoformat(result[1]).replace(tzinfo=datetime.UTC),
      datetime.timedelta(minutes=1)
    )

  def test_trigger_user_inserted_with_last_updated(self):
    # given
    cur = self.db.con.cursor()
    cur.execute("INSERT INTO user (id, last_updated, name) VALUES (1, '2000-01-01 00:00:00', 'johndoe');")

    # when
    result = cur.execute("SELECT date_created, last_updated FROM user WHERE id = 1;").fetchone()
    # then
    self.assertIsNone(result[0])
    self.assertEqual(result[1], "2000-01-01 00:00:00")

  def test_trigger_user_updated_without_last_updated(self):
    # given
    cur = self.db.con.cursor()
    cur.execute("INSERT INTO user (id, date_created, last_updated, name) VALUES (1, '2000-01-01 00:00:00', '2000-01-01 00:00:00', 'johndoe');")
    # and
    cur.execute("UPDATE user SET name = 'janedoe' WHERE id = 1;")

    # when
    result = cur.execute("SELECT date_created, last_updated FROM user WHERE id = 1;").fetchone()
    # then
    self.assertEqual(result[0], "2000-01-01 00:00:00")
    self.assertLessEqual(
      datetime.datetime.now(datetime.UTC) - datetime.datetime.fromisoformat(result[1]).replace(tzinfo=datetime.UTC),
      datetime.timedelta(minutes=1)
    )

  def test_trigger_user_updated_with_last_updated(self):
    # given
    cur = self.db.con.cursor()
    cur.execute("INSERT INTO user (id, date_created, last_updated, name) VALUES (1, '2000-01-01 00:00:00', '2000-01-01 00:00:00', 'johndoe');")
    # and
    cur.execute("UPDATE user SET name = 'janedoe', last_updated = '2001-01-01 00:00:00' WHERE id = 1;")

    # when
    result = cur.execute("SELECT date_created, last_updated FROM user WHERE id = 1;").fetchone()
    # then
    self.assertEqual(result[0], "2000-01-01 00:00:00")
    self.assertEqual(result[1], "2001-01-01 00:00:00")

  def test_should_update_movie_no_movie(self):
    # when
    result = self.db.should_update_movie(1)
    # then
    self.assertTrue(result)

  def test_should_update_movie_fresh_movie(self):
    # given
    cur = self.db.con.cursor()
    cur.execute("INSERT INTO movie (id, orig_title, year) VALUES (1, 'John Doe Movie', 2020);")

    # when
    result = self.db.should_update_movie(1)
    # then
    self.assertFalse(result)

  def test_should_update_movie_stale_movie(self):
    # given
    cur = self.db.con.cursor()
    cur.execute("INSERT INTO movie (id, last_updated, orig_title, year) VALUES (1, '2000-01-01 00:00:00', 'John Doe Movie', 2020);")

    # when
    result = self.db.should_update_movie(1)
    # then
    self.assertTrue(result)

  def test_should_update_movie_no_movie_rating(self):
    # when
    result = self.db.should_update_movie_rating(1)
    # then
    self.assertTrue(result)

  def test_should_update_movie_rating_fresh_movie_rating(self):
    # given
    cur = self.db.con.cursor()
    cur.execute("INSERT INTO movie_rating (movie_id, count, rate, countWantToSee, countVote1, countVote2, countVote3, countVote4, countVote5, countVote6, countVote7, countVote8, countVote9, countVote10) VALUES (1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);")

    # when
    result = self.db.should_update_movie_rating(1)
    # then
    self.assertFalse(result)

  def test_should_update_movie_rating_stale_movie_rating(self):
    # given
    cur = self.db.con.cursor()
    cur.execute("INSERT INTO movie_rating (movie_id, last_updated, count, rate, countWantToSee, countVote1, countVote2, countVote3, countVote4, countVote5, countVote6, countVote7, countVote8, countVote9, countVote10) VALUES (1, '2000-01-01 00:00:00', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);")

    # when
    result = self.db.should_update_movie_rating(1)
    # then
    self.assertTrue(result)

  def test_should_update_user_no_user(self):
    # when
    result = self.db.should_update_user(1)
    # then
    self.assertTrue(result)

  def test_should_update_user_fresh_user(self):
    # given
    cur = self.db.con.cursor()
    cur.execute("INSERT INTO user (id, name) VALUES (1, 'johndoe');")

    # when
    result = self.db.should_update_user(1)
    # then
    self.assertFalse(result)

  def test_should_update_user_stale_user(self):
    # given
    cur = self.db.con.cursor()
    cur.execute("INSERT INTO user (id, last_updated, name) VALUES (1, '2000-01-01 00:00:00', 'johndoe');")

    # when
    result = self.db.should_update_user(1)
    # then
    self.assertTrue(result)
