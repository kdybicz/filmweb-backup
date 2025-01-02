
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
    result = cur.execute("SELECT last_updated FROM movie WHERE id = 1;")
    # then
    self.assertLessEqual(
      datetime.datetime.now(datetime.UTC) - datetime.datetime.fromisoformat(result.fetchone()[0]).replace(tzinfo=datetime.UTC),
      datetime.timedelta(minutes=1)
    )

  def test_trigger_movie_inserted_with_last_updated(self):
    # given
    cur = self.db.con.cursor()
    cur.execute("INSERT INTO movie (id, last_updated, orig_title, year) VALUES (1, '2000-01-01 00:00:00', 'title', 2000);")

    # when
    result = cur.execute("SELECT last_updated FROM movie WHERE id = 1;")
    # then
    self.assertEqual(result.fetchone()[0], "2000-01-01 00:00:00")

  def test_trigger_movie_updated_without_last_updated(self):
    # given
    cur = self.db.con.cursor()
    cur.execute("INSERT INTO movie (id, last_updated, orig_title, year) VALUES (1, '2000-01-01 00:00:00', 'title', 2000);")
    # and
    cur.execute("UPDATE movie SET title = 'title' WHERE id = 1;")

    # when
    result = cur.execute("SELECT last_updated FROM movie WHERE id = 1;")
    # then
    self.assertLessEqual(
      datetime.datetime.now(datetime.UTC) - datetime.datetime.fromisoformat(result.fetchone()[0]).replace(tzinfo=datetime.UTC),
      datetime.timedelta(minutes=1)
    )

  def test_trigger_movie_updated_with_last_updated(self):
    # given
    cur = self.db.con.cursor()
    cur.execute("INSERT INTO movie (id, last_updated, orig_title, year) VALUES (1, '2000-01-01 00:00:00', 'title', 2000);")
    # and
    cur.execute("UPDATE movie SET title = 'title', last_updated = '2001-01-01 00:00:00' WHERE id = 1;")

    # when
    result = cur.execute("SELECT last_updated FROM movie WHERE id = 1;")
    # then
    self.assertEqual(result.fetchone()[0], "2001-01-01 00:00:00")

  def test_trigger_user_inserted_without_last_updated(self):
    # given
    cur = self.db.con.cursor()
    cur.execute("INSERT INTO user (id, name) VALUES (1, 'johndoe');")

    # when
    result = cur.execute("SELECT last_updated FROM user WHERE id = 1;")
    # then
    self.assertLessEqual(
      datetime.datetime.now(datetime.UTC) - datetime.datetime.fromisoformat(result.fetchone()[0]).replace(tzinfo=datetime.UTC),
      datetime.timedelta(minutes=1)
    )

  def test_trigger_user_inserted_with_last_updated(self):
    # given
    cur = self.db.con.cursor()
    cur.execute("INSERT INTO user (id, last_updated, name) VALUES (1, '2000-01-01 00:00:00', 'johndoe');")

    # when
    result = cur.execute("SELECT last_updated FROM user WHERE id = 1;")
    # then
    self.assertEqual(result.fetchone()[0], "2000-01-01 00:00:00")

  def test_trigger_user_updated_without_last_updated(self):
    # given
    cur = self.db.con.cursor()
    cur.execute("INSERT INTO user (id, last_updated, name) VALUES (1, '2000-01-01 00:00:00', 'johndoe');")
    # and
    cur.execute("UPDATE user SET name = 'janedoe' WHERE id = 1;")

    # when
    result = cur.execute("SELECT last_updated FROM user WHERE id = 1;")
    # then
    self.assertLessEqual(
      datetime.datetime.now(datetime.UTC) - datetime.datetime.fromisoformat(result.fetchone()[0]).replace(tzinfo=datetime.UTC),
      datetime.timedelta(minutes=1)
    )

  def test_trigger_user_updated_with_last_updated(self):
    # given
    cur = self.db.con.cursor()
    cur.execute("INSERT INTO user (id, last_updated, name) VALUES (1, '2000-01-01 00:00:00', 'johndoe');")
    # and
    cur.execute("UPDATE user SET name = 'janedoe', last_updated = '2001-01-01 00:00:00' WHERE id = 1;")

    # when
    result = cur.execute("SELECT last_updated FROM user WHERE id = 1;")
    # then
    self.assertEqual(result.fetchone()[0], "2001-01-01 00:00:00")

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


