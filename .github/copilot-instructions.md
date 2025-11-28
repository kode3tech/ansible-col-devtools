# GitHub Copilot Instructions - code3tech.devtools Ansible Collection

> **📐 Documentation Quality Standards**: This project follows strict documentation standards (see section "📐 Documentation Quality Standards" below).
> When user requests to **"update documentation"**, **"improve docs"**, **"document feature"**, or similar commands, 
> **ALL 14 standards MUST be applied systematically**. This ensures consistency, quality, and maintainability.

## 📋 Project Overview

This is an **Ansible Collection** project following official Ansible best practices and Galaxy standards.

- **Collection Name**: `code3tech.devtools`
- **Version**: 1.0.0
- **Purpose**: DevOps tools installation and configuration (Docker, Podman, etc.)
- **License**: MIT
- **Supported Platforms**: Ubuntu 22.04+, Debian 11+, RHEL 9+

## � Organization Pattern: Separation by Scope

**CRITICAL**: This project follows a **strict organization pattern** based on **scope and target audience**. This pattern MUST be followed when creating any new content.

### Core Principle

```
"Everything in its place based on scope and target audience"
```

### Pattern Rules

#### 1️⃣ Documentation Organization

**By Target Audience:**
- **`docs/`** → Public (end users) - distributed with collection
- **`.tmp/analysis/`** → Internal (maintainers) - NOT distributed

**By Scope (within `docs/`):**
- **Multi-role documentation** → `docs/{category}/` (applies to 2+ roles)
- **Single-role documentation** → `roles/{role}/README.md` or `roles/{role}/docs/`

**By Category (within `docs/`):**
- `getting-started/` → New users
- `user-guides/` → Using the collection
- `development/` → Contributors
- `maintenance/` → Upgrades/versions

#### 2️⃣ Playbook Organization

**By Role Usage:**
- **Single role examples** → `playbooks/{role}/`
- **General index** → `playbooks/README.md`

#### 3️⃣ Code Organization

**By Scope:**
- **Role-specific code** → `roles/{role}/tasks/`, `roles/{role}/templates/`, etc.
- **Collection-wide plugins** → `plugins/`

### Decision Tree for New Content

```
┌─ Creating Something New?
│
├─ Is it DOCUMENTATION?
│  ├─ Internal planning/analysis? → .tmp/analysis/
│  ├─ Applies to 2+ roles? → docs/{category}/
│  └─ Specific to 1 role? → roles/{role}/README.md or roles/{role}/docs/
│
├─ Is it a PLAYBOOK EXAMPLE?
│  ├─ Uses 1 role? → playbooks/{role}/
│  └─ General index? → playbooks/README.md
│
└─ Is it CODE/FUNCTIONALITY?
   ├─ Specific to 1 role? → roles/{role}/
   └─ Collection-wide? → plugins/
```

### Navigation Pattern

**Every directory MUST have a README.md with:**
- 📝 Purpose description
- 📚 List of contents with descriptions
- 🔗 Links to documents (relative paths)
- 🔙 Navigation back to parent (bidirectional)

## �🏗️ Project Structure Standards

### Root Level Organization
```
ansible-col-devtools/
├── .github/                    # GitHub workflows and configs
├── .tmp/                       # Temporary files and internal analysis
│   └── analysis/              # Project analysis documents (NOT for users)
├── docs/                       # Collection-level documentation (USER-FACING)
│   ├── getting-started/       # Quick start guides
│   ├── user-guides/           # How-to guides
│   ├── development/           # Contributing & testing
│   └── maintenance/           # Upgrades & versions
├── playbooks/                  # Example playbooks (organized by role)
│   ├── docker/                # Docker role examples
│   └── podman/                # Podman role examples
├── plugins/                    # Custom Ansible plugins
│   ├── filter/                # Custom filters
│   └── modules/               # Custom modules
├── roles/                      # Ansible roles (main content)
│   ├── docker/                # Docker role
│   │   └── README.md          # Complete Docker documentation
│   └── podman/                # Podman role
│       ├── README.md          # Complete Podman documentation
│       └── docs/              # Role-specific docs (if needed)
├── galaxy.yml                  # Collection metadata
├── ansible.cfg                 # Ansible configuration
├── requirements.txt            # Python dependencies
├── Makefile                    # Automation commands
├── activate.sh                 # Venv activation script
├── README.md                   # Main documentation
├── CHANGELOG.md               # Version history
├── CONTRIBUTING.md            # Contribution guidelines
├── CODE_OF_CONDUCT.md         # Community standards
└── SECURITY.md                # Security policies
```

### ⚠️ Important: Playbooks Organization

**CRITICAL**: Example playbooks should be organized by role for better maintainability.

- **`playbooks/{role}/`** - Role-specific examples (single role usage)

**Structure:**
```
playbooks/
├── docker/                           # Docker role examples only
│   ├── README.md                    # Index of Docker examples
│   ├── install-docker.yml           # Basic installation
│   ├── setup-registry-auth.yml      # Private registry auth
│   └── setup-insecure-registry.yml  # Insecure registries
└── podman/                           # Podman role examples only
    ├── README.md                    # Index of Podman examples
    └── install-podman.yml           # Production installation with full validation
```

This organization ensures:
- Easy discovery of role-specific examples
- Clear separation of examples by role
- Scalability as new roles are added
- Each role folder has its own README documenting examples

### ⚠️ Important: Analysis Documents Location

**CRITICAL**: Project analysis, planning documents, and internal assessments should be stored in `.tmp/analysis/`, NOT in `docs/`.

- **`.tmp/analysis/`** - Internal planning, analysis, roadmaps (NOT distributed with collection)
- **`docs/`** - User-facing documentation only (distributed with collection)

This separation ensures that:
- Users only see relevant documentation
- Internal planning doesn't clutter the docs
- Collection tarballs stay lean
- Analysis can be gitignored if needed

