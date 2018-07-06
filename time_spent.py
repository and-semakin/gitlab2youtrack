import re
from datetime import timedelta

"""
    Examples:
        added 5h of time spent at 2018-07-04
        added 4h of time spent at 2018-04-27
        added 2h 30m of time spent at 2018-06-05
        added 30m of time spent at 2018-06-29
        added 1h 30m of time spent at 2018-06-13
        added 10m of time spent at 2018-06-01
"""


spent = re.compile(r'added ((?P<d>\d{1,2})d)?\s?((?P<h>\d{1,2})h)?\s?((?P<m>\d{1,2})m)?'
                   r' of time spent at \d{4}-\d{2}-\d{2}')


def get_time_spent(message):
    if not message:
        return timedelta()  # zero timedelta

    matches = re.match(spent, message)
    if not matches:
        return timedelta()  # zero timedelta

    d = int(matches.group('d') or 0)
    h = int(matches.group('h') or 0)
    m = int(matches.group('m') or 0)

    return timedelta(days=d, hours=h, minutes=m)


def timedelta_to_string(td):
    s = td.seconds

    d = td.days

    h = s // (60 * 60)
    s = s % (60 * 60)

    m = s // 60

    return '{d}d {h}h {m}m'.format(d=d, h=h, m=m)
