# Production Deployment

Complete guide for deploying Docker in production environments with best practices, pre/post tasks, and validation.

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

Production Docker deployments require:

- ✅ Pre-deployment validation
- ✅ Optimized daemon configuration
- ✅ Registry authentication
- ✅ Post-deployment verification
- ✅ Monitoring integration
- ✅ Rollback procedures

---

## Pre-Deployment Tasks

### System Preparation

```yaml
pre_tasks:
  # Ensure system is updated
  - name: Update apt cache
    ansible.builtin.apt:
      update_cache: true
      cache_valid_time: 3600
    when: ansible_os_family == "Debian"
  
  # Check disk space
  - name: Check available disk space
    ansible.builtin.shell: |
      df -h {{ docker_data_root | default('/var/lib/docker') }} | tail -1 | awk '{print $5}' | tr -d '%'
    register: disk_usage
    changed_when: false
  
  - name: Fail if disk usage is too high
    ansible.builtin.fail:
      msg: "Disk usage is {{ disk_usage.stdout }}%. Must be below 80%."
    when: disk_usage.stdout | int > 80
```

### Time Synchronization

```yaml
pre_tasks:
  - name: Install chrony for time sync
    ansible.builtin.package:
      name: chrony
      state: present
  
  - name: Ensure chrony is running
    ansible.builtin.service:
      name: chronyd
      state: started
      enabled: true
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
      path: /etc/modules-load.d/docker.conf
      line: "{{ item }}"
      create: true
      mode: '0644'
    loop:
      - overlay
      - br_netfilter
```

### Kernel Parameters

```yaml
pre_tasks:
  - name: Set kernel parameters for Docker
    ansible.posix.sysctl:
      name: "{{ item.name }}"
      value: "{{ item.value }}"
      sysctl_file: /etc/sysctl.d/99-docker.conf
      reload: true
    loop:
      - { name: 'net.bridge.bridge-nf-call-iptables', value: '1' }
      - { name: 'net.bridge.bridge-nf-call-ip6tables', value: '1' }
      - { name: 'net.ipv4.ip_forward', value: '1' }
```

---

## Production Playbook

### Complete Example

```yaml
---
- name: Production Docker Deployment
  hosts: docker_hosts
  become: true
  
  vars_files:
    - vars/secrets.yml
  
  vars:
    # Docker configuration
    docker_users:
      - deploy
      - jenkins
    
    # Daemon configuration
    docker_daemon_config:
      # Logging - Production optimized
      log-driver: "json-file"
      log-opts:
        max-size: "50m"
        max-file: "5"
        compress: "true"
        mode: "non-blocking"
        max-buffer-size: "4m"
      
      # Storage - SSD optimized
      storage-driver: "overlay2"
      data-root: "/data/docker"
      
      # Network - Performance
      userland-proxy: false
      iptables: true
      dns:
        - "10.0.0.2"
        - "8.8.8.8"
      
      # Concurrency
      max-concurrent-downloads: 10
      max-concurrent-uploads: 5
      
      # Reliability
      live-restore: true
      
      # Resource Limits
      default-ulimits:
        nofile:
          Hard: 65535
          Soft: 65535
      default-shm-size: "128M"
      
      # Monitoring
      metrics-addr: "0.0.0.0:9323"
      experimental: true
    
    # Registry authentication
    docker_registries_auth:
      - registry: "https://index.docker.io/v1/"
        username: "{{ dockerhub_username }}"
        password: "{{ vault_dockerhub_token }}"
      - registry: "ghcr.io"
        username: "{{ github_username }}"
        password: "{{ vault_github_token }}"
  
  pre_tasks:
    # System checks
    - name: Update package cache
      ansible.builtin.apt:
        update_cache: true
        cache_valid_time: 3600
      when: ansible_os_family == "Debian"
    
    # Disk space check
    - name: Get disk usage
      ansible.builtin.shell: |
        df {{ docker_daemon_config['data-root'] | default('/var/lib/docker') }} 2>/dev/null | tail -1 | awk '{print $5}' | tr -d '%' || echo "0"
      register: disk_check
      changed_when: false
    
    - name: Warn if disk usage high
      ansible.builtin.debug:
        msg: "⚠️ Disk usage is {{ disk_check.stdout }}%. Consider cleanup."
      when: disk_check.stdout | int > 70
    
    # Custom data directory
    - name: Create Docker data directory
      ansible.builtin.file:
        path: "{{ docker_daemon_config['data-root'] }}"
        state: directory
        mode: '0711'
      when: docker_daemon_config['data-root'] is defined
    
    # Kernel modules
    - name: Load overlay module
      community.general.modprobe:
        name: overlay
        state: present
  
  roles:
    - code3tech.devtools.docker
  
  post_tasks:
    # Service verification
    - name: Verify Docker service
      ansible.builtin.service_facts:
    
    - name: Assert Docker is running
      ansible.builtin.assert:
        that:
          - ansible_facts.services['docker.service'].state == 'running'
        fail_msg: "Docker service is not running!"
        success_msg: "✅ Docker service is running"
    
    # Docker functionality check
    - name: Test Docker functionality
      community.docker.docker_container:
        name: docker-test
        image: hello-world
        state: started
        auto_remove: true
        detach: false
      register: docker_test
    
    - name: Display test result
      ansible.builtin.debug:
        msg: "✅ Docker test container ran successfully"
      when: docker_test is success
    
    # User verification
    - name: Verify users in docker group
      ansible.builtin.command: "id -nG {{ item }}"
      loop: "{{ docker_users }}"
      register: user_groups
      changed_when: false
    
    - name: Display user group membership
      ansible.builtin.debug:
        msg: "✅ {{ item.item }}: {{ item.stdout }}"
      loop: "{{ user_groups.results }}"
      when: "'docker' in item.stdout"
    
    # Metrics verification
    - name: Check Prometheus metrics endpoint
      ansible.builtin.uri:
        url: "http://localhost:9323/metrics"
        return_content: false
      register: metrics_check
      failed_when: false
      when: docker_daemon_config['metrics-addr'] is defined
    
    - name: Display metrics status
      ansible.builtin.debug:
        msg: "✅ Prometheus metrics available at :9323"
      when: 
        - docker_daemon_config['metrics-addr'] is defined
        - metrics_check.status == 200
```

