# Ansible Collection - netology_devops.learning

This is a learning Ansible collection created for educational purposes. It contains custom modules and roles for file operations and cloud infrastructure management.

## Description

The `netology_devops.learning` collection provides tools for file management and cloud infrastructure automation. It includes:

- **dev_write_module**: A custom Ansible module for creating/overwriting text files with specified content
- **yc_instance**: Module for managing Yandex Cloud virtual machines via the `yc` CLI
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

- **yc_instance**: Manages Yandex Cloud VM instances
  - Creates instances with custom sizing (CPU, RAM, disk)
  - Supports preemptible instances and NAT configuration
  - SSH key injection
  - Requires `yc` CLI installed and configured

### Roles

- **dev_write**: Simple role that wraps the dev_write_module for easy playbook integration

## Using This Collection

### dev_write_module

```yaml
- name: Write a configuration file
  netology_devops.learning.dev_write_module:
    path: /etc/myapp/config.txt
    content: "Configuration data here"
```

### yc_instance

```yaml
- name: Create Yandex Cloud instance
  netology_devops.learning.yc_instance:
    name: demo-vm
    folder_id: "{{ yc_folder_id }}"
    zone: ru-central1-a
    subnet_id: "{{ yc_subnet_id }}"
    image_id: "{{ yc_image_id }}"
    cores: 2
    memory_gb: 4
    disk_gb: 20
    preemptible: false
    nat: true
    ssh_key: "{{ lookup('file', '~/.ssh/id_rsa.pub') }}"
```

### dev_write role

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
- `yc` CLI (for yc_instance module only)

## License

GPL-2.0-or-later

## Author

Laura Grechenko (@lauragrechenko)

## Contributing

This is a learning collection for educational purposes.
