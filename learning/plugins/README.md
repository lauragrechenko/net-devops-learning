# Plugins

This directory contains plugins for the collection.

## dev_write_module

Simple module that writes text to a file. Only updates the file if content actually changed (idempotent).

Usage:

```yaml
- name: Write config file
  netology_devops.learning.dev_write_module:
    path: /tmp/config.txt
    content: "some text here"
```

Parameters:
- `path` (required): Absolute path of the file to create/overwrite
- `content` (required): Text content to write into the file

Returns:
- `path`: File path that was written/checked
- `size`: Size in bytes of the content
- `changed`: Boolean indicating if the file was modified

Run `ansible-doc netology_devops.learning.dev_write_module` for more details.

## yc_instance

Manages Yandex Cloud VMs via the `yc` CLI. Creates instances with custom sizing, preemptible mode, NAT, and SSH keys.

Usage:

```yaml
- name: Create YC instance
  netology_devops.learning.yc_instance:
    name: demo
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

Key parameters:
- `name`, `folder_id`, `zone`, `subnet_id`, `image_id` - required
- `cores`, `memory_gb`, `disk_gb` - sizing (defaults: 2, 2, 10)
- `preemptible` - use preemptible instance (default: true)
- `nat` - attach public IP (default: true)
- `core_fraction` - guaranteed CPU (5/20/50/100, default: 5)

Requires `yc` CLI installed and configured.

Run `ansible-doc netology_devops.learning.yc_instance` for more details.
