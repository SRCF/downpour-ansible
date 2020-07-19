from mattermostdriver import Driver
from ansible.module_utils.basic import *

def main():
    module = AnsibleModule(argument_spec={
        "username": {"required": True, "type": "str"},
        "password": {"required": True, "type": "str"},
        "token_description": {"required": False, "type": "str", "default": ""},
        "url": {"required": False, "type": "str", "default": "localhost"},
        "scheme": {"required": False, "type": "str", "default": "http"},
        "port": {"required": False, "type": "int", "default": 8065},
    })

    driver = Driver({
        "login_id": module.params['username'],
        "password": module.params['password'],
        "url": module.params['url'],
        "port": module.params['port'],
        "scheme": module.params['scheme'],
    })
    driver.login()
    token = driver.users.create_user_access_token(driver.client.userid,
            {"description": module.params["token_description"]})
    driver.logout()
    module.exit_json(changed=True, meta={"token": token["token"]})

if __name__ == '__main__':
    main()
