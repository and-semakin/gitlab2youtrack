import re


def get_attachments_urls(message):
    attachments = re.compile(r'\[[^ \t\n\r\f\v\[\]]+]\(([^ \t\n\r\f\v\[\]]+)\)')
    matches = re.findall(attachments, message)
    return matches

