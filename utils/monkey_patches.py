import urllib.parse
import requests
from xml.sax.saxutils import quoteattr


def urlquote(s):
    return urllib.parse.quote(utf8encode(s), safe="")


def utf8encode(source):
    if isinstance(source, str):
        source = source.encode('utf-8')
    return source


def create_issue(self, project, assignee, summary, description, priority=None, issue_type=None, subsystem=None,
                 state=None,
                 affects_version=None,
                 fixed_version=None, fixed_in_build=None, permitted_group=None,
                 markdown=True):
    params = {'project': project,
              'summary': summary}
    if description is not None:
        params['description'] = description
    if assignee is not None:
        params['assignee'] = assignee
    if priority is not None:
        params['priority'] = priority
    if issue_type is not None:
        params['type'] = issue_type
    if subsystem is not None:
        params['subsystem'] = subsystem
    if state is not None:
        params['state'] = state
    if affects_version is not None:
        params['affectsVersion'] = affects_version
    if fixed_version is not None:
        params['fixVersion'] = fixed_version
    if fixed_in_build is not None:
        params['fixedInBuild'] = fixed_in_build
    if permitted_group is not None:
        params['permittedGroup'] = permitted_group

    params['markdown'] = markdown

    return self._req('PUT', '/issue', urllib.parse.urlencode(params),
                     content_type='application/x-www-form-urlencoded')


def create_user_detailed(self, login, full_name, email, jabber, password=None):
    params = {
        'login': login,
        'fullName': full_name,
        'email': email,
        'jabber': jabber,
    }
    if password:
        params['password'] = password

    return self._req('PUT', f'/admin/user/{login}', urllib.parse.urlencode(params),
                     content_type='application/x-www-form-urlencoded')


def create_attachment(self, issue_id, files, author_login=None, created=None, group=None):
    params = {
        'issue': issue_id,
        # 'name': name
    }
    if author_login:
        params['authorLogin'] = author_login
    if created:
        params['created'] = created
    if group:
        params['group'] = group

    url = self.base_url + '/issue/' + issue_id + "/attachment"
    r = requests.post(url, data=params, files=files, headers=self.headers.copy())
    # print(r)


def create_custom_field_detailed(self, custom_field_name, type_name, is_private, default_visibility,
                                 auto_attached=False, additional_params=None):
    if additional_params is None:
        additional_params = dict([])
    params = {
        'type': type_name,
        'isPrivate': str(is_private).lower(),
        'defaultVisibility': str(default_visibility).lower(),
        'autoAttached': str(auto_attached).lower()
    }
    params.update(additional_params)
    for key in params:
        if isinstance(params[key], str):
            params[key] = params[key].encode('utf-8')

    self._req('PUT', '/admin/customfield/field/' + urlquote(custom_field_name.encode('utf-8')),
                     urllib.parse.urlencode(params),
                     content_type='application/x-www-form-urlencoded')

    return "Created"
