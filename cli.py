import logging
from argparse import ArgumentParser, Namespace

from backup.backup import FilmwebBackup
from backup.utils.logging import RotatingFileOnStartHandler


def setup_logging(level=logging.DEBUG, log_file="logs/app.log") -> logging.Logger:
    LOG_FORMAT = "%(asctime)s  %(levelname)-8s  %(message)s"

    logger = logging.getLogger("filmweb")
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


def parse_args(args: list[str] | None = None) -> Namespace:
    """Define CLI parameters"""

    parser = ArgumentParser(
        prog="filmweb",
        description="Filmweb account information backup tool",
    )
    parser.add_argument(
        "-t",
        "--token",
        help="User token from the _artuser_prm cookie",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-e",
        "--export",
        help="Should export user details",
        action="store_true",
    )
    parser.add_argument(
        "-ee",
        "--extended-export",
        help="Should export user details incl. friends",
        action="store_true",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="increase output verbosity",
        action="store_true",
    )

    return parser.parse_args(args)


def main(argv: list[str] | None = None) -> int:
    """main function"""

    args = parse_args(argv)

    if args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logger = setup_logging(level=log_level)

    try:
        filmweb = FilmwebBackup.from_secret(args.token)
        user = filmweb.backup()

        if args.export or args.extended_export:
            if args.extended_export:
                filmweb.export_all()
            else:
                filmweb.export(user)
    except Exception as e:
        logger.error(e, stack_info=True)
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