## 🎯 Role Structure Standards

**CRITICAL**: Every role MUST follow this exact structure:

```
roles/
└── <role_name>/
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

## 🔧 Coding Standards

### Ansible Task Standards
```yaml
---
# ALWAYS use FQCN (Fully Qualified Collection Names)
# ✅ CORRECT
- name: Install packages
  ansible.builtin.package:
    name: "{{ item }}"
    state: present

# ❌ WRONG
- name: Install packages
  package:
    name: "{{ item }}"
    state: present

# ALWAYS add tags
- name: Configure service
  ansible.builtin.service:
    name: docker
    state: started
  tags: docker

# ALWAYS use descriptive names
# ✅ CORRECT
- name: Ensure Docker repository GPG key is present

# ❌ WRONG
- name: Add key
```

### Variable Naming Conventions
```yaml
# Format: <role>_<purpose>_<detail>
docker_version: ""
docker_edition: "ce"
docker_packages: []
docker_users: []
docker_daemon_config: {}
docker_service_enabled: true
docker_service_state: started
docker_configure_repo: true

# Prefix ALL variables with role name to avoid conflicts
```

### Multi-Platform Support Pattern
```yaml
# tasks/main.yml - Orchestration
---
- name: Include OS-specific variables
  ansible.builtin.include_vars: "{{ ansible_os_family }}.yml"
  tags: <role_name>

- name: Include OS-specific tasks
  ansible.builtin.include_tasks: "setup-{{ ansible_os_family }}.yml"
  tags: <role_name>

# Common tasks here...
```

### Handler Standards
```yaml
# handlers/main.yml
---
- name: restart <service>
  ansible.builtin.service:
    name: <service>
    state: restarted

- name: reload <service>
  ansible.builtin.service:
    name: <service>
    state: reloaded
```

### Meta Standards
```yaml
# meta/main.yml
---
galaxy_info:
  role_name: <role_name>
  namespace: code3tech
  author: Code3Tech DevOps Team
  description: <brief description>
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

## 🧪 Testing Standards

### Molecule Configuration
```yaml
# molecule/default/molecule.yml
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

### Pytest Standards
```python
# molecule/default/test_default.py
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
    package = host.package('<package_name>')
    assert package.is_installed


def test_service_running(host):
    """Test that service is running and enabled."""
    service = host.service('<service_name>')
    assert service.is_running
    assert service.is_enabled


def test_user_in_group(host):
    """Test that user is in correct group."""
    # Implement based on role requirements
    pass
```

## 📝 Documentation Standards

### Role README.md Template
```markdown
# Ansible Role: <role_name>

Brief description of what this role does.

## Requirements

- Ansible >= 2.15
- Target system: Ubuntu 22.04+, Debian 11+, or RHEL 9+
- Root or sudo privileges on target hosts

## Role Variables

Available variables with defaults (see `defaults/main.yml`):

\`\`\`yaml
<role>_variable: default_value  # Description
\`\`\`

## Dependencies

None (or list collection/role dependencies).

## Example Playbook

\`\`\`yaml
- hosts: servers
  become: true
  roles:
    - code3tech.devtools.<role_name>
\`\`\`

## Testing

\`\`\`bash
cd roles/<role_name>
molecule test
\`\`\`

## License

MIT

## Author Information

Code3Tech DevOps Team <suporte@kode3.tech>
```

## 🚀 Development Workflow

### 🎯 Documentation and Changelog Update Rules

**CRITICAL**: To optimize the development process, follow these rules strictly:

#### Rule 1: Documentation Updates ONLY When Requested
- ❌ **DO NOT** update documentation during feature implementation
- ❌ **DO NOT** update CHANGELOG.md during feature implementation
- ❌ **DO NOT** update README.md during feature implementation
- ❌ **DO NOT** update META.md during feature implementation
- ✅ **ONLY** update documentation when **explicitly requested** by the user
- ✅ **ONLY** update documentation when user says "update docs" or similar

#### Rule 2: Final Documentation Update on Feature Completion
- ✅ When user explicitly says **"feature finished"**, **"finalize feature"**, **"complete implementation"**, or similar:
  - Update all relevant documentation (README.md, role README.md, etc.)
  - Update CHANGELOG.md with feature description
  - Update META.md if needed
  - Update playbooks/README.md if new examples were added
  - Update collection-level docs if applicable
  - Verify all bidirectional links are correct

#### Workflow Summary

```
┌─ Feature Development Lifecycle
│
├─ 1. IMPLEMENTATION PHASE
│  ├─ Write code
│  ├─ Create tests
│  ├─ Run linters
│  └─ ❌ NO documentation updates
│
├─ 2. TESTING PHASE
│  ├─ Run molecule tests
│  ├─ Fix issues
│  └─ ❌ NO documentation updates
│
└─ 3. FINALIZATION PHASE (User says "feature finished")
   ├─ ✅ Update all documentation
   ├─ ✅ Update CHANGELOG.md
   ├─ ✅ Update README files
   ├─ ✅ Update playbook examples
   └─ ✅ Verify all links
```

#### Exceptions

Documentation updates ARE allowed during implementation ONLY when:
- User **explicitly** asks to "update docs"
- User **explicitly** asks to "document this feature"
- User says "finalize", "complete", "finish feature", or similar completion commands

### Creating a New Role
```bash
# 1. Navigate to roles directory
cd roles/

# 2. Initialize role
ansible-galaxy init <role_name>

# 3. Create Molecule scenario
cd <role_name>
molecule init scenario --driver-name docker

# 4. Customize structure according to standards above

# 5. Implement role following patterns

# 6. Test
molecule test

# 7. Lint
cd ../..
ansible-lint roles/<role_name>/
yamllint roles/<role_name>/

# 8. Documentation (ONLY when user says "feature finished")
# Update README.md, CHANGELOG.md, META.md, etc.
```

