import gitlab
import csv
import globre
from transliterate import translit
from datetime import timedelta

from youtrack.connection import Connection
from youtrack.youtrack import YouTrackException

from utils.monkey_patches import create_issue, create_user_detailed, create_attachment, create_custom_field_detailed
from utils.attachments import get_attachments_urls
from utils.gitlab_auth import get_gitlab_session
from utils.time_spent import get_time_spent, timedelta_to_string
from utils.reformat_datetime import reformat_datetime

from config import (gitlab_url, gitlab_api_token, gitlab_per_page, gitlab_password, gitlab_login,
                    youtrack_url, youtrack_login, youtrack_password, youtrack_default_user,
                    youtrack_new_user_password, youtrack_new_user_email)

# apply monkey patches
Connection.create_issue = create_issue
Connection.create_user_detailed = create_user_detailed
Connection.create_attachment = create_attachment
Connection.create_custom_field_detailed = create_custom_field_detailed

# create GitLab API object
gl = gitlab.Gitlab(gitlab_url, gitlab_api_token)

# create YouTrack API object
youtrack = Connection(youtrack_url, youtrack_login, youtrack_password)


_users = None
_projects = None


def read_users(filename='users.csv'):
    """Read users from users.csv file."""
    global _users
    _users = dict()
    with open(filename) as f:
        reader = csv.DictReader(f, delimiter=';')
        for u in reader:
            _users[u['gitlab_username']] = u['youtrack_username']


def get_user_by_login(login, default_user=youtrack_default_user):
    """Get YouTrack user login by GitLab username."""
    if _users is None:
        read_users()

    return _users[login] if login in _users else default_user


def yt_create_users(users):
    """Create groups and users in YouTrack."""

    # create group and add all users
    try:
        youtrack._put('/admin/group/%s?autoJoin=true' % 'admins')
        print('*' * 80)
        input(f"Add user '{youtrack_login}' to group 'admins' and press any key...")
        input("Now grant 'sysadmin' role to group 'admins' and press any key...")
    except YouTrackException as e:
        if e.response.status in (409,):
            print("Group 'admins' already exists.")
        else:
            raise e

    print()
    print('Creating users...')
    for login in set(users.values()):
        email = youtrack_new_user_email.format(username=login)
        try:
            youtrack.create_user_detailed(login=login,
                                          full_name='',
                                          email=email,
                                          jabber='',
                                          password=youtrack_new_user_password)
            print('*', login)
        except YouTrackException as e:
            if e.response.status in (409,):
                print('*', login, '(exists)')
            else:
                print('*', login, '(error)')
                raise e


def read_projects(filename='projects.csv'):
    """Read projects from projects.csv file."""
    global _projects
    _projects = dict()
    with open(filename) as f:
        reader = csv.DictReader(f, delimiter=';')
        for p in reader:
            _projects[p['gitlab_project_pattern']] = {
                'youtrack_project_id': p['youtrack_project_id'],
                'youtrack_project_name': p['youtrack_project_name'],
            }


def get_project_by_pattern(project_name):
    """Find YouTrack project name by GitLab project name."""
    if _projects is None:
        read_projects()

    for pattern in _projects:
        if globre.match(pattern, project_name):
            return _projects[pattern]

    raise ValueError('Project name does not match any pattern!')


def yt_create_subsystems():
    """Create YouTrack subsystems."""
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


def yt_create_custom_fields():
    """Create YouTrack custom fields."""
    def create_custom_field(name, field_type):
        print(f'Creating custom field {name}... ', end='')
        try:
            youtrack.create_custom_field_detailed(
                name,
                field_type,
                is_private=False,
                default_visibility=True,
                auto_attached=True,
                additional_params={
                    'canBeEmpty': True,
                }
            )
            print("OK")
        except YouTrackException as e:
            if e.response.status in (409,):
                print('exists')
            else:
                print('error')
                raise e

    fields = (
        {
            'name': 'Срок начала',
            'field_type': 'date and time'
        },
        {
            'name': 'Срок окончания',
            'field_type': 'date and time'
        },
        {
            'name': 'Длительность',
            'field_type': 'period'
        },
        {
            'name': 'Бэклог',
            'field_type': 'state[1]'
        },
    )
    print()
    for field in fields:
        create_custom_field(**field)


