# Role Structure Standards

## Overview

All roles in the `code3tech.devtools` collection follow a standardized structure based on Ansible best practices. This document defines the mandatory structure and conventions for creating and maintaining roles.

## Standard Role Structure

```text
<role_name>/
├── README.md                      # Role documentation
├── pytest.ini                     # Pytest configuration
├── defaults/
│   └── main.yml                  # Default variables (user-configurable)
├── files/                        # Static files
├── handlers/
│   └── main.yml                  # Event handlers (restart, reload, etc.)
├── meta/
│   └── main.yml                  # Role metadata (dependencies, platforms, galaxy_info)
├── molecule/
│   └── default/
│       ├── molecule.yml          # Molecule config (multi-distro testing)
│       ├── converge.yml          # Test playbook
│       ├── prepare.yml           # Pre-test setup (optional)
│       ├── verify.yml            # Ansible-based verification
│       └── test_default.py       # Pytest/testinfra tests
├── tasks/
│   ├── main.yml                  # Main task orchestration
│   ├── setup-Debian.yml          # Debian/Ubuntu specific tasks
│   └── setup-RedHat.yml          # RHEL/CentOS/Rocky specific tasks
├── templates/                    # Jinja2 templates
│   └── *.j2                      # Configuration files
├── tests/                        # Legacy test directory
│   ├── inventory                 # Test inventory
│   └── test.yml                  # Basic test playbook
└── vars/
    ├── main.yml                  # General variables
    ├── Debian.yml                # Debian/Ubuntu variables
    └── RedHat.yml                # RHEL/CentOS/Rocky variables
```

## Directory Purposes

### `defaults/main.yml`
**User-configurable variables** with sensible defaults.

**Requirements:**
- All variables prefixed with role name: `<role>_variable_name`
- Document each variable with inline comments
- Set safe default values
- Mark required variables with comments

**Example:**
```yaml
---
# Service edition (ce = Community Edition, ee = Enterprise Edition)
service_edition: "ce"

# List of packages to install
service_packages:
  - "service-{{ service_edition }}"
  - "service-cli"

# Users to add to service group (password-less access)
# WARNING: Users in this group may have elevated privileges!
service_users: []

# Service configuration (JSON format)
service_daemon_config:
  log-driver: "json-file"
  log-opts:
    max-size: "10m"
    max-file: "3"
```

### `vars/`
**OS-specific and immutable variables.**

**Structure:**
- `main.yml` - Common variables across all OS families
- `Debian.yml` - Debian/Ubuntu specific (package names, paths)
- `RedHat.yml` - RHEL/CentOS/Rocky specific (package names, paths)

**Example `vars/Debian.yml`:**
```yaml
---
# Debian/Ubuntu package names
service_prerequisite_packages:
  - apt-transport-https
  - ca-certificates
  - gnupg
  - lsb-release

service_repo_key_url: "https://download.service.com/linux/debian/gpg"
service_repo_url: "https://download.service.com/linux/debian"
```

### `tasks/main.yml`
**Orchestration layer** that includes OS-specific tasks.

**Pattern:**
```yaml
---
- name: Include OS-specific variables
  ansible.builtin.include_vars: "{{ ansible_os_family }}.yml"
  tags: <role_name>

- name: Include OS-specific tasks
  ansible.builtin.include_tasks: "setup-{{ ansible_os_family }}.yml"
  tags: <role_name>

# Common tasks here (apply to all OS families)
- name: Configure service
  ansible.builtin.template:
    src: config.j2
    dest: /etc/service/config.yaml
    owner: root
    group: root
    mode: '0644'
  notify: restart service
  tags: <role_name>
```

### `handlers/main.yml`
**Event-driven actions** triggered by task changes.

**Requirements:**
- Use FQCN (Fully Qualified Collection Names)
- Name handlers with verb + service: `Restart service`, `Reload service`

**Example:**
```yaml
---
- name: Restart service
  ansible.builtin.systemd:
    name: service
    state: restarted

- name: Reload service
  ansible.builtin.systemd:
    name: service
    state: reloaded
```

### `meta/main.yml`
**Role metadata** for Ansible Galaxy and dependencies.

**Required fields:**
```yaml
---
galaxy_info:
  role_name: <role_name>
  namespace: code3tech
  author: Code3Tech DevOps Team
  description: Brief description of role purpose
  company: Code3Tech
  license: MIT
  min_ansible_version: "2.15"
  
  platforms:
    - name: Ubuntu
      versions:
        - jammy    # 22.04
        - noble    # 24.04
        - plucky   # 25.04
    - name: Debian
      versions:
        - bullseye # 11
        - bookworm # 12
        - trixie   # 13
    - name: EL
      versions:
        - "9"
        - "10"

  galaxy_tags:
    - devops
    - tools
    - <relevant_tags>

dependencies: []
```

### `molecule/default/`
**Automated testing** with Molecule.

**Required files:**

#### `molecule.yml` - Test configuration
```yaml
---
dependency:
  name: galaxy

driver:
  name: docker

platforms:
  - name: ubuntu2204
    image: geerlingguy/docker-ubuntu2204-ansible:latest
    command: ""
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:rw
    cgroupns_mode: host
    privileged: true
    pre_build_image: true

  - name: debian12
    image: geerlingguy/docker-debian12-ansible:latest
    command: ""
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:rw
    cgroupns_mode: host
    privileged: true
    pre_build_image: true

  - name: rockylinux9
    image: geerlingguy/docker-rockylinux9-ansible:latest
    command: ""
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:rw
    cgroupns_mode: host
    privileged: true
    pre_build_image: true

provisioner:
  name: ansible
  config_options:
    defaults:
      callbacks_enabled: profile_tasks
      stdout_callback: yaml
  playbooks:
    converge: converge.yml
    verify: verify.yml
  env:
    ANSIBLE_ROLES_PATH: ../../../

verifier:
  name: ansible
```