### Makefile Commands
```bash
make help               # Show available commands
make install            # Install dependencies
make version            # Show installed versions
make lint               # Run all linters (yamllint + ansible-lint)
make lint-yaml          # Run yamllint only
make lint-ansible       # Run ansible-lint only
make test               # Test all roles
make build              # Build collection tarball
make install-collection # Install collection locally
make publish            # Publish to Galaxy (requires GALAXY_API_KEY)
make clean              # Clean build artifacts
```

## 🎨 YAML Style Guidelines

```yaml
---
# Use --- at the start of YAML files
# Use 2 spaces for indentation (NO TABS)
# Use snake_case for variables
# Use lowercase for boolean values
# Add trailing comma for lists when multiline

# ✅ CORRECT
- name: Configure service
  ansible.builtin.template:
    src: config.j2
    dest: /etc/service/config.yaml
    owner: root
    group: root
    mode: '0644'
  notify: restart service
  tags:
    - configuration
    - service

# List format preference
list_variable:
  - item1
  - item2
  - item3

# Dict format preference
dict_variable:
  key1: value1
  key2: value2
  key3: value3

# Use quotes for:
# - Strings starting with special chars
# - File permissions (mode: '0644')
# - Empty strings ("")
# - Strings with variables when needed
```

## 🔍 Linting Configuration

### Ansible-Lint Rules
- Use `production` profile
- All FQCN required
- No `jinja[spacing]` issues
- No deprecated modules
- Proper task naming (min 3 words)
- See `.ansible-lint` for full config

### Yamllint Rules
- 2 spaces indentation
- Line length: 160 chars
- No trailing spaces
- Proper document start (---)
- See `.yamllint` for full config

## 🔐 Security Standards

- Never commit secrets or credentials
- Use Ansible Vault for sensitive data
- Validate user inputs
- Use `no_log: true` for sensitive tasks
- Follow principle of least privilege

## 📦 Collection Building

### galaxy.yml Requirements
```yaml
namespace: code3tech
name: devtools
version: <semver>
readme: README.md
authors:
  - Code3Tech DevOps Team <suporte@kode3.tech>
description: >-
  Detailed description...
license:
  - MIT
tags:
  - <relevant_tags>
repository: https://github.com/kode3tech/ansible-col-devtools
```

## 🤝 Git Commit Standards

```bash
# Format: <type>(<scope>): <subject>

# Types:
feat     # New feature
fix      # Bug fix
docs     # Documentation changes
style    # Code style changes (formatting)
refactor # Code refactoring
test     # Adding or updating tests
chore    # Maintenance tasks

# Examples:
feat(docker): add support for custom registry
fix(podman): correct storage configuration path
docs(readme): update installation instructions
test(docker): add verification for user groups
chore(deps): update ansible to 2.16
```

## ⚠️ Common Mistakes to Avoid

1. ❌ Using short module names instead of FQCN
2. ❌ Forgetting tags on tasks
3. ❌ Not prefixing variables with role name
4. ❌ Hardcoding OS-specific values in main.yml
5. ❌ Missing handler for service configuration changes
6. ❌ Not testing on multiple distributions
7. ❌ Incomplete or missing documentation
8. ❌ Not using `become` when needed
9. ❌ Missing error handling with `failed_when` or `ignore_errors`
10. ❌ Not making tasks idempotent

## 🎯 Complete Checklist for Creating New Roles

**CRITICAL**: When creating a new role, ALL items in this checklist MUST be completed. This ensures consistency, quality, and adherence to project patterns.

### 📁 Phase 1: Role Structure Setup

- [ ] **1.1** Create role directory: `roles/{role_name}/`
- [ ] **1.2** Create all required directories:
  - [ ] `defaults/` - Default variables
  - [ ] `tasks/` - Task files
  - [ ] `handlers/` - Event handlers
  - [ ] `templates/` - Jinja2 templates (if needed)
  - [ ] `files/` - Static files (if needed)
  - [ ] `vars/` - Variables (OS-specific)
  - [ ] `meta/` - Role metadata
  - [ ] `molecule/default/` - Molecule tests
  - [ ] `tests/` - Legacy test support
- [ ] **1.3** Create `pytest.ini` for test configuration
- [ ] **1.4** Create main `README.md` for role documentation

### 📝 Phase 2: Core Files Implementation

#### Variables & Defaults
- [ ] **2.1** Create `defaults/main.yml` with ALL user-configurable variables
- [ ] **2.2** Prefix ALL variables with role name: `{role}_variable_name`
- [ ] **2.3** Document each variable with inline comments
- [ ] **2.4** Set sensible default values

#### OS-Specific Variables
- [ ] **2.5** Create `vars/Debian.yml` for Debian/Ubuntu variables
- [ ] **2.6** Create `vars/RedHat.yml` for RHEL/CentOS/Rocky variables
- [ ] **2.7** Create `vars/main.yml` for common variables (if needed)

#### Tasks
- [ ] **2.8** Create `tasks/main.yml` as orchestration layer
- [ ] **2.9** Create `tasks/setup-Debian.yml` for Debian/Ubuntu tasks
- [ ] **2.10** Create `tasks/setup-RedHat.yml` for RHEL/CentOS/Rocky tasks
- [ ] **2.11** Use **FQCN** (Fully Qualified Collection Names) for ALL modules
- [ ] **2.12** Add **descriptive names** to ALL tasks (minimum 3 words)
- [ ] **2.13** Add **appropriate tags** to ALL tasks
- [ ] **2.14** Make ALL tasks **idempotent**
- [ ] **2.15** Use `changed_when`, `failed_when` where appropriate

#### Handlers
- [ ] **2.16** Create `handlers/main.yml` with service restart/reload handlers
- [ ] **2.17** Use FQCN in handlers
- [ ] **2.18** Name handlers descriptively (e.g., `restart service_name`)

