import requests
import json
from datetime import datetime

from config import (hw_token_alive, hw_token_url, hw_iam_user, hw_iam_pwd, hw_account, hw_project_scope)

_token_ = ''
_update_time_ = datetime.now()
_first_ = True


def _update_token():
    global _first_
    global _token_
    global _update_time_

    # test token alive
    if not _first_:
        now = datetime.now()
        if (now-_update_time_).seconds < hw_token_alive:
            return
    else:
        _first_ = False

    header = {"Content-Type": "application/json;charset=utf8"}
    data = {
        "auth": {
            "identity": {
                "methods": ["password"],
                "password": {
                    "user": {
                        "name": hw_iam_user,
                        "password": hw_iam_pwd,
                        "domain": {
                            "name": hw_account
                        }
                    }
                }
            },
            "scope": {
                "project": {"name": hw_project_scope}
            }
        }
    }
    response = requests.post(
        url=hw_token_url,
        data=json.dumps(data),
        headers=header
    )
    _token_, _update_time_ = response.headers['X-Subject-Token'], datetime.now()


def get_token():
    _update_token()

    global _token_
    return _token_


if __name__ == "__main__":
    print(get_token())
    print(_update_time_)
