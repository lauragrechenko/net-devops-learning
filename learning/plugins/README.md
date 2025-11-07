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
