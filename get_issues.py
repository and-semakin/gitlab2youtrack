import requests
from pprint import pprint
import getpass
from youtrack.connection import Connection
from youtrack.youtrack import YouTrackException

gitlab_url = 'https://gitlab.ezmp.kbinform.ru/api/v4/'
gitlab_api_token = '2FHbXaGd-i59EbeGV4dW'
gitlab_per_page = 1000

youtrack_url = 'http://youtrack.dev.kbinform.ru/'
youtrack_login = 'GitLab'
youtrack_password = 'gitlab'
youtrack = Connection(youtrack_url, youtrack_login, youtrack_password)


def get_user_by_id(id):
    users = {
        1: 'admin',
        2: 'admin',
        3: 'admin',
        5: 'AndreevAA',
        6: 'SemakinAE',
        7: 'BazhinKA',
        8: 'TyukovaAA',
        9: 'IgnatevYG',
        10: 'SemenovaEV',
        11: 'BabichAV',
        12: 'KuznetsovIV',
        13: 'StepanovAV',
        14: 'PetrushinDA',
        15: 'LegostaevV',
        16: 'mityashina',
        17: 'TaratuninSA',
    }
    return users[id]


def get_user_by_login(login):
    users = {
        'root': 'admin',
        'dovgal_ivan': 'admin',
        'okulov_artemy': 'admin',
        'gagara11': 'AndreevAA',
        'semakin': 'SemakinAE',
        'kabazhin': 'BazhinKA',
        'maroola': 'TyukovaAA',
        'naHDeMoHuyc': 'IgnatevYG',
        'katuxa': 'SemenovaEV',
        'avbabich': 'BabichAV',
        'iljakuzne': 'KuznetsovIV',
        'Alexey': 'StepanovAV',
        'Denis': 'PetrushinDA',
        'legostaev': 'LegostaevV',
        'MityashinaML': 'mityashina',
        'Legend072': 'TaratuninSA',
    }
    return users[login]

# youtrack project
yt_project_id = 'ezmp'
# yt_project_id = 'youtrack_test'
print(yt_project_id)
# create youtrack project if not exists
try:
    yt_project = youtrack.get_project(yt_project_id)
except YouTrackException:
    youtrack.create_project_detailed(yt_project_id, 'ЕЗМП', 'Единая Защищенная Мобильная Платформа', youtrack_login)
    yt_project = youtrack.get_project(yt_project_id)


# list gitlab projects
_projects = requests.get(f'{gitlab_url}projects?per_page={gitlab_per_page}&private_token={gitlab_api_token}').json()

# print(projects)
for p in _projects:
    project_id = p['id']
    project_path = p['path']
    issues = requests.get(f'{gitlab_url}projects/{project_id}/issues?scope=all'
                          f'&per_page={gitlab_per_page}&private_token={gitlab_api_token}').json()

    # print project name
    print()
    print('=' * 80)
    print(project_path)
    # pprint(p)
    # exit()

    for issue in issues:
        issue_iid = issue['iid']
        assignee = get_user_by_id(issue['assignee']['id']) if issue['assignee'] is not None else None
        summary = "[" + project_path + "] " + issue['title']
        description = issue['description']
        state = 'fixed' if issue['state'] == 'closed' else None
        response = youtrack.create_issue(yt_project_id, assignee, summary, description, state=state)
        yt_issue_id = response[0]['location'].split('/')[-1]
        # pprint(issue)
        print(" *", summary)

        comments = requests.get(
            f'{gitlab_url}projects/{project_id}/issues/{issue_iid}/'
            f'notes?per_page={gitlab_per_page}&private_token={gitlab_api_token}').json()
        for comment in comments:
            username = comment['author']['name']
            text = comment['body']
            created_at = comment['created_at']

            full_text = f"{username} ({created_at}):\n\n{text}"

            youtrack.execute_command(yt_issue_id, 'comment', full_text, run_as=get_user_by_id(comment['author']['id']))
            # pprint(comment)
            print('   *', username, created_at)
