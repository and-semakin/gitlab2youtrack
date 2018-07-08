import re


attachments = re.compile(r'\[[^ \t\n\r\f\v\[\]]+]\(([^ \t\n\r\f\v\[\]]+)\)')


def get_attachments_urls(message):
    if not message:
        return []

    matches = re.findall(attachments, message)
    return matches

