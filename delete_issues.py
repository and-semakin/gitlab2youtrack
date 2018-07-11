from youtrack.connection import Connection

youtrack_url = 'http://youtrack.dev.kbinform.ru/'
youtrack_login = 'GitLab'
youtrack_password = 'gitlab'
youtrack = Connection(youtrack_url, youtrack_login, youtrack_password)

project_list = [
    'ezmp',
    'chel_taxi',
    'chel_medicine',
    'ekb_taxi',
    'ekb_medicine',
    'ekb_alcohol',
    'ekb_state_property',
    'ekb_building',
    'ekb_home_book',
    'ekb_investments',
    'ekb_advertising'
]

for _ in range(30):
    for p in project_list:
        issues = youtrack.get_issues(p, '', '', '')
        for i in issues:
            youtrack.delete_issue(i._data['id'])
