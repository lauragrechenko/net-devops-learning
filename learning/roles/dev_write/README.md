dev_write
=========

A simple Ansible role that wraps the `dev_write_module` to write or update text files with specified content in an idempotent manner.

Requirements
------------

- Ansible 2.14 or higher
- The `netology_devops.learning` collection must be installed

Role Variables
--------------

Available variables are listed below, along with default values (see `defaults/main.yml`):

```yaml
path: /tmp/hello.txt
```

The absolute path where the file should be created or updated.

```yaml
content: "Hello from role default"
```

The text content to write to the file. The file will only be modified if the content differs from what's currently in the file.

Dependencies
------------

This role has no external role dependencies. It uses the `dev_write_module` module from the `netology_devops.learning` collection.

Example Playbook
----------------

Basic usage with default values:

```yaml
- hosts: servers
  roles:
    - role: netology_devops.learning.dev_write
```

Custom path and content:

```yaml
- hosts: servers
  roles:
    - role: netology_devops.learning.dev_write
      path: /etc/myapp/config.txt
      content: |
        server_name=myserver
        port=8080
        enabled=true
```

Using variables:

```yaml
- hosts: servers
  vars:
    config_path: /opt/app/settings.conf
    config_data: "Environment=production"
  roles:
    - role: netology_devops.learning.dev_write
      path: "{{ config_path }}"
      content: "{{ config_data }}"
```

Features
--------

- **Idempotent**: Only modifies the file if content differs
- **Check mode**: Supports `--check` mode to preview changes
- **Diff support**: Shows differences when run with `--diff`
- **Directory creation**: Automatically creates parent directories if needed

License
-------

GPL-3.0-or-later

Author Information
------------------

Laura Grechenko (@lauragrechenko)

Created for learning purposes as part of the Netology DevOps course.
