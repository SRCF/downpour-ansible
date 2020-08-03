from mattermostdriver import Driver
from ansible.module_utils.basic import *

FIELDS = ["name", "display_name", "purpose", "header"]
def main():
    module = AnsibleModule(argument_spec={
        "username": {"required": True, "type": "str"},
        "password": {"required": True, "type": "str", "no_log": True},
        "url": {"required": False, "type": "str", "default": "localhost"},
        "scheme": {"required": False, "type": "str", "default": "http"},
        "port": {"required": False, "type": "int", "default": 8065},
        "name": {"required": True, "type": "str"},
        "display_name": {"required": True, "type": "str"},
        "type": {"required": True, "type": "str", "choices": ["O", "I"]},
    })

    driver = Driver({
        "login_id": module.params["username"],
        "password": module.params["password"],
        "url": module.params["url"],
        "port": module.params["port"],
        "scheme": module.params["scheme"],
    })
    driver.login()
    changed = False

    if driver.teams.check_team_exists(module.params["name"])["exists"]:
        team = driver.teams.get_team_by_name(module.params["name"])
        try:
            driver.teams.get_team_member(team["id"], driver.client.userid)
        except:
            driver.teams.add_user_to_team(team["id"], {
                "team_id": team["id"],
                "user_id": driver.client.userid
            })
            changed=True
    else:
        changed = True
        team = driver.teams.create_team(options={
            "name": module.params["name"],
            "display_name": module.params["display_name"],
            "type": module.params["type"]
        })

    if team["allow_open_invite"] != (module.params["type"] == "O") or team["display_name"] != module.params["display_name"]:
        changed = True
        driver.teams.patch_team(team["id"], {
            "display_name": module.params["display_name"],
            "allow_open_invite": module.params["type"] == "O",
        })

    module.exit_json(changed=changed, meta={"id": team["id"]})

if __name__ == "__main__":
    main()
