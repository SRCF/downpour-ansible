#!/usr/bin/env python3

from ansible.module_utils.basic import *
from matrix_client.client import *
import json

def main():
    module = AnsibleModule(argument_spec={
        "username": {"required": True, "type": "str"},
        "password": {"required": True, "type": "str"},
        "domain": {"required": False, "type": "str", "default": "http://localhost:8008"},
        "shared_secret": {"required": False, "type": "str"},
    })

    username = module.params['username']
    password = module.params['password']
    domain = module.params['domain']

    if module.params['shared_secret']:
        from synapse._scripts.register_new_matrix_user import request_registration
        res = request_registration(
                username,
                password,
                domain,
                module.params['shared_secret'],
                exit = lambda x: x)

        if res == 1:
            client = MatrixClient(domain)
            client.login(username, password)
            client.logout()
            module.exit_json(changed=False)
        else:
            module.exit_json(changed=True)
    else:
        client = MatrixClient(module.params['domain'])
        try:
            client.register_with_password(username, password)
            client.logout()
            module.exit_json(changed=True)
        except MatrixRequestError as e:
            if json.loads(e.content)["errcode"] == "M_USER_IN_USE":
                client.login(username, password)
                client.logout()
                module.exit_json(changed=False)
            else:
                client.logout()
                raise

if __name__ == '__main__':
    main()
