
import logging
import sys

from backup.api import FilmwebError
from backup.backup import FilmwebBackup

def setup_logging(level=logging.DEBUG) -> logging.Logger:
  logger = logging.getLogger("filmweb")
  logger.setLevel(level)

  # Create a console handler
  ch = logging.StreamHandler()
  ch.setLevel(level)

  logger.addHandler(ch)

  return logger

if __name__ == "__main__":
  secret = ""

  logger = setup_logging()

  try:
    filmweb = FilmwebBackup.from_secret(secret)
    filmweb.backup()
    filmweb.export_all()
  except FilmwebError as e:
    logger.error(e)
    sys.exit(-1)

  sys.exit(0)