#### Metadata
- [ ] **2.19** Create `meta/main.yml` with complete galaxy_info:
  - [ ] `namespace: code3tech`
  - [ ] `role_name: {role_name}`
  - [ ] `author: Code3Tech DevOps Team`
  - [ ] `license: MIT`
  - [ ] `min_ansible_version: "2.15"`
  - [ ] Complete `platforms` list:
    ```yaml
    platforms:
      - name: Ubuntu
        versions: [jammy, noble, plucky]  # 22.04, 24.04, 25.04
      - name: Debian
        versions: [bullseye, bookworm, trixie]  # 11, 12, 13
      - name: EL
        versions: ["9", "10"]
    ```
  - [ ] Relevant `galaxy_tags`
- [ ] **2.20** Set `dependencies: []` (or list if needed)

### 🧪 Phase 3: Testing Setup

#### Molecule Configuration
- [ ] **3.1** Create `molecule/default/molecule.yml` with:
  - [ ] Docker driver
  - [ ] **3 platforms minimum**:
    - [ ] Ubuntu 22.04 (geerlingguy/docker-ubuntu2204-ansible)
    - [ ] Debian 12 (geerlingguy/docker-debian12-ansible)
    - [ ] Rocky Linux 9 (geerlingguy/docker-rockylinux9-ansible)
  - [ ] Privileged mode and cgroup configuration
  - [ ] Ansible verifier configuration

- [ ] **3.2** Create `molecule/default/converge.yml` - Apply role playbook
- [ ] **3.3** Create `molecule/default/verify.yml` - Ansible-based verification
- [ ] **3.4** Create `molecule/default/prepare.yml` (if pre-setup needed)

#### Pytest Tests
- [ ] **3.5** Create `molecule/default/test_default.py` with testinfra tests:
  - [ ] Test package installation
  - [ ] Test service running and enabled
  - [ ] Test configuration files exist
  - [ ] Test user/group permissions (if applicable)
  - [ ] Test functionality (basic smoke tests)

#### Legacy Tests
- [ ] **3.6** Create `tests/inventory` - Test inventory file
- [ ] **3.7** Create `tests/test.yml` - Basic test playbook

### 📚 Phase 4: Documentation

#### Role README.md
- [ ] **4.1** Create comprehensive `roles/{role}/README.md` with:
  - [ ] Role description and purpose
  - [ ] Requirements section (Ansible version, target systems, collections)
  - [ ] Supported Distributions list (Ubuntu, Debian, RHEL with versions)
  - [ ] Role Variables section (ALL variables documented)
  - [ ] Dependencies section
  - [ ] Example Playbook section (multiple examples)
  - [ ] Testing instructions
  - [ ] License (MIT)
  - [ ] Author Information (Code3Tech DevOps Team)

#### Role-Specific Documentation (if needed)
- [ ] **4.2** Create `roles/{role}/docs/` for additional documentation (if role is complex)
- [ ] **4.3** Create `roles/{role}/docs/README.md` with index of additional docs
- [ ] **4.4** Add links from main README to additional docs

#### Collection Documentation (for multi-role features)
- [ ] **4.5** If feature applies to 2+ roles, create doc in `docs/{category}/`
- [ ] **4.6** Update `docs/README.md` with link to new document

### 🎮 Phase 5: Example Playbooks

- [ ] **5.1** Create `playbooks/{role}/` directory
- [ ] **5.2** Create `playbooks/{role}/README.md` with:
  - [ ] Index of all example playbooks
  - [ ] Description of each example
  - [ ] Usage instructions
  - [ ] Links to role README
- [ ] **5.3** Create example playbooks (minimum 2):
  - [ ] `install-{role}.yml` - Basic installation
  - [ ] `setup-{feature}.yml` - Advanced feature example
- [ ] **5.4** Ensure each playbook has:
  - [ ] Clear comments
  - [ ] Variable examples
  - [ ] Proper tags
  - [ ] Error handling
- [ ] **5.5** Update `playbooks/README.md` with new role examples

### 🔍 Phase 6: Quality Assurance

#### Linting
- [ ] **6.1** Run `ansible-lint` (production profile) - ZERO errors
- [ ] **6.2** Run `yamllint` - ZERO errors
- [ ] **6.3** Fix all linting issues

#### Testing
- [ ] **6.4** Run `molecule test` - ALL tests pass on ALL platforms
- [ ] **6.5** Verify tests on:
  - [ ] Ubuntu 22.04
  - [ ] Debian 12
  - [ ] Rocky Linux 9
- [ ] **6.6** All pytest tests pass
- [ ] **6.7** All Ansible verification tests pass

#### Code Review
- [ ] **6.8** Review all variable names (prefixed with role name)
- [ ] **6.9** Review all task names (descriptive, 3+ words)
- [ ] **6.10** Review all tags (appropriate and consistent)
- [ ] **6.11** Review OS-specific logic (properly separated)
- [ ] **6.12** Review idempotency (tasks can run multiple times safely)

### 📦 Phase 7: Collection Integration

#### Update Collection Files
- [ ] **7.1** Update `README.md` - Add new role to "Included Roles" section
- [ ] **7.2** Update `META.md` - Add role description and supported platforms
- [ ] **7.3** Update `galaxy.yml` if needed
- [ ] **7.4** Update `CHANGELOG.md` - Add entry for new role

#### Update Documentation
- [ ] **7.5** Update `docs/development/ROLE_STRUCTURE.md` if pattern changed
- [ ] **7.6** Create user guide in `docs/user-guides/` if needed

### 🚀 Phase 8: Final Verification

- [ ] **8.1** Git status clean (no untracked files that should be committed)
- [ ] **8.2** All documentation has bidirectional links
- [ ] **8.3** All README.md files have navigation links
- [ ] **8.4** Role follows ALL project patterns:
  - [ ] Organization by scope
  - [ ] Documentation in correct location
  - [ ] Playbooks in `playbooks/{role}/`
  - [ ] Variables prefixed correctly
  - [ ] FQCN used everywhere
  - [ ] Multi-platform support
  - [ ] Complete testing