def yt_create_projects(projects):
    """Create YouTrack projects."""
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


# init script
read_users()
read_projects()

yt_create_users(_users)
yt_create_custom_fields()
yt_create_projects(_projects)
yt_create_subsystems()


# list gitlab projects
gl_projects = gl.projects.list(page=1, per_page=gitlab_per_page)

project_count = 0
issue_count = 0
note_count = 0
gitlab_users = []


# authenticate in GitLab via requests to download files
file_downloader = get_gitlab_session(gitlab_url, gitlab_login, gitlab_password)


for p in gl_projects:
    project_count += 1

    project_id = p.id
    project_path = p.path
    issues = p.issues.list(page=1, per_page=gitlab_per_page, state='opened', order_by='created_at', sort='asc')

    # print project name
    print()
    print('=' * 80)
    print(project_id, project_path)

    for issue in issues:
        issue_count += 1

        if issue.author['username'] not in gitlab_users:
            gitlab_users.append(issue.author['username'])

        if issue.assignee and issue.assignee['username'] not in gitlab_users:
            gitlab_users.append(issue.assignee['username'])

        issue_iid = issue.iid
        assignee = get_user_by_login(issue.assignee['username']) if issue.assignee is not None else None
        author = get_user_by_login(issue.author['username'])
        summary = issue.title
        description = issue.description

        subsystem = project_path
        state = 'fixed' if issue.state == 'closed' else None

        print(f" * [{issue.author['username']}, {issue.iid}] {summary}")

        files = get_attachments_urls(description)
        attach = []
        if files:
            for relative_url in files:
                file_name = translit(relative_url.split('/')[-1], 'ru', reversed=True)
                url = p.web_url + relative_url + f'?access_token={gitlab_api_token}'
                headers = {'PRIVATE-TOKEN': gitlab_api_token}
                print('   FILE:', url)
                r = file_downloader.get(url, headers=headers)

                description = description.replace(relative_url, file_name)

                attach.append({
                    'author_login': author,
                    'files': {
                        file_name: r.content
                    }
                })

        yt_project = get_project_by_pattern(p.name)
        yt_project_id = yt_project['youtrack_project_id']
        response = youtrack.create_issue(project=yt_project_id,
                                         assignee=assignee,
                                         summary=summary,
                                         description=description,
                                         subsystem=subsystem,
                                         state=state)
        yt_issue_id = response[0]['location'].split('/')[-1]

        for f in attach:
            youtrack.create_attachment(yt_issue_id, **f)

        issue_time_spent = timedelta()

        notes = issue.notes.list(page=1, per_page=gitlab_per_page, order_by='created_at', sort='asc')
        for note in notes:
            note_count += 1

            if note.author['username'] not in gitlab_users:
                gitlab_users.append(note.author['username'])

            username = note.author['name']
            text = note.body
            created_at = reformat_datetime(note.created_at)

            full_text = f"{username} ({created_at}):\n\n{text}"

            # post comment
            youtrack.execute_command(
                yt_issue_id,
                'comment',
                full_text,
                run_as=get_user_by_login(note.author['username'])
            )
            print('   *', note.id,  username, created_at)

            note_time_spent = get_time_spent(text)
            issue_time_spent += note_time_spent
            if note_time_spent:
                print('   *** Time spent detected in text:', text, note_time_spent)

        # update spent time on issue
        youtrack.execute_command(yt_issue_id, 'Длительность {ts}'.format(
            ts=timedelta_to_string(issue_time_spent)
        ))

print('project_count', project_count)
print('issue_count', issue_count)
print('note_count', note_count)
print('Done.')
