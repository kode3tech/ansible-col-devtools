# Shared Tasks

This directory contains reusable Ansible tasks that can be shared across multiple roles within the collection.

## Available Shared Tasks

| Task File | Purpose | Used By |
|-----------|---------|---------|
| [permission_fixes.yml](#permission_fixesyml) | Fix file permissions for container configs | docker, podman |

## Usage

Include shared tasks in your role using:

```yaml
- name: Include shared task
  ansible.builtin.include_tasks:
    file: "{{ role_path }}/../../plugins/shared_tasks/task_name.yml"
```

## Task Documentation

### permission_fixes.yml

**Features:**
- ✅ **User config directory creation** - Creates `.docker` and `.config/containers` as needed
- ✅ **File ownership correction** - Fixes `root:root` to `user:user` ownership
- ✅ **SELinux context restoration** - Restores proper contexts on RHEL/CentOS
- ✅ **Multi-distribution support** - Works on Ubuntu, Debian, RHEL

**Variables:**
- `container_users` (required) - List of users to fix permissions for
- `container_config_paths` (required) - List of config directories (e.g., `.docker`)
- `container_config_files` (required) - List of config files (e.g., `.docker/config.json`)

**Example:**
```yaml
- name: Fix Docker config permissions for users
  ansible.builtin.include_tasks:
    file: "{{ role_path }}/../../plugins/shared_tasks/permission_fixes.yml"
  vars:
    container_users: "{{ docker_users }}"
    container_config_paths: ['.docker']
    container_config_files: ['.docker/config.json']
  when: docker_users | length > 0
```

---

## Best Practices

1. **Always use relative paths** from role directory
2. **Include error handling** with `failed_when: false` where appropriate
3. **Add appropriate tags** to shared tasks
4. **Document variables** used by shared tasks
5. **Test shared tasks** in multiple roles

---

[← Back to Plugins](../README.md)