# Plugins

This directory contains custom Ansible plugins and shared tasks for the `code3tech.devtools` collection.

## Directory Structure

- `modules/` - Custom Ansible modules
- `filter/` - Custom Jinja2 filter plugins
- `inventory/` - Custom inventory plugins (when needed)
- `lookup/` - Custom lookup plugins (when needed)
- `shared_tasks/` - Reusable task files shared across roles

## Shared Tasks

The `shared_tasks/` directory contains common tasks that can be included in multiple roles to avoid code duplication.

See [shared_tasks/README.md](shared_tasks/README.md) for detailed documentation.

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