- [ ] **8.5** Commit with conventional commit message:
  ```
  feat(roles): add {role_name} role
  
  - Implements {brief description}
  - Supports Ubuntu 22.04+, Debian 11+, RHEL 9+
  - Includes comprehensive tests (Molecule + Pytest)
  - Adds example playbooks
  - Complete documentation
  
  Closes #{issue_number}
  ```

---

## 🎯 Quick Reference Checklist

Use this abbreviated checklist for quick verification:

- [ ] Role structure follows standard (all directories created)
- [ ] All tasks use FQCN
- [ ] All tasks have descriptive names
- [ ] All tasks have appropriate tags
- [ ] Variables prefixed with role name
- [ ] OS-specific logic separated (Debian.yml, RedHat.yml)
- [ ] Handlers defined for service changes
- [ ] Meta/main.yml complete with platforms (Ubuntu 22/24/25, Debian 11/12/13, RHEL 9/10)
- [ ] README.md with complete documentation and examples
- [ ] Molecule tests configured (3+ distros: Ubuntu, Debian, RHEL)
- [ ] Pytest tests implemented with full coverage
- [ ] Passes ansible-lint (production profile) - ZERO errors
- [ ] Passes yamllint - ZERO errors
- [ ] Default values in defaults/main.yml
- [ ] Example playbooks in `playbooks/{role}/` (minimum 2)
- [ ] `playbooks/{role}/README.md` with playbook index
- [ ] Collection docs updated (README.md, META.md, CHANGELOG.md)
- [ ] All documentation follows organization pattern
- [ ] Bidirectional navigation links in place

## 🌟 Best Practices Summary

1. **Always** use FQCN for modules
2. **Always** tag your tasks
3. **Always** name tasks descriptively
4. **Always** support multiple OS families
5. **Always** make tasks idempotent
6. **Always** test on multiple distributions
7. **Always** document variables and examples
8. **Always** run linters before committing
9. **Always** follow semantic versioning
10. **Always** update CHANGELOG.md

---

## 📚 Documentation Organization

### Documentation Structure Principle

Documentation is organized by **scope**:
- **Collection-level documentation** → `docs/` (organized in categories)
- **Role-specific documentation** → `roles/{role}/README.md` (main docs) or `roles/{role}/docs/` (additional docs)

### Collection Documentation (`docs/`)

Documentation in `docs/` is organized into **4 categories**:

#### 1. `getting-started/` - Quick Start & Setup
- Quick start guides
- Installation instructions
- Initial configuration
- **For:** New users getting started

#### 2. `user-guides/` - How-To Guides
- Using collection features
- Common use cases
- Configuration examples
- **For:** Users learning to use the collection

#### 3. `development/` - Contributing & Development
- Contributing guidelines
- Role structure documentation
- Testing guides (in `development/testing/`)
- Architecture documentation
- **For:** Contributors and developers

#### 4. `maintenance/` - Upgrades & Versions
- Upgrade guides
- Version information
- Deprecation notices
- Breaking changes
- **For:** Users upgrading or maintaining installations

### Internal Analysis (`..tmp/analysis/`)

### Internal Analysis (`.tmp/analysis/`)

**NOT part of user documentation!** Internal project planning and analysis:
- Project analysis documents
- Planning documents
- Internal assessments
- Roadmaps and action plans
- **For:** Maintainers and core team only
- **Important:** NOT distributed with the collection tarball

### Role Documentation (`roles/{role}/`)

Each role maintains its own documentation:

#### Main Documentation
- **`roles/{role}/README.md`** - Primary role documentation
  - Complete role description
  - All variables documented
  - Usage examples
  - Requirements and dependencies
  - Performance tuning
  - Security considerations

#### Additional Documentation (Optional)
- **`roles/{role}/docs/`** - Role-specific guides
  - Create only when needed
  - Use for complex role-specific topics
  - Link from main README.md

### Documentation Decision Criteria

#### When to Document in `docs/` (Collection-level)
✅ Feature applies to **multiple roles** (e.g., registry authentication for Docker + Podman)  
✅ General collection usage  
✅ Cross-role integration  
✅ Development/testing/contributing  

#### When to Document in `roles/{role}/` (Role-level)
✅ Feature is **exclusive to one role** (e.g., Podman XDG_RUNTIME_DIR fix)  
✅ Role-specific configuration  
✅ Advanced role features  

#### When in Doubt
- If it applies to **2+ roles** → `docs/`
- If it's **role-specific** → `roles/{role}/docs/`
- If it's **general usage** → Start in role README, move to `docs/` if it grows

### Documentation Index Files

Every documentation directory **MUST** have a `README.md` index:
- **Purpose:** Navigation and overview
- **Content:** List of documents with brief descriptions
- **Links:** Relative links to documents
- **Navigation:** Link back to parent index

### Example Documentation References

**Note**: The examples below show correct relative paths **from the perspective of the source file**, not from this copilot-instructions.md file. Use these patterns when writing documentation in the appropriate locations.

```markdown
# In role README.md (e.g., roles/podman/README.md) - referencing collection docs
See [Registry Authentication](../docs/user-guides/REGISTRY_AUTHENTICATION.md) for details.

# In collection docs (e.g., docs/user-guides/SOME_GUIDE.md) - referencing role docs
See [Docker Role](../roles/docker/README.md) for Docker-specific configuration.
```

### Maintaining Documentation

1. **Keep indexes updated** - When adding docs, update parent README.md
2. **Update links** - When moving/renaming files, update all references
3. **Follow structure** - Place docs in appropriate category
4. **Create indexes** - New directories need README.md indexes
5. **Link bidirectionally** - Reference both ways (collection ↔ role)

---

## 📐 Documentation Quality Standards

