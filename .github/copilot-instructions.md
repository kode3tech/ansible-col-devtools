# GitHub Copilot Instructions - kode3tech.devtools Ansible Collection

## 📋 Project Overview

This is an **Ansible Collection** project following official Ansible best practices and Galaxy standards.

- **Collection Name**: `kode3tech.devtools`
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
- `troubleshooting/` → Problem solving
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
│   ├── troubleshooting/       # Problem solving
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
    ├── install-podman.yml           # Basic installation
    └── test-podman-auth.yml         # Authentication testing
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
  namespace: kode3tech
  author: Kode3Tech DevOps Team
  description: <brief description>
  company: Kode3Tech
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
    - kode3tech.devtools.<role_name>
\`\`\`

## Testing

\`\`\`bash
cd roles/<role_name>
molecule test
\`\`\`

## License

MIT

## Author Information

Kode3Tech DevOps Team <devops@kode3.com.br>
```

## 🚀 Development Workflow

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
```

### Makefile Commands
```bash
make help              # Show available commands
make install           # Install dependencies
make lint              # Run all linters
make test-<role>       # Test specific role
make test-all          # Test all roles
make build             # Build collection tarball
make install-collection # Install locally
make publish           # Publish to Galaxy
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
namespace: kode3tech
name: devtools
version: <semver>
readme: README.md
authors:
  - Kode3Tech DevOps Team <devops@kode3.com.br>
description: >-
  Detailed description...
license:
  - MIT
tags:
  - <relevant_tags>
repository: https://github.com/kode3tech/ansible-devtools
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
  - [ ] `namespace: kode3tech`
  - [ ] `role_name: {role_name}`
  - [ ] `author: Kode3Tech DevOps Team`
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
  - [ ] Author Information (Kode3Tech DevOps Team)

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
- [ ] **7.7** Create troubleshooting guide in `docs/troubleshooting/` if needed

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

Documentation in `docs/` is organized into **5 categories**:

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

#### 3. `troubleshooting/` - Problem Solving
- Common issues and solutions
- Platform-specific problems
- Error resolution
- **For:** Users encountering problems

#### 4. `development/` - Contributing & Development
- Contributing guidelines
- Role structure documentation
- Testing guides (in `development/testing/`)
- Architecture documentation
- **For:** Contributors and developers

#### 5. `maintenance/` - Upgrades & Versions
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
✅ Collection-wide troubleshooting  
✅ Development/testing/contributing  

#### When to Document in `roles/{role}/` (Role-level)
✅ Feature is **exclusive to one role** (e.g., Podman XDG_RUNTIME_DIR fix)  
✅ Role-specific configuration  
✅ Role-specific troubleshooting  
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

```markdown
# In role README.md - referencing collection docs
See [Registry Authentication](../../docs/user-guides/REGISTRY_AUTHENTICATION.md) for details.

# In role README.md - referencing role-specific docs
See [XDG Runtime Fix](docs/PODMAN_XDG_RUNTIME_FIX.md) for troubleshooting.

# In collection docs - referencing role docs
See [Docker Role](../roles/docker/README.md) for Docker-specific configuration.
```

### Maintaining Documentation

1. **Keep indexes updated** - When adding docs, update parent README.md
2. **Update links** - When moving/renaming files, update all references
3. **Follow structure** - Place docs in appropriate category
4. **Create indexes** - New directories need README.md indexes
5. **Link bidirectionally** - Reference both ways (collection ↔ role)

---


## 📞 Support

For questions or issues:
- GitHub Issues: https://github.com/kode3tech/ansible-devtools/issues
- Email: devops@kode3.com.br

---

**Remember**: Quality over speed. Follow these standards for consistency and maintainability! 🚀
