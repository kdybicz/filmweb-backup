import os
from logging.handlers import RotatingFileHandler


class RotatingFileOnStartHandler(RotatingFileHandler):
    def __init__(
        self,
        filename,
        mode="a",
        maxBytes=0,
        backupCount=0,
        encoding=None,
        delay=False,
        errors=None,
    ) -> None:
        # Check if log exists and should therefore be rolled
        needRoll = os.path.isfile(filename)

        # Create a rotating file handler
        fh = super().__init__(
            filename,
            mode=mode,
            maxBytes=maxBytes,
            backupCount=backupCount,
            encoding=encoding,
            delay=delay,
            errors=errors,
        )

        # Roll the log only if it already exists
        if needRoll:
            self.doRollover()
