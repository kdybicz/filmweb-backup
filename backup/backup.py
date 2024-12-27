import json
import sys

from api import fetch_movie_details, fetch_user_details, fetch_user_ratings

def main() -> int:
  jwt = "<ENTER_JWT_HERE>"
  
  # user_details = fetch_user_details(jwt)
  # print(json.dumps(user_details))

  # user_ratings = fetch_user_ratings(jwt)
  # print(json.dumps(user_ratings))

  movie_details = fetch_movie_details(287740, jwt)
  print(json.dumps(movie_details))

  return 0

if __name__ == '__main__':
  sys.exit(main())
