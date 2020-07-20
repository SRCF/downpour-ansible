#!/usr/bin/env python3

from ansible.module_utils.basic import *
from matrix_client.client import *
from matrix_client.room import Room
from typing import Optional
import urllib.parse
import json

def get_state(room: Room, event: str, state_key: str="") -> Optional[dict]:
    try:
        return room.client.api._send("GET", "/rooms/{}/state/{}/{}".format(room.room_id, event, state_key))
    except MatrixRequestError as e:
        # If it is currently unset, it returns 404
        if e.code == 404:
            return None
        else:
            raise

def main():
    module = AnsibleModule(argument_spec={
        "username": {"required": True, "type": "str"},
        "password": {"required": True, "type": "str"},
        "domain": {"required": False, "type": "str", "default": "http://localhost:8008"},
        "join_rule": {"required": False, "type": "str", "choices": ["public", "invite"]},
        "history_visibility": {"required": False, "type": "str", "choices": ["invited", "joined", "shared", "world_readable"]},
        "invites": {"required": False, "type": "list", "default": []},
        "power_levels": {"required": False, "type": "list", "default": []},
        "room_alias": {"required": False, "type": "str"},
    })

    client = MatrixClient(module.params['domain'])
    client.login(module.params["username"], module.params["password"])
    room = None
    changed = False
    try:
        room = client.create_room(module.params["room_alias"], invitees=module.params["invites"])
        changed = True
    except MatrixRequestError as e:
        if json.loads(e.content)["errcode"] == "M_ROOM_IN_USE":
            # Get proper domain name
            import requests
            result = requests.get(module.params["domain"] + "/.well-known/matrix/client").json()
            url = urllib.parse.urlparse(result["m.homeserver"]["base_url"]).netloc

            room_id = client.api.get_room_id("#" + module.params["room_alias"] + ":" + url)
            room = Room(client, room_id)
            for user_id in module.params["invites"]:
                # Failure can be due to many reasons, one of which is that the user is
                # already in the room. We interpret failure as lack of changing.
                changed |= room.invite_user(user_id)

        else:
            raise


    if module.params["power_levels"] != []:
        content = client.api.get_power_levels(room.room_id)
        content_changed = False
        for [user, level] in module.params["power_levels"]:
            if content["users"].get(user, -1) != level:
                content["users"][user] = level
                content_changed = True

        if content_changed:
            changed = True
            client.api.set_power_levels(room.room_id, content)

    if module.params["join_rule"] is not None:
        current = get_state(room, "m.room.join_rules")
        if current is None or current["join_rule"] != module.params["join_rule"]:
            client.api.set_join_rule(room.room_id, module.params["join_rule"])

    if module.params["history_visibility"] is not None:
        current = get_state(room, "m.room.history_visibility")
        if current is None or current["history_visibility"] != module.params["history_visibility"]:
            changed = True
            room.send_state_event("m.room.history_visibility", {
                    "history_visibility": module.params["history_visibility"],
                })

    module.exit_json(changed=changed, meta={"room_id": room.room_id})

if __name__ == '__main__':
    main()
