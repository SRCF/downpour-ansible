#!/usr/bin/env python3

import requests

PREFIX = "http://localhost:8065/api/v4"

def _request(endpoint, data, tok=None):
    headers = {}
    if tok is not None:
        headers["Authorization"] = "Bearer " + tok

    r = requests.post(PREFIX + endpoint, json=data, headers=headers)
    return (r.json(), r.headers)

userid=None
token=None

def login(username: str, password: str):
    global userid, token
    response = _request("/users/login", {
        "login_id": username,
        "password": password,
    })
    userid = response[0]["id"]
    token = response[1]["Token"]

def login_admin():
    with open("/root/mattermost-admin-password") as f:
        login("admin", f.read().strip())

def request(endpoint, data):
    if userid == None:
        login_admin()

    return _request(endpoint, data, tok=token)[0]
