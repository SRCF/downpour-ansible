#!/usr/bin/env python3

import os, shutil
import mattermost_client

mattermost_client.login_admin()

token = mattermost_client.request("/users/" + mattermost_client.userid + "/tokens", {
    "description": "Internal server use. DO NOT DELETE.",
})["token"]

open(os.open("/etc/mattermost-admin-token", os.O_CREAT | os.O_WRONLY, 0o660), "w").write("set $access_token %s;" % token)
shutil.chown("/etc/mattermost-admin-token", user="mattermost", group="www-data")
