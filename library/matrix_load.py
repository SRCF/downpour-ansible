#!/usr/bin/env python3

# After `systemctl start matrix-synapse`, the matrix server is not up and
# running yet. This tries to connect to the matrix server with a timeuot of 5
# seconds

from ansible.module_utils.basic import *
from urllib.request import urlopen
from urllib.error import URLError
from time import sleep
import sys

def main():
    module = AnsibleModule(argument_spec={
        "domain": {"required": False, "type": "str", "default": "http://localhost:8008"},
        "timeout": {"required": False, "type": "float", "default": 5},
        "interval": {"required": False, "type": "float", "default": 0.1},
    })
    for _ in range(0, int(module.params['timeout'] / module.params['interval'])):
        try:
            urlopen(module.params['domain'])
            module.exit_json(changed=False)
            sys.exit(0)
        except URLError:
            sleep(module.params['interval'])

    module.fail_json(msg="Failed to connect to matrix")

if __name__ == '__main__':
    main()
