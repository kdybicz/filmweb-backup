from dataclasses import asdict, dataclass
import sqlite3

from api import Genre, Movie, Rating, UserDetails

@dataclass
class MovieRating:
  title: str
  year: int
  rate: int
  favorite: bool
  view_date: int
  genres: str

class FilmwebDB:
  def __init__(self):
    self.con = sqlite3.connect("filmweb.db")

    cur = self.con.cursor()
    try:
      cur.execute("CREATE TABLE IF NOT EXISTS movie (id INTEGER PRIMARY KEY, title TEXT NOT NULL, year INTEGER NOT NULL);")
      cur.execute("CREATE TABLE IF NOT EXISTS genre (id INTEGER PRIMARY KEY, name TEXT NOT NULL);")
      cur.execute("CREATE TABLE IF NOT EXISTS movie_genres (id INTEGER PRIMARY KEY AUTOINCREMENT, movie_id INTEGER NOT NULL, genre_id INTEGER NOT NULL, FOREIGN KEY (movie_id) REFERENCES movie (id), FOREIGN KEY (genre_id) REFERENCES genre (id));")
      cur.execute("CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY, name TEXT NOT NULL, display_name TEXT);")
      cur.execute("CREATE TABLE IF NOT EXISTS rating (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, movie_id INTEGER NOT NULL, rate INTEGER NOT NULL, favorite INTEGER NOT NULL, view_date INTEGER NOT NULL, FOREIGN KEY (user_id) REFERENCES user (id), FOREIGN KEY (movie_id) REFERENCES movie (id));")
      self.con.commit()
    finally:
      cur.close()


  def has_movie(self, movie_id: int) -> bool:
    cur = self.con.cursor()
    try:
      cur.execute("SELECT EXISTS (SELECT 1 FROM movie WHERE id=:id LIMIT 1);", ({ "id": movie_id }))
      return cur.fetchone()[0] == 1
    finally:
      cur.close()


  def insert_movie(self, movie: Movie):
    cur = self.con.cursor()
    try:
      cur.execute("INSERT INTO movie (id, title, year) VALUES (:id, :title, :year);", asdict(movie))

      genres = list(asdict(genre) for genre in movie.genres)
      cur.executemany("INSERT INTO genre (id, name) VALUES (:id, :name) ON CONFLICT DO NOTHING;", genres)

      movie_genres = list({ "movie_id": movie.id, "genre_id": genre.id } for genre in movie.genres)
      cur.executemany("INSERT INTO movie_genres (movie_id, genre_id) VALUES (:movie_id, :genre_id);", movie_genres)

      self.con.commit()
    finally:
      cur.close()


  def upsert_genres(self, genres: list[Genre]):
    if (len(genres) == 0):
      return

    cur = self.con.cursor()
    try:
      rows = list(asdict(genre) for genre in genres)
      cur.executemany("INSERT INTO genre (id, name) VALUES (:id, :name) ON CONFLICT DO NOTHING;", rows)
      self.con.commit()
    finally:
      cur.close()
  

  def set_user_details(self, user_details: UserDetails):
    cur = self.con.cursor()
    try:
      cur.execute("DELETE FROM user WHERE id=:id;", { "id": user_details.id })
      cur.execute("INSERT INTO user (id, name, display_name) VALUES (:id, :name, :display_name);", asdict(user_details))
      self.con.commit()
    finally:
      cur.close()


  def upsert_ratings(self, user_id: int, ratings: list[Rating]):
    if (len(ratings) == 0):
      return

    cur = self.con.cursor()
    try:
      cur.execute("DELETE FROM rating WHERE user_id=:user_id;", { "user_id": user_id })

      rows = list({
        "user_id": user_id,
        "movie_id": rating.movie_id,
        "rate": rating.rate,
        "favorite": 1 if rating.favorite else 0,
        "view_date": rating.view_date
      } for rating in ratings)
      cur.executemany("INSERT INTO rating (user_id, movie_id, rate, favorite, view_date) VALUES (:user_id, :movie_id, :rate, :favorite, :view_date);", rows)
      self.con.commit()
    finally:
      cur.close()


  def get_user_rating(self, user_id: int) -> list[MovieRating]:
    cur = self.con.cursor()
    try:
      cur.execute("""
        SELECT m.title, m.year, r.rate, r.favorite, r.view_date, GROUP_CONCAT(g.name, ", ") genres
        FROM rating r
        JOIN movie m ON r.movie_id = m.id
        JOIN movie_genres mg ON mg.movie_id = m.id
        JOIN genre g ON mg.genre_id = g.id
        WHERE r.user_id = :id
        GROUP BY m.id;
      """, ({ "id": user_id }))
      return list(MovieRating(
        rating[0],
        rating[1],
        rating[2],
        True if rating[3] == 1 else False,
        rating[4],
        rating[5],
      ) for rating in cur.fetchall())
    finally:
      cur.close()



