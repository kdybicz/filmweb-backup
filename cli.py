
import logging
import sys

from backup.api import FilmwebException
from backup.backup import FilmwebBackup

def setup_logging(level=logging.DEBUG) -> logging.Logger:
  logger = logging.getLogger('filmweb')
  logger.setLevel(level)

  # Create a console handler
  ch = logging.StreamHandler()
  ch.setLevel(level)

  logger.addHandler(ch)

  return logger

if __name__ == '__main__':
  jwt = ""

  logger = setup_logging()

  try:
    filmweb = FilmwebBackup()
    user = filmweb.backup(jwt)
    filmweb.export(user.id)
  except FilmwebException as e:
    logger.error(e)
    sys.exit(-1)

  sys.exit(0)
