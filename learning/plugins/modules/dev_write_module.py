#!/usr/bin/python
# # Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# # GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import annotations

DOCUMENTATION = r'''
---
module: dev_write_module
short_description: Create/overwrite a text file with given content (idempotent)
version_added: "1.0.0"
description:
  - Creates a text file at the given path with the provided content.
  - If the file already exists with identical content, nothing changes.
  - Supports check mode and returns a diff.
options:
  path:
    description: Absolute path of the file to create/overwrite.
    type: path
    required: true
  content:
    description: Text content to write into the file (UTF-8).
    type: str
    required: true
author:
  - "Laura Grechenko (@lauragrechenko)"
'''

EXAMPLES = r'''
- name: Write a file with content
  dev_write_module:
    path: /tmp/hello.txt
    content: "Hello, ansible-world!"
'''

RETURN = r'''
path:
  description: File path written/checked.
  type: str
  returned: always
size:
  description: Size in bytes of the desired content.
  type: int
  returned: always
changed:
  description: Whether the file was created/modified.
  type: bool
  returned: always
'''

import os
from ansible.module_utils.basic import AnsibleModule


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type='path', required=True),
            content=dict(type='str', required=True),
        ),
        supports_check_mode=True,
    )

    path = module.params['path']
    new_content = module.params['content']

    current_content = None
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                current_content = f.read()
        except Exception as e:
            module.fail_json(msg=f"Failed to read '{path}': {e}")

    content_changed = (current_content != new_content)

    result = {
        'changed': content_changed,
        'path': path,
        'size': len(new_content),
    }

    if module.check_mode:
        module.exit_json(**result)

    if content_changed:
        try:
            parent = os.path.dirname(path)
            if parent and not os.path.isdir(parent):
                os.makedirs(parent, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
        except Exception as e:
            module.fail_json(msg=f"Failed to write '{path}': {e}", **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
