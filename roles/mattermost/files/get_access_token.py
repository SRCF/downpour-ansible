#!/usr/bin/env python3

import os, shutil
import urllib.request
import urllib.parse
import sys
import json

PREFIX = "http://localhost:8065/api/v4"

def request(endpoint, data, tok=None):
    req = urllib.request.Request(PREFIX + endpoint, data=json.dumps(data).encode("utf-8"))
    req.add_header("Content-Type", "application/json")
    if tok is not None:
        req.add_header("Authorization", "Bearer " + tok)
    response = urllib.request.urlopen(req)
    return (json.loads(response.read().decode("utf-8")), response.info())

login, headers = request("/users/login", {
    "login_id": sys.argv[1],
    "password": sys.argv[2]
})

tok = headers["Token"]
userid = login["id"]

token = request("/users/" + userid + "/tokens", {
    "description": "Internal server use. DO NOT DELETE.",
}, tok=tok)[0]["token"]
open(os.open("/etc/mattermost-admin-token", os.O_CREAT | os.O_WRONLY, 0o660), "w").write("set $access_token %s;" % token)
shutil.chown("/etc/mattermost-admin-token", user="mattermost", group="www-data")
