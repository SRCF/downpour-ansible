#!/usr/bin/env python3

from ansible.module_utils.basic import *
from matrix_client.client import *
from matrix_client.room import Room
import urllib.parse
import json

def main():
    module = AnsibleModule(argument_spec={
        "username": {"required": True, "type": "str"},
        "password": {"required": True, "type": "str"},
        "domain": {"required": False, "type": "str", "default": "http://localhost:8008"},
        "join_rule": {"required": False, "type": "str", "choices": ["public", "invite"]},
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
        # We can't tell if this changed. Just assume it didn't
        client.api.set_join_rule(room.room_id, module.params["join_rule"])

    module.exit_json(changed=changed, meta={"room_id": room.room_id})

if __name__ == '__main__':
    main()
