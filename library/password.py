#!/usr/bin/env python3

# After `systemctl start matrix-synapse`, the matrix server is not up and
# running yet. This tries to connect to the matrix server with a timeuot of 5
# seconds

from ansible.module_utils.basic import *
import secrets
import string

alphabet = string.ascii_letters + string.digits
def main():
    module = AnsibleModule(argument_spec={
        "path": {"required": True, "type": "str"},
        "length": {"required": False, "type": "int", "default": 20},
    })
    password = None
    changed = False
    try:
        with open(module.params['path']) as f:
            password = f.read().strip()
    except FileNotFoundError:
        changed = True
        password = ''.join(secrets.choice(alphabet) for i in range(module.params['length']))
        with open(module.params['path'], 'w') as f:
            f.write(password + '\n')

    module.exit_json(changed=changed, meta = password )

if __name__ == '__main__':
    main()