**CRITICAL**: When user requests to "update documentation", "improve docs", "document feature", or similar commands, **ALL** of the following standards MUST be applied systematically.

### Quick Reference: The 14 Documentation Standards

| # | Standard | When to Apply | Impact |
|---|----------|---------------|--------|
| 1️⃣ | **Language Consistency** | All docs must be English | CRITICAL |
| 2️⃣ | **Bidirectional Navigation** | All docs need `[← Back]` links | CRITICAL |
| 3️⃣ | **Table of Contents (TOC)** | Docs > 100 lines | HIGH |
| 4️⃣ | **DRY Principle** | Content duplicated 2+ places | HIGH |
| 5️⃣ | **Link Validation** | All links must work | CRITICAL |
| 6️⃣ | **Centralized References** | FAQ, Variables reference | MEDIUM |
| 7️⃣ | **Semantic Emoji Usage** | Consistent emoji meanings | LOW |
| 8️⃣ | **Directory Index Files** | Every dir needs README.md | HIGH |
| 9️⃣ | **Code Examples Progression** | Simple → Complex | MEDIUM |
| 🔟 | **Variable Documentation** | Consistent format everywhere | HIGH |
| 1️⃣1️⃣ | **Security Warnings** | Prominent warnings for risks | CRITICAL |
| 1️⃣2️⃣ | **Checklist Format** | Use `- [ ]` checkboxes | LOW |
| 1️⃣3️⃣ | **Update Metadata** | CHANGELOG, indexes, etc. | HIGH |
| 1️⃣4️⃣ | **Documentation Workflow** | Systematic 5-step process | CRITICAL |

---

### 🌍 Standard 1: Language Consistency

**Rule**: ALL documentation MUST be written in **English** (US/International).

- ✅ **ALWAYS** write new documentation in English
- ✅ **ALWAYS** translate existing Portuguese (PT-BR) content to English
- ❌ **NEVER** mix Portuguese and English in the same document
- ❌ **NEVER** leave Portuguese comments, headers, or examples

**Applies to**:
- All `.md` files in `docs/`, `roles/`, `playbooks/`
- All code comments in YAML files
- All commit messages
- All examples and snippets

**Exception**: User-facing messages that need localization (NOT applicable to this project currently).

### 🔗 Standard 2: Bidirectional Navigation

**Rule**: Every document MUST have a navigation link back to its parent/index.

**Format**:
```markdown
[← Back to {Parent Section}](README.md)
```

**Placement**: At the **bottom** of the document, after all content, before any horizontal rules.

**Examples**:
```markdown
# In docs/user-guides/REGISTRY_AUTHENTICATION.md
[← Back to User Guides](README.md)

# In roles/docker/README.md  
[← Back to Roles](../README.md)

# In docs/getting-started/QUICKSTART.md
[← Back to Getting Started](README.md)
```

**Applies to**:
- All documents in `docs/` subdirectories
- All role README.md files
- All playbook README.md files
- Any document more than 2 levels deep

**Exception**: Root-level files (main README.md, CONTRIBUTING.md) don't need back navigation.

### 📑 Standard 3: Table of Contents (TOC)

**Rule**: Documents with **100+ lines** MUST have a Table of Contents.

**Placement**: After the main title, before the first section.

**Format**:
```markdown
# Document Title

Brief description (1-2 sentences).

## 📋 Table of Contents

- [Section 1](#section-1)
- [Section 2](#section-2)
  - [Subsection 2.1](#subsection-21)
- [Section 3](#section-3)
```

**Requirements**:
- Use `##` for "Table of Contents" heading
- Include emoji 📋 before "Table of Contents"
- Link to ALL main sections (`##` level)
- Include subsections (`###`) if document has 5+ subsections
- Use lowercase, hyphenated anchor links

**Applies to**:
- All role README.md files (typically 200-400 lines)
- Long user guides (> 100 lines)
- CONTRIBUTING.md, CHANGELOG.md if long
- Any technical documentation > 100 lines

**Exception**: Short docs under 100 lines don't need TOC.

### 🔄 Standard 4: DRY Principle (Don't Repeat Yourself)

**Rule**: Detailed content should exist in **ONE place only**. Other locations should have **summaries + links**.

**Pattern**:
```markdown
# In role README.md (e.g., roles/docker/README.md) - SUMMARY
### Registry Authentication

Quick example:
```yaml
docker_registries_auth:
  - registry: "ghcr.io"
    username: "myuser"
    password: "{{ vault_token }}"
```

📖 **Complete guide**: [Registry Authentication](../docs/user-guides/REGISTRY_AUTHENTICATION.md)

# In docs/user-guides/REGISTRY_AUTHENTICATION.md - COMPLETE
[Full detailed content with all examples, explanations, security notes]
```

**Reduction Target**: When applying DRY, aim to reduce duplicated sections by **50-70%** (keep 30-50% as summary).

**Summary Components**:
1. **Brief description** (1-2 sentences)
2. **Quick example** (simplest use case)
3. **Link to complete guide** (with emoji 📖)

**Applies to**:
- Registry authentication (Docker + Podman roles)
- LXC container configuration (Docker + Podman roles)
- Testing procedures (if repeated across roles)
- Security considerations (if repeated)

**When to apply**:
- Content appears in **2+ places**
- Section exceeds **30 lines** in role README
- Same examples repeated verbatim
- Same security warnings repeated

**Decision**: 
- If content applies to **2+ roles** → Full version in `docs/`, summaries in role READMEs
- If content is **role-specific** → Full version in `roles/{role}/docs/`, summary in role README

### 🔍 Standard 5: Link Validation

**Rule**: ALL links MUST be valid and use correct relative paths.

**Validation checklist**:
- [ ] All `[text](path)` links point to existing files
- [ ] All anchor links `#section` match actual heading IDs
- [ ] All relative paths are correct from document location
- [ ] No broken links after file moves/renames
- [ ] Cross-references between docs/ and roles/ use correct `../../` navigation

