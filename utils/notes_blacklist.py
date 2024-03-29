import re


patterns = [
    re.compile(r'assigned to @\w+'),
    re.compile(r'unassigned @\w+'),
    re.compile(r'assigned to @\w+ and unassigned @\w+'),

    re.compile(r'moved to [\w_-]*#\d+'),
    re.compile(r'closed'),
    re.compile(r'closed via commit \w{40}'),
    re.compile(r'closed via merge request !\d+'),
    re.compile(r'reopened'),

    re.compile(r'changed the description'),
    re.compile(r'changed time estimate to .+'),
    re.compile(r'changed title from \*\*.+\*\* to \*\*.+\*\*'),
    re.compile(r'marked the task \*\*.+\*\* as completed'),
    re.compile(r'marked the task \*\*.+\*\* as incomplete'),
    re.compile(r'created branch \[\s*`\d+-[\w_-]*`\s*\]\(.+\)'),

    re.compile(r'added (\d{1,2}d)?\s?(\d{1,2}h)?\s?(\d{1,2}m)? of time spent at \d{4}-\d{2}-\d{2}'),

    re.compile(r'mentioned in issue [-\w]*#\d+'),
    re.compile(r'mentioned in merge request !\d+'),
    re.compile(r'mentioned in commit \w{40}'),

    re.compile(r'added( [\w_-]*~\d+)+ label(s)?'),
    re.compile(r'removed( [\w_-]*~\d+)+ label(s)?'),
    re.compile(r'added( [\w_-]*~\d+)+ and removed( [\w_-]*~\d+)+ labels'),
]


def is_blacklisted(message):
    for p in patterns:
        if p.match(message):
            return True

    return False
