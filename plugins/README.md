# Plugins

This directory contains custom Ansible plugins for the `kode3tech.devtools` collection.

## Directory Structure

- `modules/` - Custom Ansible modules
- `filter/` - Custom Jinja2 filter plugins
- `inventory/` - Custom inventory plugins (when needed)
- `lookup/` - Custom lookup plugins (when needed)

## Usage

Plugins in this collection are automatically available when using the collection:

```yaml
---
- hosts: localhost
  collections:
    - kode3tech.devtools
  tasks:
    - name: Use custom module
      kode3tech.devtools.custom_module:
        param: value
```

## Future Plugins

As the collection grows, we may add custom plugins for:
- Container management utilities
- Configuration helpers
- Infrastructure automation tasks

## Contributing

When adding new plugins, ensure:
- Proper documentation in docstrings
- Unit tests included
- ansible-test sanity checks pass
