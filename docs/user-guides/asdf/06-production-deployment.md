# Production Deployment

Complete production playbook with pre-tasks, validation, and post-tasks for enterprise asdf deployments.

---

## 📋 Table of Contents

- [Production Playbook Structure](#production-playbook-structure)
- [Pre-Tasks: Environment Preparation](#pre-tasks-environment-preparation)
- [Role Configuration](#role-configuration)
- [Post-Tasks: Validation](#post-tasks-validation)
- [Complete Production Playbook](#complete-production-playbook)
- [CI/CD Integration](#cicd-integration)

---

## Production Playbook Structure

A production-ready asdf playbook has three phases:

```
┌─────────────────────────────────────────────────────────────┐
│                    PRODUCTION PLAYBOOK                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. PRE-TASKS                                               │
│     ├── Time synchronization                                │
│     ├── Internet connectivity check                         │
│     ├── Disk space verification                             │
│     └── User existence validation                           │
│                                                              │
│  2. ROLE EXECUTION                                          │
│     ├── Install asdf                                        │
│     ├── Configure group permissions                         │
│     ├── Install plugins and versions                        │
│     └── Configure user shells                               │
│                                                              │
│  3. POST-TASKS                                              │
│     ├── Verify asdf installation                            │
│     ├── Validate installed plugins                          │
│     ├── Test shim functionality                             │
│     └── Verify user access                                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Pre-Tasks: Environment Preparation

### Time Synchronization

Critical for GPG key validation during package installation:

```yaml
pre_tasks:
  # ==========================================================================
  # TIME SYNCHRONIZATION - CRITICAL FOR GPG KEY VALIDATION
  # ==========================================================================
  
  - name: "[TimeSync] Ensure chrony is installed (RedHat)"
    ansible.builtin.dnf:
      name: chrony
      state: present
    when: ansible_os_family in ['RedHat', 'Rocky', 'AlmaLinux']
    tags: [prereq, timesync]
  
  - name: "[TimeSync] Start and enable chronyd (RedHat)"
    ansible.builtin.service:
      name: chronyd
      state: started
      enabled: true
    when: ansible_os_family in ['RedHat', 'Rocky', 'AlmaLinux']
    tags: [prereq, timesync]
  
  - name: "[TimeSync] Force time synchronization (RedHat)"
    ansible.builtin.command:
      cmd: chronyc makestep
    changed_when: false
    when: ansible_os_family in ['RedHat', 'Rocky', 'AlmaLinux']
    tags: [prereq, timesync]
  
  - name: "[TimeSync] Ensure systemd-timesyncd is installed (Debian)"
    ansible.builtin.apt:
      name: systemd-timesyncd
      state: present
      update_cache: true
    when: ansible_os_family == 'Debian'
    tags: [prereq, timesync]
```

### System Requirements Check

```yaml
  # ==========================================================================
  # SYSTEM REQUIREMENTS
  # ==========================================================================
  
  - name: "[PreCheck] Verify internet connectivity"
    ansible.builtin.uri:
      url: "https://github.com"
      method: GET
      timeout: 10
    register: internet_check
    failed_when: false
    tags: [prereq, connectivity]
  
  - name: "[PreCheck] Fail if no internet connectivity"
    ansible.builtin.fail:
      msg: "Cannot reach GitHub. Internet connectivity required for asdf installation."
    when: internet_check.status is not defined or internet_check.status != 200
    tags: [prereq, connectivity]
  
  - name: "[PreCheck] Check available disk space"
    ansible.builtin.command: df -h /opt
    register: disk_space
    changed_when: false
    tags: [prereq, diskspace]
  
  - name: "[PreCheck] Display disk space"
    ansible.builtin.debug:
      msg: "Available disk space:\n{{ disk_space.stdout }}"
    tags: [prereq, diskspace]
```

### User Validation

```yaml
  # ==========================================================================
  # USER VALIDATION
  # ==========================================================================
  
  - name: "[UserCheck] Verify configured users exist"
    ansible.builtin.getent:
      database: passwd
      key: "{{ item }}"
    loop: "{{ asdf_users }}"
    register: user_check
    failed_when: false
    tags: [prereq, users]
  
  - name: "[UserCheck] Report missing users"
    ansible.builtin.debug:
      msg: "WARNING: User '{{ item.item }}' does not exist"
    loop: "{{ user_check.results }}"
    when: item.failed | default(false)
    tags: [prereq, users]
```

---

## Role Configuration

### Basic Configuration

```yaml
vars:
  # ==========================================================================
  # BASIC CONFIGURATION
  # ==========================================================================
  asdf_version: "latest"              # Use latest asdf version
  asdf_install_dir: "/opt/asdf"       # System-wide installation
  asdf_install_dependencies: true     # Install build tools
  asdf_configure_shell: true          # Configure user shells
  asdf_shell_profile: "bashrc"        # Default shell profile
```

### User Configuration

```yaml
  # ==========================================================================
  # USER CONFIGURATION
  # ==========================================================================
  asdf_users:
    - "{{ ansible_user }}"            # Current SSH user
    # - "developer"
    # - "jenkins"
```

### Plugin Configuration

```yaml
  # ==========================================================================
  # PLUGIN CONFIGURATION
  # ==========================================================================
  asdf_plugins:
    # Lightweight plugins (fast installation)
    - name: "direnv"
      versions: ["2.35.0"]
      global: "2.35.0"
    
    - name: "jq"
      versions: ["1.7.1"]
      global: "1.7.1"
    
    # Heavy plugins (require compilation)
    - name: "nodejs"
      versions: ["22.11.0", "20.18.0"]
      global: "22.11.0"
    
    - name: "python"
      versions: ["3.13.0", "3.12.7"]
      global: "3.13.0"
```

---

## Post-Tasks: Validation

### Basic Verification

```yaml
post_tasks:
  # ==========================================================================
  # VERIFICATION
  # ==========================================================================
  
  - name: "[Verify] Check asdf installation"
    ansible.builtin.command: "{{ asdf_install_dir }}/bin/asdf --version"
    register: asdf_version_result
    changed_when: false
    tags: [verify, asdf]
  
  - name: "[Verify] Display asdf version"
    ansible.builtin.debug:
      msg: "asdf version: {{ asdf_version_result.stdout }}"
    tags: [verify, asdf]
```

### Plugin Validation

```yaml
  - name: "[Verify] List installed plugins"
    ansible.builtin.command: "{{ asdf_install_dir }}/bin/asdf plugin list"
    register: installed_plugins
    environment:
      ASDF_DIR: "{{ asdf_install_dir }}"
      ASDF_DATA_DIR: "{{ asdf_install_dir }}"
    changed_when: false
    tags: [verify, plugins]
  
  - name: "[Verify] Display installed plugins"
    ansible.builtin.debug:
      msg: "Installed plugins:\n{{ installed_plugins.stdout }}"
    tags: [verify, plugins]
```

### Functionality Tests

```yaml
  - name: "[FuncTest] Test nodejs functionality"
    ansible.builtin.command: "{{ asdf_install_dir }}/shims/node --version"
    register: nodejs_test
    environment:
      ASDF_DIR: "{{ asdf_install_dir }}"
      ASDF_DATA_DIR: "{{ asdf_install_dir }}"
    when: "'nodejs' in (asdf_plugins | map(attribute='name') | list)"
    changed_when: false
    tags: [verify, nodejs]
  
  - name: "[FuncTest] Display nodejs version"
    ansible.builtin.debug:
      msg: "Node.js version: {{ nodejs_test.stdout }}"
    when: nodejs_test is not skipped
    tags: [verify, nodejs]
  
  - name: "[FuncTest] Test python functionality"
    ansible.builtin.command: "{{ asdf_install_dir }}/shims/python --version"
    register: python_test
    environment:
      ASDF_DIR: "{{ asdf_install_dir }}"
      ASDF_DATA_DIR: "{{ asdf_install_dir }}"
    when: "'python' in (asdf_plugins | map(attribute='name') | list)"
    changed_when: false
    tags: [verify, python]
  
  - name: "[FuncTest] Display python version"
    ansible.builtin.debug:
      msg: "Python version: {{ python_test.stdout }}"
    when: python_test is not skipped
    tags: [verify, python]
```

### User Access Validation

```yaml
  - name: "[UserTest] Test user access to asdf"
    ansible.builtin.command: "{{ asdf_install_dir }}/bin/asdf --version"
    become: true
    become_user: "{{ item }}"
    loop: "{{ asdf_users }}"
    register: user_asdf_test
    changed_when: false
    tags: [verify, users]
  
  - name: "[UserTest] Verify group membership"
    ansible.builtin.command: "groups {{ item }}"
    loop: "{{ asdf_users }}"
    register: group_check
    changed_when: false
    tags: [verify, users]
  
  - name: "[UserTest] Display group membership"
    ansible.builtin.debug:
      msg: "{{ item.stdout }}"
    loop: "{{ group_check.results }}"
    loop_control:
      label: "{{ item.item }}"
    tags: [verify, users]
```

---

## Complete Production Playbook

Here's the complete production playbook combining all sections:

```yaml
---
# =============================================================================
# ASDF PRODUCTION INSTALLATION
# =============================================================================
# This playbook installs and configures asdf with full validation.
#
# Features:
# - Time synchronization for reliable package installation
# - Pre-flight checks (connectivity, disk space, users)
# - Centralized plugin management
# - Comprehensive post-installation validation
#
# Usage:
#   ansible-playbook install-asdf-production.yml -i inventory.ini
#
# =============================================================================

- name: "ASDF Production Installation"
  hosts: all
  become: true
  gather_facts: true

  vars:
    # =========================================================================
    # BASIC CONFIGURATION
    # =========================================================================
    asdf_version: "latest"
    asdf_install_dir: "/opt/asdf"
    asdf_install_dependencies: true
    asdf_configure_shell: true
    asdf_shell_profile: "bashrc"

    # =========================================================================
    # USER CONFIGURATION
    # =========================================================================
    asdf_users:
      - "{{ ansible_user }}"

    # =========================================================================
    # PLUGIN CONFIGURATION
    # =========================================================================
    asdf_plugins:
      # Lightweight plugins
      - name: "direnv"
        versions: ["2.35.0"]
        global: "2.35.0"
      
      # Heavy plugins (optional - add as needed)
      # - name: "nodejs"
      #   versions: ["22.11.0"]
      #   global: "22.11.0"

  # ===========================================================================
  # PRE-TASKS
  # ===========================================================================
  pre_tasks:
    - name: "[TimeSync] Configure time synchronization"
      ansible.builtin.include_role:
        name: code3tech.devtools.asdf
        tasks_from: prereq
      tags: [prereq]
    
    - name: "[PreCheck] Verify internet connectivity"
      ansible.builtin.uri:
        url: "https://github.com"
        method: GET
        timeout: 10
      register: internet_check
      failed_when: internet_check.status != 200
      tags: [prereq]
    
    - name: "[UserCheck] Verify users exist"
      ansible.builtin.getent:
        database: passwd
        key: "{{ item }}"
      loop: "{{ asdf_users }}"
      tags: [prereq]

  # ===========================================================================
  # ROLE EXECUTION
  # ===========================================================================
  roles:
    - role: code3tech.devtools.asdf
      tags: [asdf]

  # ===========================================================================
  # POST-TASKS
  # ===========================================================================
  post_tasks:
    - name: "[Verify] Check asdf installation"
      ansible.builtin.command: "{{ asdf_install_dir }}/bin/asdf --version"
      register: asdf_version_result
      changed_when: false
      tags: [verify]
    
    - name: "[Verify] List installed plugins"
      ansible.builtin.command: "{{ asdf_install_dir }}/bin/asdf plugin list"
      register: plugins_result
      environment:
        ASDF_DIR: "{{ asdf_install_dir }}"
        ASDF_DATA_DIR: "{{ asdf_install_dir }}"
      changed_when: false
      tags: [verify]
    
    - name: "[Summary] Installation complete"
      ansible.builtin.debug:
        msg: |
          ═══════════════════════════════════════════════════════════════
          ASDF INSTALLATION COMPLETE
          ═══════════════════════════════════════════════════════════════
          
          asdf Version: {{ asdf_version_result.stdout }}
          Install Dir:  {{ asdf_install_dir }}
          
          Installed Plugins:
          {{ plugins_result.stdout | default('None') }}
          
          Configured Users: {{ asdf_users | join(', ') }}
          
          ═══════════════════════════════════════════════════════════════
      tags: [verify]
```

---

## CI/CD Integration

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    
    environment {
        ANSIBLE_HOST_KEY_CHECKING = 'False'
    }
    
    stages {
        stage('Install asdf') {
            steps {
                ansiblePlaybook(
                    playbook: 'install-asdf-production.yml',
                    inventory: 'inventory.ini',
                    credentialsId: 'ssh-key',
                    extras: '-e "asdf_users=[jenkins]"'
                )
            }
        }
        
        stage('Verify') {
            steps {
                sh '''
                    source ~/.bashrc
                    asdf --version
                    node --version || true
                    python --version || true
                '''
            }
        }
    }
}
```

### GitHub Actions Workflow

```yaml
name: Deploy asdf

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Ansible
        run: pip install ansible
      
      - name: Install Collection
        run: ansible-galaxy collection install code3tech.devtools
      
      - name: Deploy asdf
        run: |
          ansible-playbook install-asdf-production.yml \
            -i inventory.ini \
            -e "asdf_users=[runner]"
        env:
          ANSIBLE_HOST_KEY_CHECKING: 'false'
```

### GitLab CI Pipeline

```yaml
deploy_asdf:
  stage: deploy
  image: cytopia/ansible:latest
  
  before_script:
    - ansible-galaxy collection install code3tech.devtools
  
  script:
    - ansible-playbook install-asdf-production.yml
        -i inventory.ini
        -e "asdf_users=[gitlab-runner]"
  
  environment:
    name: production
```

---

## Deployment Scenarios

### Development Workstations

```yaml
asdf_plugins:
  - name: "nodejs"
    versions: ["22.11.0", "20.18.0"]
    global: "22.11.0"
  - name: "python"
    versions: ["3.13.0", "3.12.7"]
    global: "3.13.0"
  - name: "direnv"
    versions: ["2.35.0"]
    global: "2.35.0"

asdf_shell_profile: "zshrc"  # Developers use zsh
```

### CI/CD Servers

```yaml
asdf_plugins:
  - name: "nodejs"
    versions: ["22.11.0"]
    global: "22.11.0"
  - name: "python"
    versions: ["3.13.0"]
    global: "3.13.0"
  - name: "terraform"
    versions: ["1.9.0"]
    global: "1.9.0"
  - name: "kubectl"
    versions: ["1.31.0"]
    global: "1.31.0"

asdf_shell_profile: "bashrc"  # CI uses bash
```

### DevOps Tooling Only

```yaml
asdf_plugins:
  - name: "direnv"
    versions: ["2.35.0"]
    global: "2.35.0"
  - name: "jq"
    versions: ["1.7.1"]
    global: "1.7.1"
  - name: "kubectl"
    versions: ["1.31.0"]
    global: "1.31.0"
  - name: "helm"
    versions: ["3.15.0"]
    global: "3.15.0"
  - name: "terraform"
    versions: ["1.9.0"]
    global: "1.9.0"
```

---

## Next Steps

- **[Performance & Security](07-performance-security.md)** - Optimization and best practices
- **[Troubleshooting](08-troubleshooting.md)** - Common issues and solutions

---

[← Back to asdf Documentation](README.md) | [Previous: Multi-User Configuration](05-multi-user-config.md) | [Next: Performance & Security →](07-performance-security.md)
