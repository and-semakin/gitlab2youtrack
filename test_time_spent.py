import pytest
from datetime import timedelta

from time_spent import get_time_spent, timedelta_to_string


@pytest.mark.parametrize(
    'message, td',
    (
        ('added 5h of time spent at 2018-07-04', timedelta(hours=5)),
        ('added 4h of time spent at 2018-04-27', timedelta(hours=4)),
        ('added 2h 30m of time spent at 2018-06-05', timedelta(hours=2, minutes=30)),
        ('added 30m of time spent at 2018-06-29', timedelta(minutes=30)),
        ('added 1h 30m of time spent at 2018-06-13', timedelta(hours=1, minutes=30)),
        ('added 10m of time spent at 2018-06-01', timedelta(minutes=10)),
        ('added 2d 10h 10m of time spent at 2018-06-01', timedelta(days=2, hours=10, minutes=10)),
        ('asdasdqwe', timedelta()),
        ('', timedelta())
    )
)
def test_discussions_count(message, td):
    r = get_time_spent(message)
    assert r == td


@pytest.mark.parametrize(
    'td, td_str',
    (
        (timedelta(), '0d 0h 0m'),
        (timedelta(days=10), '10d 0h 0m'),
        (timedelta(minutes=50), '0d 0h 50m'),
        (timedelta(hours=5, minutes=30), '0d 5h 30m'),
        (timedelta(minutes=90), '0d 1h 30m'),
    )
)
def test_timedelta_to_string(td, td_str):
    assert timedelta_to_string(td) == td_str
