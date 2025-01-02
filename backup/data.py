from dataclasses import dataclass

@dataclass(eq=True, repr=True)
class Genre:
  id: int
  name: str

@dataclass(eq=True, repr=True)
class Director:
  id: int
  name: str

@dataclass(eq=True, repr=True)
class Cast:
  id: int
  name: str

@dataclass(eq=True, repr=True)
class Country:
  id: int
  code: str

@dataclass(eq=True, repr=True)
class Movie:
  id: int
  title: str | None
  originalTitle: str
  internationalTitle: str | None
  year: int
  genres: list[Genre]
  duration: int
  directors: list[Director]
  cast: list[Cast]
  countries: list[Country]

@dataclass(eq=True, repr=True)
class MovieRating:
  movie_id: int
  count: int
  rate: float
  countWantToSee: int
  countVote1: int
  countVote2: int
  countVote3: int
  countVote4: int
  countVote5: int
  countVote6: int
  countVote7: int
  countVote8: int
  countVote9: int
  countVote10: int

@dataclass(eq=True, repr=True)
class UserRating:
  movie_id: int
  rate: int
  favorite: bool
  view_date: int

@dataclass(eq=True, repr=True)
class UserDetails:
  id: int
  name: str
  display_name: str | None
