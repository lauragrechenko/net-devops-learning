# Ansible Collection - netology_devops.learning

This is a learning Ansible collection created for educational purposes. It contains a custom module and role for file writing operations.

## Description

The `netology_devops.learning` collection provides tools for managing file content in an idempotent manner. It includes:

- **dev_write_module**: A custom Ansible module for creating/overwriting text files with specified content
- **dev_write role**: A wrapper role that simplifies the use of the dev_write_module

## Installation

You can install this collection from source:

```bash
ansible-galaxy collection install netology_devops.learning
```

Or build and install locally:

```bash
ansible-galaxy collection build
ansible-galaxy collection install netology_devops-learning-1.0.0.tar.gz
```

## Included Content

### Modules

- **dev_write_module**: Creates or overwrites a text file with given content
  - Idempotent operation (only changes file if content differs)
  - Supports check mode

### Roles

- **dev_write**: Simple role that wraps the dev_write_module for easy playbook integration

## Using This Collection

### Using the Module Directly

```yaml
- name: Write a configuration file
  netology_devops.learning.dev_write_module:
    path: /etc/myapp/config.txt
    content: "Configuration data here"
```

### Using the Role

```yaml
- name: Use dev_write role
  hosts: all
  roles:
    - role: netology_devops.learning.dev_write
      path: /tmp/output.txt
      content: "Custom content"
```

## Requirements

- Ansible 2.14 or higher
- Python 3.6 or higher

## License

GPL-2.0-or-later

## Author

Laura Grechenko (@lauragrechenko)

## Contributing

This is a learning collection for educational purposes.
