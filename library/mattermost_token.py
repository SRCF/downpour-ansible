from mattermostdriver import Driver
from ansible.module_utils.basic import *
from requests import HTTPError

def main():
    module = AnsibleModule(argument_spec={
        "username": {"required": True, "type": "str"},
        "password": {"required": True, "type": "str", "no_log": True},
        "token_description": {"required": False, "type": "str", "default": ""},
        "url": {"required": False, "type": "str", "default": "localhost"},
        "scheme": {"required": False, "type": "str", "default": "http"},
        "port": {"required": False, "type": "int", "default": 8065},
        "path": {"required": True, "type": "str"},
    })

    token = None
    try:
        token = open(module.params["path"]).read().strip()
    except FileNotFoundError:
        pass

    if token is not None:
        test_driver = Driver({
            "token": token,
            "url": module.params['url'],
            "port": module.params['port'],
            "scheme": module.params['scheme'],
            })

        try:
            test_driver.login()
            userid = test_driver.client.userid
            test_driver.logout()
            module.exit_json(changed=False, meta={"token": token, "userid": userid})
        except HTTPError:
            pass


    driver = Driver({
        "login_id": module.params['username'],
        "password": module.params['password'],
        "url": module.params['url'],
        "port": module.params['port'],
        "scheme": module.params['scheme'],
    })
    driver.login()
    userid = driver.client.userid
    token = driver.users.create_user_access_token(driver.client.userid,
            {"description": module.params["token_description"]})
    driver.logout()
    open(module.params["path"], "w").write(token["token"])
    module.exit_json(changed=True, meta={"token": token["token"], "userid": userid})

if __name__ == '__main__':
    main()