**Common patterns**:
```markdown
# From roles/docker/ to docs/user-guides/
../docs/user-guides/REGISTRY_AUTHENTICATION.md

# From docs/getting-started/ to roles/docker/
../roles/docker/README.md

# From playbooks/docker/ to roles/docker/
../roles/docker/README.md
```

**Testing**: When updating links, verify by:
1. Checking file exists at specified path
2. Testing anchor links match heading structure
3. Verifying relative path depth matches directory nesting

### 📚 Standard 6: Centralized References

**Rule**: Common questions and reference material should be centralized, not scattered.

**Centralized documents**:
- **`docs/FAQ.md`** - All frequently asked questions
- **`docs/reference/VARIABLES.md`** - All role variables reference
- **`docs/reference/README.md`** - Index of all reference material

**When to add to FAQ**:
- Question appears in 2+ role READMEs
- Common user question from issues/discussions
- Conceptual questions (not role-specific)

**When to add to VARIABLES.md**:
- New role variables added
- Variable behavior changes
- Security-sensitive variables
- Performance-tuning variables

**Update requirement**: When adding content to FAQ or VARIABLES, MUST also update:
1. Parent `docs/README.md` - link in appropriate category
2. Parent `docs/reference/README.md` - link with description
3. Related role READMEs - link to centralized content instead of duplicating

### 🏷️ Standard 7: Semantic Emoji Usage

**Rule**: Use emojis consistently for visual navigation and meaning.

**Standard emoji meanings**:
```markdown
📋 - Table of Contents
📝 - Documentation / Writing
📚 - Documentation section / Library
🔗 - Links / References
🔙 - Back navigation
📖 - Complete guide / Full documentation
⚠️ - Warning / Important note
✅ - Correct / Recommended
❌ - Wrong / Not recommended
🎯 - Goal / Objective
🚀 - Getting started / Quick start
🔧 - Configuration / Tools
🧪 - Testing
🔍 - Search / Investigation
💡 - Tip / Insight
🔐 - Security
🌍 - Language / International
🔄 - Process / Workflow
📦 - Package / Component
🏗️ - Architecture / Structure
📞 - Support / Contact
🌟 - Best practices / Important
```

**Usage**:
- Use **ONE** emoji per heading (not multiple)
- Place emoji **before** heading text with space: `## 📋 Table of Contents`
- Use same emoji for same concept across all docs
- Don't overuse - only for main sections, not every paragraph

### 📝 Standard 8: Directory Index Files

**Rule**: Every directory with multiple documents MUST have a `README.md` index.

**Required content**:
1. **Purpose** - What this directory contains (1-2 sentences)
2. **Document list** - Table with Name, Description
3. **Links** - Relative links to each document
4. **Back navigation** - Link to parent index

**Template**:
```markdown
# {Category Name}

Brief description of what this category contains.

## Documents

| Document | Description |
|----------|-------------|
| [Document Name](DOCUMENT.md) | Brief description of content |
| [Another Document](ANOTHER.md) | Brief description of content |

## Quick Links

- [Main Documentation](../README.md)
- [Related Category](../category/README.md)

[← Back to Documentation](../README.md)
```

**Applies to**:
- `docs/getting-started/README.md`
- `docs/user-guides/README.md`
- `docs/development/README.md`
- `docs/maintenance/README.md`
- `docs/reference/README.md`
- `playbooks/{role}/README.md`
- `roles/{role}/docs/README.md` (if docs/ exists)

### 🔢 Standard 9: Code Examples Progression

**Rule**: Examples should progress from **simple → complex**.

**Pattern**:
```markdown
## Example Playbook

### Basic Installation
[Simplest possible example - no variables]

### With Custom Configuration
[Add 1-2 common variables]

### Advanced Setup
[Complex scenario with multiple features]

### Production Example
[Real-world scenario with all best practices]
```

**Requirements**:
- Start with **minimal working example** (< 10 lines)
- Each example adds **ONE new concept**
- Label complexity: "Basic", "Intermediate", "Advanced", "Production"
- Include comments explaining **why**, not just **what**
- Always show **working code**, not pseudo-code

### 📊 Standard 10: Variable Documentation Format

**Rule**: Variables MUST be documented with consistent format.

**In `defaults/main.yml`** (inline comments):
```yaml
# Docker edition: "ce" (Community Edition) or "ee" (Enterprise Edition)
docker_edition: "ce"

# List of Docker packages to install
docker_packages:
  - "docker-{{ docker_edition }}"
  - "docker-{{ docker_edition }}-cli"
  - containerd.io

# Users to add to docker group (password-less docker access)
# WARNING: Users in docker group have root-equivalent privileges!
docker_users: []
```

**In role README.md** (variables section):
```markdown
## Role Variables

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `docker_edition` | string | No | `"ce"` | Docker edition: "ce" or "ee" |
| `docker_packages` | list | No | `[...]` | Packages to install |
| `docker_users` | list | No | `[]` | Users for docker group |
```

**In `docs/reference/VARIABLES.md`** (complete reference):
```markdown
### `docker_edition`

- **Type**: String
- **Required**: No
- **Default**: `"ce"`
- **Valid values**: `"ce"`, `"ee"`
- **Description**: Docker edition to install
- **Example**:
  ```yaml
  docker_edition: "ce"
  ```
- **Notes**: Community Edition (ce) is free, Enterprise (ee) requires license
```

### ⚙️ Standard 11: Security Warnings Format

**Rule**: Security-sensitive content MUST have prominent warnings.

**Format**:
```markdown
**⚠️ Security Warning**: Brief warning in bold

Detailed explanation of the security implications...

**Recommended**: Secure alternative or best practice
```

