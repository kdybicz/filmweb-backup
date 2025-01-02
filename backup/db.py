from dataclasses import asdict, dataclass
import logging
import sqlite3

from .data import Genre, Movie, MovieRating, UserRating, UserDetails

@dataclass
class MovieRatingDetails:
  original_title: str
  international_title: str | None
  title: str | None
  year: int
  rate: float
  my_rate: int
  favorite: bool
  view_date: int
  duration: int | None
  genres: str
  directors: str
  cast: str
  countries: str

class FilmwebDB:
  def __init__(self, name: str = "filmweb.db"):
    self.logger = logging.getLogger("filmweb.db")

    self.con = sqlite3.connect(name)

    cur = self.con.cursor()
    try:
      cur.executescript("""
        BEGIN;

        CREATE TABLE IF NOT EXISTS movie(
          id INTEGER PRIMARY KEY,
          last_updated TEXT,
          orig_title TEXT NOT NULL,
          int_title TEXT,
          title TEXT,
          year INTEGER NOT NULL,
          duration INTEGER
        );
        CREATE TABLE IF NOT EXISTS movie_rating(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          movie_id INTEGER NOT NULL,
          count INTEGER NOT NULL,
          rate REAL NOT NULL,
          countWantToSee INTEGER NOT NULL,
          countVote1 INTEGER NOT NULL,
          countVote2 INTEGER NOT NULL,
          countVote3 INTEGER NOT NULL,
          countVote4 INTEGER NOT NULL,
          countVote5 INTEGER NOT NULL,
          countVote6 INTEGER NOT NULL,
          countVote7 INTEGER NOT NULL,
          countVote8 INTEGER NOT NULL,
          countVote9 INTEGER NOT NULL,
          countVote10 INTEGER NOT NULL,
          FOREIGN KEY (movie_id) REFERENCES movie (id) ON DELETE CASCADE ON UPDATE CASCADE
        );
        CREATE TABLE IF NOT EXISTS genre(
          id INTEGER PRIMARY KEY,
          name TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS movie_genres(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          movie_id INTEGER NOT NULL,
          genre_id INTEGER NOT NULL,
          FOREIGN KEY (movie_id) REFERENCES movie (id) ON DELETE CASCADE ON UPDATE CASCADE,
          FOREIGN KEY (genre_id) REFERENCES genre (id) ON DELETE CASCADE ON UPDATE CASCADE
        );
        CREATE TABLE IF NOT EXISTS director(
          id INTEGER PRIMARY KEY,
          name TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS movie_directors(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          movie_id INTEGER NOT NULL,
          director_id INTEGER NOT NULL,
          FOREIGN KEY (movie_id) REFERENCES movie (id) ON DELETE CASCADE ON UPDATE CASCADE,
          FOREIGN KEY (director_id) REFERENCES director (id) ON DELETE CASCADE ON UPDATE CASCADE
        );
        CREATE TABLE IF NOT EXISTS user(
          id INTEGER PRIMARY KEY,
          last_updated TEXT,
          name TEXT NOT NULL,
          display_name TEXT
        );
        CREATE TABLE IF NOT EXISTS rating(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER NOT NULL,
          movie_id INTEGER NOT NULL,
          rate INTEGER NOT NULL,
          favorite INTEGER NOT NULL,
          view_date INTEGER NOT NULL,
          FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE ON UPDATE CASCADE,
          FOREIGN KEY (movie_id) REFERENCES movie (id) ON DELETE CASCADE ON UPDATE CASCADE
        );
        CREATE TABLE IF NOT EXISTS cast(
          id INTEGER PRIMARY KEY,
          name TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS movie_cast(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          movie_id INTEGER NOT NULL,
          cast_id INTEGER NOT NULL,
          FOREIGN KEY (movie_id) REFERENCES movie (id) ON DELETE CASCADE ON UPDATE CASCADE,
          FOREIGN KEY (cast_id) REFERENCES cast (id) ON DELETE CASCADE ON UPDATE CASCADE
        );
        CREATE TABLE IF NOT EXISTS country(
          id INTEGER PRIMARY KEY,
          code TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS movie_countries(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          movie_id INTEGER NOT NULL,
          country_id INTEGER NOT NULL,
          FOREIGN KEY (movie_id) REFERENCES movie (id) ON DELETE CASCADE ON UPDATE CASCADE,
          FOREIGN KEY (country_id) REFERENCES country (id) ON DELETE CASCADE ON UPDATE CASCADE
        );

        CREATE TRIGGER IF NOT EXISTS movie_inserted AFTER INSERT ON movie
        FOR EACH ROW
        WHEN NEW.last_updated IS NULL
        BEGIN
          UPDATE movie SET last_updated = datetime() WHERE id = NEW.id;
        END;
        CREATE TRIGGER IF NOT EXISTS movie_updated AFTER UPDATE ON movie
        FOR EACH ROW
        WHEN OLD.last_updated = NEW.last_updated
        BEGIN
          UPDATE movie SET last_updated = datetime() WHERE id = NEW.id;
        END;
        CREATE TRIGGER IF NOT EXISTS user_inserted AFTER INSERT ON user
        FOR EACH ROW
        WHEN NEW.last_updated IS NULL
        BEGIN
          UPDATE user SET last_updated = datetime() WHERE id = NEW.id;
        END;
        CREATE TRIGGER IF NOT EXISTS user_updated AFTER UPDATE ON user
        FOR EACH ROW
        WHEN OLD.last_updated = NEW.last_updated
        BEGIN
          UPDATE user SET last_updated = datetime() WHERE id = NEW.id;
        END;

        COMMIT;
      """)

      self.con.commit()

      self.logger.debug("Database initialized!")
    finally:
      cur.close()


  def should_update_movie(self, movie_id: int) -> bool:
    cur = self.con.cursor()
    try:
      cur.execute("""
        SELECT 
          CASE 
            WHEN NOT EXISTS (
              SELECT 1 FROM movie WHERE id = :id
            ) THEN 1
            WHEN EXISTS (
              SELECT 1 FROM movie WHERE id = :id AND (last_updated IS NULL OR unixepoch() - unixepoch(last_updated) > 86400)
            ) THEN 1
            ELSE 0
          END
      """, ({ "id": movie_id }))
      return cur.fetchone()[0] == 1
    finally:
      cur.close()


  def upsert_movie(self, movie: Movie):
    cur = self.con.cursor()
    try:
      cur.execute("REPLACE INTO movie (id, orig_title, int_title, title, duration, year) VALUES (:id, :orig_title, :int_title, :title, :duration, :year);", {
        "id": movie.id,
        "orig_title": movie.originalTitle,
        "int_title": movie.internationalTitle,
        "title": movie.title,
        "duration": movie.duration,
        "year": movie.year,
      })

      genres = list(asdict(genre) for genre in movie.genres)
      cur.executemany("INSERT INTO genre (id, name) VALUES (:id, :name) ON CONFLICT DO NOTHING;", genres)

      movie_genres = list({ "movie_id": movie.id, "genre_id": genre.id } for genre in movie.genres)
      cur.executemany("INSERT INTO movie_genres (movie_id, genre_id) VALUES (:movie_id, :genre_id) ON CONFLICT DO NOTHING;", movie_genres)

      directors = list(asdict(director) for director in movie.directors)
      cur.executemany("INSERT INTO director (id, name) VALUES (:id, :name) ON CONFLICT DO NOTHING;", directors)

      movie_directors = list({ "movie_id": movie.id, "director_id": director.id } for director in movie.directors)
      cur.executemany("INSERT INTO movie_directors (movie_id, director_id) VALUES (:movie_id, :director_id) ON CONFLICT DO NOTHING;", movie_directors)

      cast = list(asdict(cast) for cast in movie.cast)
      cur.executemany("INSERT INTO cast (id, name) VALUES (:id, :name) ON CONFLICT DO NOTHING;", cast)

      movie_cast = list({ "movie_id": movie.id, "cast_id": cast.id } for cast in movie.cast)
      cur.executemany("INSERT INTO movie_cast (movie_id, cast_id) VALUES (:movie_id, :cast_id) ON CONFLICT DO NOTHING;", movie_cast)

      countries = list(asdict(country) for country in movie.countries)
      cur.executemany("INSERT INTO country (id, code) VALUES (:id, :code) ON CONFLICT DO NOTHING;", countries)

      movie_countries = list({ "movie_id": movie.id, "country_id": country.id } for country in movie.countries)
      cur.executemany("INSERT INTO movie_countries (movie_id, country_id) VALUES (:movie_id, :country_id) ON CONFLICT DO NOTHING;", movie_countries)

      self.con.commit()

      self.logger.debug(f"Stored movie details for movie id {movie.id}")
    finally:
      cur.close()


  def upsert_movie_rating(self, rating: MovieRating):
    cur = self.con.cursor()
    try:
      cur.execute("REPLACE INTO movie_rating (movie_id, count, rate, countWantToSee, countVote1, countVote2, countVote3, countVote4, countVote5, countVote6, countVote7, countVote8, countVote9, countVote10) VALUES (:movie_id, :count, :rate, :countWantToSee, :countVote1, :countVote2, :countVote3, :countVote4, :countVote5, :countVote6, :countVote7, :countVote8, :countVote9, :countVote10);", asdict(rating))

      self.con.commit()

      self.logger.debug(f"Stored movie rating for movie id {rating.movie_id}")
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

      self.logger.debug(f"Stored {len(genres)} movie genres!")
    finally:
      cur.close()


  def set_user_details(self, user_details: UserDetails):
    cur = self.con.cursor()
    try:
      cur.execute("REPLACE INTO user (id, name, display_name) VALUES (:id, :name, :display_name);", asdict(user_details))

      self.con.commit()

      self.logger.debug(f"Stored user details for user id {user_details.id}")
    finally:
      cur.close()


  def upsert_ratings(self, user_id: int, ratings: list[UserRating]):
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

      self.logger.debug(f"Stored user ratings for user id {user_id}")
    finally:
      cur.close()


  def get_user_rating(self, user_id: int) -> list[MovieRatingDetails]:
    cur = self.con.cursor()
    try:
      cur.execute("""
        SELECT m.orig_title,
          m.int_title,
          m.title,
          m.year,
          round(mr.rate, 1) rate,
          r.rate my_rate,
          r.favorite,
          r.view_date,
          m.duration,
          GROUP_CONCAT(distinct g.name) genres,
          GROUP_CONCAT(distinct d.name) directors,
          GROUP_CONCAT(distinct c.name) cast,
          GROUP_CONCAT(distinct ct.code) countries
        FROM `movie` m
          JOIN `rating` r ON r.movie_id = m.id
          JOIN `movie_genres` mg ON mg.movie_id = m.id
          JOIN `genre` g ON mg.genre_id = g.id
          JOIN `movie_rating` mr ON mr.movie_id = m.id
          JOIN `movie_directors` md ON md.movie_id = m.id
          JOIN `director` d ON md.director_id = d.id
          JOIN `movie_cast` mc ON mc.movie_id = m.id
          JOIN `cast` c ON mc.cast_id = c.id
          JOIN `movie_countries` mct ON mct.movie_id = m.id
          JOIN `country` ct ON mct.country_id = ct.id
        WHERE r.user_id = :id
        GROUP BY m.id;
      """, ({ "id": user_id }))
      return list(MovieRatingDetails(
        original_title=rating[0],
        international_title=rating[1],
        title=rating[2],
        year=rating[3],
        rate=rating[4],
        my_rate=rating[5],
        favorite=True if rating[6] == 1 else False,
        view_date=rating[7],
        duration=rating[8],
        genres=rating[9],
        directors=rating[10],
        cast=rating[11],
        countries=rating[12],
      ) for rating in cur.fetchall())
    finally:
      cur.close()


  def get_all_users(self) -> list[UserDetails]:
    cur = self.con.cursor()
    try:
      cur.execute("SELECT id, name, display_name FROM user;")
      return list(UserDetails(
        user[0],
        user[1],
        user[2],
      ) for user in cur.fetchall())
    finally:
      cur.close()
