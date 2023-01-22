from enum import Enum

from .models import Log
from datetime import datetime
from django.utils import timezone


class LogLevels(Enum):
    degug = 0
    info = 1
    warning = 2
    error = 3


def log(message, level=LogLevels.info):
    l = Log(
        timestamp=datetime.now(tz=timezone.utc),
        message=message,
        level=level.value
    )
    l.save()