**Example**:
```markdown
**⚠️ Security Warning**: Users in the `docker` group have root-equivalent privileges!

Adding users to the docker group allows them to run containers with root privileges,
potentially compromising system security. Only add trusted users.

**Recommended**: Use rootless Podman for unprivileged container management, or implement
additional access controls with sudo policies.
```

**Applies to**:
- User privileges (docker group, sudo)
- Credential management (passwords, tokens)
- Insecure registries (HTTP, self-signed certs)
- Network exposure (ports, firewalls)
- File permissions (sensitive configs)

### 📋 Standard 12: Checklist Format

**Rule**: Action items MUST use GitHub-flavored Markdown checkboxes.

**Format**:
```markdown
- [ ] **Phase 1**: Description of task
  - [ ] Subtask 1
  - [ ] Subtask 2
- [ ] **Phase 2**: Description of task
```

**Requirements**:
- Use `- [ ]` for unchecked items
- Use `- [x]` for completed items (in progress tracking)
- Bold phase/section names: `**Phase 1**:`
- Indent subtasks with 2 spaces
- Number phases if sequential: `**Phase 1**`, `**Phase 2**`

**Applies to**:
- Complete Role Creation Checklist
- Feature implementation checklists
- Documentation update checklists
- Migration guides step-by-step

### 🎯 Standard 13: Update Metadata

**Rule**: When documentation is updated, related metadata MUST be updated.

**Files to check**:
```markdown
1. `CHANGELOG.md` - Add entry in [Unreleased] section
2. `META.md` - Update if capabilities/features changed
3. Parent `README.md` files - Update indexes/links
4. `docs/README.md` - Update if new category/major doc added
5. `playbooks/README.md` - Update if new examples added
```

**CHANGELOG.md format**:
```markdown
## [Unreleased]

### Documentation
- Enhanced Docker role README with TOC and improved examples
- Added centralized FAQ (39 questions)
- Created complete variables reference
- Translated all PT-BR content to English
```

**When NOT to update CHANGELOG**:
- Minor typo fixes
- Link corrections
- Formatting improvements (unless major)
- Internal analysis documents (`.tmp/analysis/`)

### 🔄 Standard 14: Documentation Update Workflow

**Rule**: Follow systematic workflow when user requests documentation updates.

**Workflow**:
```
1. ANALYZE SCOPE
   ├─ What needs updating? (specific files or entire project)
   ├─ What type of update? (new content, translation, restructure, fixes)
   └─ Priority level? (critical, medium, low)

2. IDENTIFY PATTERNS
   ├─ Check for language inconsistencies (PT-BR → EN)
   ├─ Check for missing TOCs (> 100 lines)
   ├─ Check for missing back navigation
   ├─ Check for broken links
   ├─ Check for duplicated content (DRY violations)
   └─ Check for missing centralized references

3. APPLY STANDARDS (in order)
   ├─ Standard 1: Language consistency (if needed)
   ├─ Standard 2: Bidirectional navigation (if missing)
   ├─ Standard 3: TOC (if document > 100 lines)
   ├─ Standard 4: DRY principle (if duplication found)
   ├─ Standard 5: Link validation (fix broken links)
   ├─ Standards 6-13: Apply as applicable
   └─ Standard 13: Update metadata (CHANGELOG, indexes)

4. VERIFY QUALITY
   ├─ All links work
   ├─ All TOCs complete
   ├─ All back navigation present
   ├─ Language consistent
   ├─ No duplication
   └─ Metadata updated

5. REPORT COMPLETION
   └─ Summarize changes made (brief, factual)
```

**Batch operations**: When multiple files need same fix (e.g., translation), use `multi_replace_string_in_file` for efficiency.

**Priority handling**:
- **CRITICAL**: Language, broken links, missing navigation
- **MEDIUM**: TOC, DRY, centralization
- **LOW**: Formatting, emoji consistency, examples

### 📝 Example: Applying Documentation Standards

**User Request**: "Update the Docker role documentation"

**Expected Agent Actions**:

1. **Read current state** of `roles/docker/README.md`
2. **Check all 14 standards**:
   - ✅ Standard 1: Is it in English? (check for PT-BR)
   - ✅ Standard 2: Does it have back navigation link?
   - ✅ Standard 3: If > 100 lines, does it have TOC?
   - ✅ Standard 4: Any duplicated content? (check against docs/)
   - ✅ Standard 5: Are all links valid?
   - ✅ Standard 6: Should content be in FAQ/VARIABLES?
   - ✅ Standard 7: Consistent emoji usage?
   - ✅ Standard 8: Does playbooks/docker/ have README index?
   - ✅ Standard 9: Examples progress from simple to complex?
   - ✅ Standard 10: Variables documented consistently?
   - ✅ Standard 11: Security warnings properly formatted?
   - ✅ Standard 12: Checklists use `- [ ]` format?
   - ✅ Standard 13: Need to update CHANGELOG.md?
   - ✅ Standard 14: Following the workflow?

3. **Apply fixes** using appropriate tools:
   - Use `multi_replace_string_in_file` for multiple related changes
   - Use `replace_string_in_file` for single targeted changes
   - Use `create_file` for new FAQ entries or reference docs

4. **Verify quality**:
   - All standards applied
   - No broken links
   - Consistent format

5. **Report completion**:
   - Brief summary of changes
   - Standards applied
   - Files modified

**User Request**: "Translate PT-BR content in documentation"

**Expected Agent Actions**:

1. **Identify scope**: Find all `.md` files with Portuguese content
2. **Batch operation**: Use `multi_replace_string_in_file` for efficiency
3. **Apply all standards**: Not just translation - also check navigation, TOC, links, etc.
4. **Update metadata**: CHANGELOG.md entry if significant changes
5. **Report**: List of files translated + other improvements made

---

## 📞 Support

For questions or issues:
- GitHub Issues: https://github.com/kode3tech/ansible-devtools/issues
- Email: suporte@kode3.tech

---

**Remember**: Quality over speed. Follow these standards for consistency and maintainability! 🚀
