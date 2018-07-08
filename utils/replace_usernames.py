def replace_usernames(msg, users):
    for gl_login, yt_credentials in users.items():
        msg = msg.replace(f'@{gl_login}', f"@{yt_credentials['username']}")
    return msg
