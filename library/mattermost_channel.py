from mattermostdriver import Driver
from ansible.module_utils.basic import *

FIELDS = ["name", "display_name", "purpose", "header"]

def main():
    module = AnsibleModule(argument_spec={
        "username": {"required": True, "type": "str"},
        "password": {"required": True, "type": "str"},
        "url": {"required": False, "type": "str", "default": "localhost"},
        "scheme": {"required": False, "type": "str", "default": "http"},
        "port": {"required": False, "type": "int", "default": 8065},
        "team_id": {"required": True, "type": "str"},
        "state": {"required": False, "type": "str", "choices": ["present", "absent"], "default": "present"},
        "name": {"required": True, "type": "str"},
        "display_name": {"required": False, "type": "str"},
        "type": {"required": False, "type": "str", "choices": ["O", "P"]},
        "purpose": {"required": False, "type": "str"},
        "header": {"required": False, "type": "str"},
    })

    driver = Driver({
        "login_id": module.params['username'],
        "password": module.params['password'],
        "url": module.params['url'],
        "port": module.params['port'],
        "scheme": module.params['scheme'],
    })
    driver.login()

    if module.params["state"] == "absent":
        try:
            channel = driver.channels.get_channel_by_name(module.params['team_id'], module.params['name'])
        except:
            channel = None

        if channel is not None:
            driver.channels.delete_channel(channel["id"])
        module.exit_json(changed=(channel is not None))

    if module.params["display_name"] is None:
        raise ValueError("display_name cannot be empty")

    changed = False

    options = {
        "team_id": module.params["team_id"],
        "type": module.params["type"],
    }
    for field in FIELDS:
        if module.params[field] is not None:
            options[field] = module.params[field]

    try:
        channel = driver.channels.get_channel_by_name(module.params['team_id'], module.params['name'])
    except:
        changed = True
        channel = driver.channels.create_channel(options=options)

    del options["team_id"]
    del options["type"]

    need_patch = False
    for field in FIELDS:
        if module.params[field] is not None and channel[field] != module.params[field]:
            need_patch = True
            break

    if need_patch:
        changed = True
        driver.channels.patch_channel(channel["id"], options)

    if module.params["type"] != channel["type"]:
        changed = True
        driver.channels.client.put(
            driver.channels.endpoint + '/channels/' + channel.id + '/privacy',
            { "privacy": channel["type"], }
        )

    module.exit_json(changed=changed, meta={"id": channel["id"]})

if __name__ == '__main__':
    main()
