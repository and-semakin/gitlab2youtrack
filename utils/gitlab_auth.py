import requests
import re


def get_gitlab_session(gitlab_url, login, password):
    s = requests.Session()

    r = s.get(f'{gitlab_url}/users/sign_in')
    csrf_re = re.compile(r"<meta name=\"csrf-token\" content=\"([A-z0-9/+=]+)\" \/>")
    csrf_matches = re.findall(csrf_re, r.text)

    if not csrf_matches:
        print('CSRF token not found!')
        exit()

    csrf = csrf_matches[0]

    auth_data = {
        'authenticity_token': csrf,
        'user[login]': login,
        'user[password]': password,
        'user[remember_me]': 0,
        'utf8': '✓'
    }

    r = s.post(f'{gitlab_url}/users/sign_in', data=auth_data)

    return s