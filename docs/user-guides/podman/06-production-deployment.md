# Production Deployment

Complete guide for deploying Podman in production with pre/post tasks, validation, and best practices.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Pre-Deployment Tasks](#pre-deployment-tasks)
- [Production Playbook](#production-playbook)
- [Post-Deployment Validation](#post-deployment-validation)
- [Multi-Environment Setup](#multi-environment-setup)
- [LXC Container Support](#lxc-container-support)
- [Rollback Procedures](#rollback-procedures)

---

## Overview

Production Podman deployments require:

- ✅ System preparation (time sync, kernel modules)
- ✅ Optimized storage configuration
- ✅ Registry authentication
- ✅ Rootless user setup
- ✅ Comprehensive validation
- ✅ Monitoring integration

---

## Pre-Deployment Tasks

### Time Synchronization

Critical for GPG key validation:

```yaml
pre_tasks:
  # RHEL/Rocky/AlmaLinux
  - name: Ensure chrony is installed (RedHat)
    ansible.builtin.dnf:
      name: chrony
      state: present
    when: ansible_os_family == 'RedHat'
  
  - name: Enable chrony
    ansible.builtin.service:
      name: chronyd
      state: started
      enabled: true
    when: ansible_os_family == 'RedHat'
  
  - name: Force time synchronization
    ansible.builtin.command: chronyc makestep
    changed_when: false
    when: ansible_os_family == 'RedHat'
  
  # Ubuntu/Debian
  - name: Ensure systemd-timesyncd is installed (Debian)
    ansible.builtin.apt:
      name: systemd-timesyncd
      state: present
      update_cache: true
    when: ansible_os_family == 'Debian'
  
  - name: Enable timesyncd
    ansible.builtin.service:
      name: systemd-timesyncd
      state: started
      enabled: true
    when: ansible_os_family == 'Debian'
```

### Create Rootless Users

```yaml
pre_tasks:
  - name: Create rootless users
    ansible.builtin.user:
      name: "{{ item }}"
      shell: /bin/bash
      create_home: true
    loop: "{{ podman_rootless_users }}"
  
  - name: Enable user lingering for persistent sessions
    ansible.builtin.command: loginctl enable-linger {{ item }}
    loop: "{{ podman_rootless_users }}"
    changed_when: false
```

### Custom Storage Directory

```yaml
pre_tasks:
  - name: Create Podman data directory
    ansible.builtin.file:
      path: /opt/podman-data
      state: directory
      mode: '0711'
      owner: root
      group: root
```

### Kernel Modules

```yaml
pre_tasks:
  - name: Load required kernel modules
    community.general.modprobe:
      name: "{{ item }}"
      state: present
    loop:
      - overlay
      - br_netfilter
  
  - name: Persist kernel modules
    ansible.builtin.lineinfile:
      path: /etc/modules-load.d/podman.conf
      line: "{{ item }}"
      create: true
      mode: '0644'
    loop:
      - overlay
      - br_netfilter
```

---

## Production Playbook

### Complete Example

```yaml
---
- name: Production Podman Deployment
  hosts: podman_hosts
  become: true
  
  vars_files:
    - vars/secrets.yml
  
  vars:
    # Test user for validation
    podman_test_user: "podman-test"
    
    # Rootless configuration
    podman_enable_rootless: true
    podman_rootless_users:
      - "{{ ansible_user }}"
      - "{{ podman_test_user }}"
      - jenkins
      - deployer
    
    # Performance-optimized storage
    podman_storage_conf:
      storage:
        driver: "overlay"
        graphroot: "/opt/podman-data/storage"
        runroot: "/run/containers/storage"
        options:
          overlay:
            mountopt: "nodev,metacopy=on"
      engine:
        runtime: "crun"
        events_logger: "file"
        cgroup_manager: "systemd"
        num_locks: 2048
        image_parallel_copies: 10
    
    # Registry search order
    podman_registries_conf:
      unqualified-search-registries:
        - docker.io
        - quay.io
        - ghcr.io
    
    # Registry authentication
    podman_registries_auth:
      - registry: "docker.io"
        username: "{{ dockerhub_username }}"
        password: "{{ vault_dockerhub_token }}"
      - registry: "ghcr.io"
        username: "{{ github_username }}"
        password: "{{ vault_github_token }}"
      - registry: "registry.company.com"
        username: "ci-service"
        password: "{{ vault_company_token }}"
  
  pre_tasks:
    # Time sync
    - name: Ensure chrony is installed (RedHat)
      ansible.builtin.dnf:
        name: chrony
        state: present
      when: ansible_os_family == 'RedHat'
    
    - name: Force time sync
      ansible.builtin.command: chronyc makestep
      changed_when: false
      when: ansible_os_family == 'RedHat'
    
    # Create test user
    - name: Create test user (no privileges)
      ansible.builtin.user:
        name: "{{ podman_test_user }}"
        shell: /bin/bash
        create_home: true
    
    - name: Remove test user from privileged groups
      ansible.builtin.user:
        name: "{{ podman_test_user }}"
        groups: []
        append: false
    
    # Custom storage directory
    - name: Create Podman storage directory
      ansible.builtin.file:
        path: /opt/podman-data
        state: directory
        mode: '0711'
    
    # Enable lingering
    - name: Enable user lingering
      ansible.builtin.command: loginctl enable-linger {{ item }}
      loop: "{{ podman_rootless_users }}"
      changed_when: false
      ignore_errors: true
  
  roles:
    - code3tech.devtools.podman
  
  post_tasks:
    # Basic verification
    - name: Verify Podman installation
      ansible.builtin.command: podman --version
      register: podman_version
      changed_when: false
    
    - name: Display Podman version
      ansible.builtin.debug:
        msg: "Podman {{ podman_version.stdout }}"
    
    # Get system info
    - name: Get Podman info
      ansible.builtin.command: podman info --format json
      register: podman_info_raw
      changed_when: false
    
    - name: Parse Podman info
      ansible.builtin.set_fact:
        podman_info: "{{ podman_info_raw.stdout | from_json }}"
    
    - name: Display configuration
      ansible.builtin.debug:
        msg: |
          ═══════════════════════════════════════
          ✅ Podman Configuration Summary
          ═══════════════════════════════════════
          Version: {{ podman_info.version.Version }}
          Runtime: {{ podman_info.host.ociRuntime.name }}
          Storage: {{ podman_info.store.graphDriverName }}
          Graph Root: {{ podman_info.store.graphRoot }}
          ═══════════════════════════════════════
    
    # Test rootless functionality
    - name: Get test user UID
      ansible.builtin.command: id -u {{ podman_test_user }}
      register: test_uid
      changed_when: false
    
    - name: Ensure XDG_RUNTIME_DIR for test user
      ansible.builtin.file:
        path: "/run/user/{{ test_uid.stdout }}"
        state: directory
        owner: "{{ podman_test_user }}"
        group: "{{ podman_test_user }}"
        mode: '0700'
    
    - name: Pull test image (rootless)
      ansible.builtin.command: podman pull docker.io/library/alpine:latest
      become: true
      become_user: "{{ podman_test_user }}"
      environment:
        XDG_RUNTIME_DIR: "/run/user/{{ test_uid.stdout }}"
      register: pull_result
      changed_when: "'already present' not in pull_result.stderr"
    
    - name: Run test container (rootless)
      ansible.builtin.command: >
        podman run --rm docker.io/library/alpine:latest
        echo "Container test SUCCESS"
      become: true
      become_user: "{{ podman_test_user }}"
      environment:
        XDG_RUNTIME_DIR: "/run/user/{{ test_uid.stdout }}"
      register: container_test
    
    - name: Display test result
      ansible.builtin.debug:
        msg: "{{ container_test.stdout }}"
    
    # Final summary
    - name: Deployment summary
      ansible.builtin.debug:
        msg: |
          ═══════════════════════════════════════
          ✅ Podman Production Deployment Complete
          ═══════════════════════════════════════
          • Podman version: {{ podman_info.version.Version }}
          • Runtime: {{ podman_info.host.ociRuntime.name }}
          • Storage driver: {{ podman_info.store.graphDriverName }}
          • Rootless users: {{ podman_rootless_users | join(', ') }}
          • Registries configured: {{ podman_registries_auth | length }}
          • Container test: PASSED ✅
          ═══════════════════════════════════════
```

---

## Post-Deployment Validation

### Automated Validation Playbook

```yaml
---
- name: Validate Podman Deployment
  hosts: podman_hosts
  become: true
  
  tasks:
    - name: Check Podman version
      ansible.builtin.command: podman --version
      register: version
      changed_when: false
    
    - name: Check runtime
      ansible.builtin.command: podman info --format '{{ "{{" }}.Host.OCIRuntime.Name{{ "}}" }}'
      register: runtime
      changed_when: false
    
    - name: Check storage driver
      ansible.builtin.command: podman info --format '{{ "{{" }}.Store.GraphDriverName{{ "}}" }}'
      register: storage
      changed_when: false
    
    - name: Test container execution
      ansible.builtin.command: podman run --rm alpine echo "OK"
      register: container_test
      changed_when: false
    
    - name: Display validation results
      ansible.builtin.debug:
        msg: |
          Podman Version: {{ version.stdout }}
          Runtime: {{ runtime.stdout }}
          Storage: {{ storage.stdout }}
          Container Test: {{ container_test.stdout }}
```

### Manual Validation Commands

```bash
# Version
podman --version

# System info
podman info

# Runtime check
podman info | grep -i runtime

# Storage check
podman info | grep -i driver

# Rootless check
podman info | grep rootless

# Test container
podman run --rm alpine echo "Works!"

# Check registries
podman info | grep -A5 registries

# Check authentication
cat ~/.config/containers/auth.json
```

---

## Multi-Environment Setup

### Inventory Structure

```ini
# inventory/production.ini
[podman_hosts]
prod-01.company.com
prod-02.company.com

[podman_hosts:vars]
env=production
```

```ini
# inventory/staging.ini
[podman_hosts]
staging-01.company.com

[podman_hosts:vars]
env=staging
```

### Environment-Specific Variables

```yaml
# group_vars/production.yml
podman_storage_conf:
  storage:
    driver: "overlay"
    graphroot: "/data/podman/storage"
    options:
      overlay:
        mountopt: "nodev,metacopy=on"
  engine:
    runtime: "crun"
    image_parallel_copies: 20
```

```yaml
# group_vars/staging.yml
podman_storage_conf:
  storage:
    driver: "overlay"
  engine:
    runtime: "crun"
    image_parallel_copies: 5
```

### Multi-Environment Playbook

```yaml
---
- name: Deploy Podman (Multi-Environment)
  hosts: podman_hosts
  become: true
  
  vars_files:
    - "vars/{{ env }}/secrets.yml"
    - "vars/{{ env }}/podman.yml"
  
  roles:
    - code3tech.devtools.podman
```

Run:
```bash
# Production
ansible-playbook deploy.yml -i inventory/production.ini

# Staging
ansible-playbook deploy.yml -i inventory/staging.ini
```

---

## LXC Container Support

Podman runs inside LXC containers with proper configuration.

### LXC Configuration

```
# /etc/pve/lxc/XXX.conf (Proxmox)
features: nesting=1
lxc.apparmor.profile: unconfined
```

### Podman Playbook for LXC

```yaml
---
- name: Podman in LXC Container
  hosts: lxc_containers
  become: true
  
  vars:
    podman_enable_rootless: true
    podman_rootless_users:
      - app
    
    podman_storage_conf:
      storage:
        driver: "overlay"
      engine:
        runtime: "crun"
        cgroup_manager: "cgroupfs"  # May be needed for LXC
  
  pre_tasks:
    - name: Check if running in LXC
      ansible.builtin.stat:
        path: /dev/lxc
      register: lxc_check
    
    - name: Display LXC status
      ansible.builtin.debug:
        msg: "Running inside LXC container"
      when: lxc_check.stat.exists
  
  roles:
    - code3tech.devtools.podman
```

---

## Rollback Procedures

### Pre-Deployment Backup

```yaml
pre_tasks:
  - name: Backup registries config
    ansible.builtin.copy:
      src: /etc/containers/registries.conf
      dest: /etc/containers/registries.conf.bak
      remote_src: true
    ignore_errors: true
  
  - name: Backup storage config
    ansible.builtin.copy:
      src: /etc/containers/storage.conf
      dest: /etc/containers/storage.conf.bak
      remote_src: true
    ignore_errors: true
```

### Rollback Playbook

```yaml
---
- name: Rollback Podman Configuration
  hosts: podman_hosts
  become: true
  
  tasks:
    - name: Stop all containers
      ansible.builtin.command: podman stop --all
      ignore_errors: true
    
    - name: Restore registries config
      ansible.builtin.copy:
        src: /etc/containers/registries.conf.bak
        dest: /etc/containers/registries.conf
        remote_src: true
    
    - name: Restore storage config
      ansible.builtin.copy:
        src: /etc/containers/storage.conf.bak
        dest: /etc/containers/storage.conf
        remote_src: true
    
    - name: Verify Podman
      ansible.builtin.command: podman info
      register: verify
      changed_when: false
    
    - name: Rollback complete
      ansible.builtin.debug:
        msg: "Rollback completed successfully"
      when: verify is success
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] System requirements verified
- [ ] Disk space checked
- [ ] Time synchronization configured
- [ ] Registry credentials in Vault
- [ ] Rootless users created
- [ ] Configuration backed up

### Deployment

- [ ] Role executed successfully
- [ ] No errors in output
- [ ] Storage configured
- [ ] Registries configured
- [ ] Users configured

### Post-Deployment

- [ ] Podman version correct
- [ ] Runtime is crun
- [ ] Storage driver is overlay
- [ ] Test container runs
- [ ] Rootless works for each user
- [ ] Registry auth works

---

## Next Steps

- **[Performance & Security](07-performance-security.md)** - Optimization
- **[Troubleshooting](08-troubleshooting.md)** - Common issues

---

[← Back to Podman Documentation](README.md) | [Previous: Rootless Config](05-rootless-config.md) | [Next: Performance & Security →](07-performance-security.md)
