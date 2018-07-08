import dateutil.parser

"""
    Examples:
    2017-12-06T05:32:16.136Z
    2017-12-19T04:40:56.882Z
    2017-12-19T04:40:57.507Z
    2017-12-12T04:48:19.351Z
"""


def reformat_datetime(message_time):
    dt = dateutil.parser.parse(message_time)
    return dt.strftime('%d.%m.%Y %H:%M')