#### `test_default.py` - Python tests
```python
"""
Molecule tests for <role_name> role.
"""
import os
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_package_installed(host):
    """Test that required packages are installed."""
    package = host.package('service-package')
    assert package.is_installed


def test_service_running(host):
    """Test that service is running and enabled."""
    service = host.service('service-name')
    assert service.is_running
    assert service.is_enabled


def test_configuration_file(host):
    """Test that configuration file exists."""
    config = host.file('/etc/service/config.yaml')
    assert config.exists
    assert config.user == 'root'
    assert config.group == 'root'
```

## Supported Platforms

All roles MUST support:

| Distribution | Versions | Galaxy Name |
|--------------|----------|-------------|
| **Ubuntu** | 22.04, 24.04, 25.04 | `jammy`, `noble`, `plucky` |
| **Debian** | 11, 12, 13 | `bullseye`, `bookworm`, `trixie` |
| **RHEL/Rocky/Alma** | 9, 10 | EL versions `"9"`, `"10"` |

## Coding Standards

### Variable Naming
```yaml
# Format: <role>_<purpose>_<detail>
service_version: ""
service_edition: "ce"
service_packages: []
service_users: []
service_daemon_config: {}
service_service_enabled: true
service_service_state: started
service_configure_repo: true
```

**Rules:**
- ALL variables prefixed with role name
- Use snake_case
- Boolean variables: `service_enabled`, `service_configure_repo`
- State variables: `service_state` (started/stopped)

### Task Standards
```yaml
# ✅ CORRECT
- name: Install service packages
  ansible.builtin.package:
    name: "{{ item }}"
    state: present
  loop: "{{ service_packages }}"
  tags: service

# ❌ WRONG
- name: Install packages  # Too generic
  package:                # Not FQCN
    name: "{{ item }}"
    state: present
  # No tags
```

**Requirements:**
- Use FQCN for ALL modules
- Descriptive names (minimum 3 words)
- Add appropriate tags
- Make tasks idempotent

### Multi-Platform Pattern
```yaml
# tasks/main.yml - Orchestration
---
- name: Include OS-specific variables
  ansible.builtin.include_vars: "{{ ansible_os_family }}.yml"
  tags: service

- name: Include OS-specific tasks
  ansible.builtin.include_tasks: "setup-{{ ansible_os_family }}.yml"
  tags: service
```

## Testing Requirements

Every role MUST have:

1. **Molecule tests** for 3+ distributions
2. **Pytest tests** with testinfra
3. **Ansible-lint** compliance (production profile)
4. **Yamllint** compliance

**Run tests:**
```bash
# Full test cycle
cd roles/<role_name>
molecule test

# Quick test
molecule converge
molecule verify

# Linting
ansible-lint
yamllint .
```

## Documentation Requirements

Every role MUST have comprehensive `README.md`:

### Required Sections
1. **Role description** - Brief overview
2. **Requirements** - Ansible version, dependencies
3. **Supported Distributions** - OS compatibility
4. **Role Variables** - Complete variable reference
5. **Dependencies** - Collection/role dependencies
6. **Example Playbook** - Multiple examples
7. **Testing** - How to run tests
8. **License** - MIT
9. **Author Information** - Code3Tech DevOps Team

### Example README Structure
```markdown
# Ansible Role: <role_name>

Brief description.

## Requirements

- Ansible >= 2.15
- Target OS: Ubuntu 22+, Debian 11+, RHEL 9+
- Root/sudo privileges

## Supported Distributions

- Ubuntu: 22.04, 24.04, 25.04
- Debian: 11, 12, 13
- RHEL/Rocky/Alma: 9, 10

## Role Variables

Available variables (see `defaults/main.yml`):

```yaml
service_variable: default_value  # Description
```

## Dependencies

None.

## Example Playbook

```yaml
- hosts: servers
  become: true
  roles:
    - code3tech.devtools.<role_name>
```

## Testing

```bash
cd roles/<role_name>
molecule test
```

## License

MIT

## Author Information

Code3Tech DevOps Team
```

## Compliance Checklist

Before submitting a role, verify:

- [ ] All variables prefixed with role name
- [ ] FQCN used for all modules
- [ ] Tasks have descriptive names (3+ words)
- [ ] Tasks have appropriate tags
- [ ] OS-specific logic separated (Debian.yml, RedHat.yml)
- [ ] Handlers defined for service changes
- [ ] meta/main.yml complete with platforms
- [ ] README.md with complete documentation
- [ ] Molecule tests for 3+ distributions
- [ ] Pytest tests implemented
- [ ] ansible-lint passes (production profile)
- [ ] yamllint passes
- [ ] All tasks idempotent

## Role Creation Workflow

```bash
# 1. Initialize role
ansible-galaxy init roles/<role_name>

# 2. Configure Molecule
cd roles/<role_name>
molecule init scenario --driver-name docker

# 3. Customize structure (following this guide)

# 4. Implement role

# 5. Test
molecule test

# 6. Lint
ansible-lint
yamllint .

# 7. Document (README.md)

# 8. Commit
git add roles/<role_name>
git commit -m "feat(roles): add <role_name> role"
```

---

[← Back to Development Documentation](README.md)
