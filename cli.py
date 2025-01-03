
import logging
import sys

from backup.api import FilmwebError
from backup.backup import FilmwebBackup
from backup.utils.logging import RotatingFileOnStartHandler


def setup_logging(level=logging.DEBUG, log_file='logs/app.log') -> logging.Logger:
    LOG_FORMAT = '%(asctime)s  %(levelname)-8s  %(message)s'

    logger = logging.getLogger('filmweb')
    logger.setLevel(level)

    # Create a console handler
    ch = logging.StreamHandler()
    ch.setLevel(level)

    # Create a rotating file handler
    fh = RotatingFileOnStartHandler(log_file, maxBytes=0, backupCount=10)
    fh.setLevel(level)

    # Create a formatter and set it for the handler
    formatter = logging.Formatter(fmt=LOG_FORMAT)
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # Add the screen log handler to the logger
    logger.addHandler(ch)

    # Add the file log handler to the logger
    logger.addHandler(fh)

    return logger

if __name__ == "__main__":
  secret = ""

  logger = setup_logging()

  try:
    filmweb = FilmwebBackup.from_secret(secret)
    filmweb.backup()
    filmweb.export_all()
  except Exception as e:
    logger.error(e)
    sys.exit(-1)

  sys.exit(0)
