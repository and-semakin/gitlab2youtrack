import re


def replace_numbered_checkboxes(msg):
    if not msg:
        return ''

    return re.sub(
        r'^(?P<num>\d+\.) (?P<checkbox>\[(x| )\]) (?P<text>.*)$',
        r'- \g<checkbox> \g<num> \g<text>',
        msg,
        flags=re.MULTILINE)
