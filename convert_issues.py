import gitlab
import csv
from pprint import pprint
import getpass
import globre
from youtrack.connection import Connection
from youtrack.youtrack import YouTrackException

from monkey_patches import create_issue

gitlab_url = 'https://gitlab.ezmp.kbinform.ru'
gitlab_api_token = '2FHbXaGd-i59EbeGV4dW'
gitlab_per_page = 10000
gl = gitlab.Gitlab(gitlab_url, gitlab_api_token)

youtrack_url = 'http://192.168.100.42:8080/'
youtrack_login = 'admin'
youtrack_password = 'P@ssw0rd'

youtrack_default_user = 'user'
youtrack_new_user_email = '{username}@kbinform.ru'
youtrack_new_user_password = '11111'

# apply monkey patches
Connection.create_issue = create_issue

youtrack = Connection(youtrack_url, youtrack_login, youtrack_password)

_users = None
_projects = None


def read_users():
    global _users
    _users = dict()
    with open('users.csv') as f:
        reader = csv.DictReader(f, delimiter=';')
        for u in reader:
            _users[u['gitlab_username']] = u['youtrack_username']


def get_user_by_login(login, default_user=youtrack_default_user):
    if _users is None:
        read_users()

    return _users[login] if login in _users else default_user


def yt_create_users(users):
    # create group and add all users
    try:
        content = youtrack._put(
            '/admin/group/%s?autoJoin=true' % 'admins')
        print('*' * 80)
        input(f"Add user '{youtrack_login}' to group 'admins' and press any key...")
        input("Now grant 'sysadmin' group rights to role 'admins' and press any key...")
    except YouTrackException as e:
        if e.response.status in (409,):
            print("Group 'admins' already exists.")
        else:
            raise e

    print()
    print('Creating users...')
    for login in users.values():
        email = youtrack_new_user_email.format(username=login)
        youtrack.create_user_detailed(login, '', email, '')
        print('*', login)


def read_projects():
    global _projects
    _projects = dict()
    with open('projects.csv') as f:
        reader = csv.DictReader(f, delimiter=';')
        for p in reader:
            _projects[p['gitlab_project_pattern']] = {
                'youtrack_project_id': p['youtrack_project_id'],
                'youtrack_project_name': p['youtrack_project_name'],
            }


def get_project_by_pattern(project_name):
    if _projects is None:
        read_projects()

    for pattern in _projects:
        if globre.match(pattern, project_name):
            return _projects[pattern]

    raise ValueError('Project name does not match any pattern!')


def yt_create_projects(projects):
    print()
    print('Creating projects...')

    already_created = []

    for project in projects.values():
        project_id = project['youtrack_project_id']
        project_name = project['youtrack_project_name']

        if project_id in already_created:
            continue

        try:
            youtrack.create_project_detailed(project_id, project_name, project_name, youtrack_login)
            # yt_project = youtrack.get_project(project_id)
            print('*', project_id)
            already_created.append(project_id)
        except YouTrackException as e:
            if e.response.status in (409,):
                print('*', project_id, 'already exists')
                already_created.append(project_id)
            else:
                print('*', project_id, 'error:')
                raise e


def yt_create_subsystems():
    gl_projects = gl.projects.list(page=1, per_page=gitlab_per_page)

    print()
    print('Creating subsystems...')

    for p in gl_projects:
        yt_project = get_project_by_pattern(p.name)
        yt_project_id = yt_project['youtrack_project_id']
        try:
            youtrack.create_subsystem_detailed(yt_project_id, p.path, is_default=False, default_assignee_login='')
            print(f" * {p.path}")
        except YouTrackException as e:
            if e.response.status in (409,):
                print(f" * {p.path} (already exists)")
            else:
                print(f" * {p.path} (error)")
                raise e


# init script
read_users()
read_projects()

yt_create_users(_users)
yt_create_projects(_projects)
yt_create_subsystems()


# list gitlab projects
gl_projects = gl.projects.list(page=1, per_page=gitlab_per_page)

project_count = 0
issue_count = 0
note_count = 0
gitlab_users = []

# print(gl_projects)
for p in gl_projects:
    project_count += 1

    project_id = p.id
    project_path = p.path
    issues = p.issues.list(page=1, per_page=gitlab_per_page, state='opened', order_by='created_at', sort='asc')

    # print project name
    print()
    print('=' * 80)
    print(project_id, project_path)
    # pprint(p)
    # exit()

    for issue in issues:
        issue_count += 1

        if issue.author['username'] not in gitlab_users:
            gitlab_users.append(issue.author['username'])

        if issue.assignee and issue.assignee['username'] not in gitlab_users:
            gitlab_users.append(issue.assignee['username'])

        issue_iid = issue.iid
        assignee = get_user_by_login(issue.assignee['username']) if issue.assignee is not None else None
        summary = issue.title
        description = issue.description
        subsystem = project_path
        state = 'fixed' if issue.state == 'closed' else None

        # pprint(issue)
        print(f" * [{issue.author['username']}, {issue.iid}] {summary}")

        yt_project = get_project_by_pattern(p.name)
        yt_project_id = yt_project['youtrack_project_id']
        response = youtrack.create_issue(project=yt_project_id,
                                         assignee=assignee,
                                         summary=summary,
                                         description=description,
                                         subsystem=subsystem,
                                         state=state)
        yt_issue_id = response[0]['location'].split('/')[-1]

        notes = issue.notes.list(page=1, per_page=gitlab_per_page, order_by='created_at', sort='asc')
        for note in notes:
            note_count += 1

            if note.author['username'] not in gitlab_users:
                gitlab_users.append(note.author['username'])

            username = note.author['name']
            text = note.body
            created_at = note.created_at

            full_text = f"{username} ({created_at}):\n\n{text}"

            youtrack.execute_command(yt_issue_id, 'comment', full_text, run_as=get_user_by_login(note.author['username']))
            # pprint(comment)
            print('   *', note.id,  username, created_at)

print('project_count', project_count)
print('issue_count', issue_count)
print('note_count', note_count)
print('Done.')
