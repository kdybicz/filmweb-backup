
import sys

from backup.api import FilmwebException
from backup.backup import FilmwebBackup


if __name__ == '__main__':
  jwt = ""

  try:
    filmweb = FilmwebBackup()
    user = filmweb.backup(jwt)
    filmweb.export(user.id)
  except FilmwebException as e:
    print(e)
    sys.exit(-1)

  sys.exit(0)