---

## Post-Deployment Validation

### Automated Validation Playbook

```yaml
---
- name: Validate Docker Deployment
  hosts: docker_hosts
  become: true
  gather_facts: true
  
  tasks:
    - name: Gather Docker info
      community.docker.docker_host_info:
      register: docker_info
    
    - name: Display Docker version
      ansible.builtin.debug:
        msg: |
          Docker Version: {{ docker_info.host_info.ServerVersion }}
          Storage Driver: {{ docker_info.host_info.Driver }}
          Logging Driver: {{ docker_info.host_info.LoggingDriver }}
          Kernel: {{ docker_info.host_info.KernelVersion }}
    
    - name: Check Docker daemon config
      ansible.builtin.slurp:
        src: /etc/docker/daemon.json
      register: daemon_config
    
    - name: Display daemon configuration
      ansible.builtin.debug:
        msg: "{{ daemon_config.content | b64decode | from_json }}"
    
    - name: Test image pull
      community.docker.docker_image:
        name: alpine:latest
        source: pull
      register: pull_test
    
    - name: Test container run
      community.docker.docker_container:
        name: validate-test
        image: alpine:latest
        command: "echo 'Docker is working!'"
        state: started
        auto_remove: true
        detach: false
      register: run_test
    
    - name: Validation summary
      ansible.builtin.debug:
        msg: |
          ═══════════════════════════════════════
          ✅ Docker Deployment Validation Complete
          ═══════════════════════════════════════
          Version: {{ docker_info.host_info.ServerVersion }}
          Storage: {{ docker_info.host_info.Driver }}
          Images:  {{ docker_info.host_info.Images }}
          Containers: {{ docker_info.host_info.Containers }}
          ═══════════════════════════════════════
```

### Manual Validation Commands

```bash
# Service status
sudo systemctl status docker

# Docker info
docker info

# Test container
docker run --rm hello-world

# Check daemon config
cat /etc/docker/daemon.json | jq

# Check user groups
id -nG your-user

# Test registry auth
docker pull your-private-image

# Check metrics (if enabled)
curl -s http://localhost:9323/metrics | head -20
```

---

## Multi-Environment Setup

### Inventory Structure

```ini
# inventory/production.ini
[docker_hosts]
prod-docker-01.company.com
prod-docker-02.company.com
prod-docker-03.company.com

[docker_hosts:vars]
env=production
```

```ini
# inventory/staging.ini
[docker_hosts]
staging-docker-01.company.com

[docker_hosts:vars]
env=staging
```

### Environment-Specific Variables

```yaml
# group_vars/production.yml
docker_daemon_config:
  log-driver: "json-file"
  log-opts:
    max-size: "100m"
    max-file: "10"
  storage-driver: "overlay2"
  data-root: "/data/docker"
  userland-proxy: false
  live-restore: true
  max-concurrent-downloads: 10
  metrics-addr: "0.0.0.0:9323"
  experimental: true
```

