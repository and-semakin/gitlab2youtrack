import requests
from pprint import pprint
import getpass
from youtrack.connection import Connection
from youtrack.youtrack import YouTrackException

gitlab_url = 'https://gitlab.ezmp.kbinform.ru/api/v4/'
gitlab_api_token = '2FHbXaGd-i59EbeGV4dW'

youtrack_url = 'http://youtrack.dev.kbinform.ru/'
youtrack_login = 'SemakinAE'
youtrack_password = getpass.getpass(prompt='YouTrack Password: ')
youtrack = Connection(youtrack_url, youtrack_login, youtrack_password)

yt_projects = youtrack.get_projects()
print(yt_projects)


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


# list gitlab projects
projects = requests.get(f'{gitlab_url}projects?private_token={gitlab_api_token}').json()

# print(projects)
for p in projects:
    project_id = p['id']
    project_path = p['path']
    issues = requests.get(f'{gitlab_url}projects/{project_id}/issues?scope=all&private_token={gitlab_api_token}').json()

    # print project name
    print()
    print('=' * 80)
    print(project_path)
    # pprint(p)
    # exit()

    yt_project_id = project_path.replace('-', '_')
    print(yt_project_id)

    # create youtrack project if not exists
    try:
        project = youtrack.get_project(yt_project_id)
    except YouTrackException:
        youtrack.create_project_detailed(yt_project_id, p['name'], p['description'], get_user_by_id(p['creator_id']))
        project = youtrack.get_project(yt_project_id)

    for issue in issues:
        assignee = get_user_by_id(issue['assignee']['id']) if issue['assignee'] is not None else None
        summary = ''
        description = issue['description']
        youtrack.create_issue(project, assignee, summary, description)
        pprint(issue)
