from datetime import datetime


def current_time_in_seconds() -> int:
    return int(datetime.utcnow().timestamp())