```yaml
# group_vars/staging.yml
docker_daemon_config:
  log-driver: "json-file"
  log-opts:
    max-size: "10m"
    max-file: "3"
  storage-driver: "overlay2"
  max-concurrent-downloads: 5
```

### Playbook with Environment Support

```yaml
---
- name: Deploy Docker (Multi-Environment)
  hosts: docker_hosts
  become: true
  
  vars_files:
    - "vars/{{ env }}/secrets.yml"
    - "vars/{{ env }}/docker.yml"
  
  roles:
    - code3tech.devtools.docker
```

Run for specific environment:

```bash
# Production
ansible-playbook site.yml -i inventory/production.ini

# Staging
ansible-playbook site.yml -i inventory/staging.ini
```

---

## LXC Container Support

Docker can run inside LXC containers (Proxmox, LXD) with proper configuration.

### LXC Configuration

Add to your LXC container config:

```
# /etc/pve/lxc/XXX.conf (Proxmox)
features: nesting=1
lxc.apparmor.profile: unconfined
```

Or via Proxmox GUI:
1. Go to container → Options
2. Enable "Nesting"
3. Set AppArmor Profile to "unconfined"

### Ansible Playbook for LXC

```yaml
---
- name: Docker in LXC Container
  hosts: lxc_containers
  become: true
  
  vars:
    docker_daemon_config:
      log-driver: "json-file"
      log-opts:
        max-size: "10m"
        max-file: "3"
      storage-driver: "overlay2"
      # Important for LXC
      iptables: true
      userland-proxy: true  # May be required in LXC
  
  pre_tasks:
    - name: Check if running in LXC
      ansible.builtin.stat:
        path: /dev/lxc
      register: lxc_check
    
    - name: Display LXC status
      ansible.builtin.debug:
        msg: "Running in LXC container"
      when: lxc_check.stat.exists
  
  roles:
    - code3tech.devtools.docker
```

---

## Rollback Procedures

### Pre-Deployment Backup

```yaml
pre_tasks:
  - name: Backup current Docker config
    ansible.builtin.copy:
      src: /etc/docker/daemon.json
      dest: /etc/docker/daemon.json.bak
      remote_src: true
    ignore_errors: true
  
  - name: Record current Docker version
    ansible.builtin.shell: docker version --format '{{ "{{" }}.Server.Version{{ "}}" }}'
    register: docker_version_before
    changed_when: false
    ignore_errors: true
```

### Rollback Playbook

```yaml
---
- name: Rollback Docker Configuration
  hosts: docker_hosts
  become: true
  
  tasks:
    - name: Stop Docker service
      ansible.builtin.service:
        name: docker
        state: stopped
    
    - name: Restore previous configuration
      ansible.builtin.copy:
        src: /etc/docker/daemon.json.bak
        dest: /etc/docker/daemon.json
        remote_src: true
    
    - name: Start Docker service
      ansible.builtin.service:
        name: docker
        state: started
    
    - name: Verify Docker is running
      ansible.builtin.command: docker info
      register: docker_check
      changed_when: false
    
    - name: Display rollback result
      ansible.builtin.debug:
        msg: "✅ Docker rolled back successfully"
      when: docker_check is success
```

### Emergency Rollback Commands

```bash
# Stop Docker
sudo systemctl stop docker

# Restore config
sudo cp /etc/docker/daemon.json.bak /etc/docker/daemon.json

# Start Docker
sudo systemctl start docker

# Verify
docker info
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] System requirements verified
- [ ] Disk space checked (< 80% usage)
- [ ] Network connectivity verified
- [ ] Registry credentials in Ansible Vault
- [ ] Backup of existing configuration
- [ ] Time synchronization configured
- [ ] Kernel modules loaded

### Deployment

- [ ] Role executed successfully
- [ ] No errors in Ansible output
- [ ] Docker service started
- [ ] Users added to docker group

### Post-Deployment

- [ ] Docker service running
- [ ] Hello-world container runs
- [ ] Registry authentication works
- [ ] Prometheus metrics accessible
- [ ] Logging working correctly
- [ ] User permissions verified

---

## Next Steps

- **[Performance & Security](07-performance-security.md)** - Optimization techniques
- **[Troubleshooting](08-troubleshooting.md)** - Common issues and solutions

---

[← Back to Docker Documentation](README.md) | [Previous: Daemon Config](05-daemon-config.md) | [Next: Performance & Security →](07-performance-security.md)
