# Part 6: Production Deployment

## 📋 Table of Contents

- [Production Architecture Patterns](#production-architecture-patterns)
- [Multi-Runner Deployment](#multi-runner-deployment)
- [Performance Optimization](#performance-optimization)
- [High Availability Setup](#high-availability-setup)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Complete Production Example](#complete-production-example)

---

## Production Architecture Patterns

### Pattern 1: Single Host, Multiple Runners

```
┌─────────────────────────────────────────────────────────────────────────┐
│                 Production Server: ci-runner-01                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   backend-runner          frontend-runner        deploy-runner          │
│   ┌──────────────┐        ┌──────────────┐      ┌──────────────┐       │
│   │ Service:     │        │ Service:     │      │ Service:     │       │
│   │ gitlab-      │        │ gitlab-      │      │ gitlab-      │       │
│   │ runner-      │        │ runner-      │      │ runner-      │       │
│   │ backend      │        │ frontend     │      │ deploy       │       │
│   ├──────────────┤        ├──────────────┤      ├──────────────┤       │
│   │ Config:      │        │ Config:      │      │ Config:      │       │
│   │ /etc/gitlab- │        │ /etc/gitlab- │      │ /etc/gitlab- │       │
│   │ runner/      │        │ runner/      │      │ runner/      │       │
│   │ backend/     │        │ frontend/    │      │ deploy/      │       │
│   ├──────────────┤        ├──────────────┤      ├──────────────┤       │
│   │ Tags:        │        │ Tags:        │      │ Tags:        │       │
│   │ [docker,     │        │ [docker,     │      │ [shell,      │       │
│   │  backend,    │        │  frontend,   │      │  deploy,     │       │
│   │  linux]      │        │  nodejs,     │      │  production] │       │
│   │              │        │  linux]      │      │              │       │
│   └──────────────┘        └──────────────┘      └──────────────┘       │
│                                                                          │
│   ✅ Isolated configurations per runner                                 │
│   ✅ Independent service control                                        │
│   ✅ Different executors on same host                                   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Pattern 2: Load Balanced Runner Pool

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   Load Balanced Runner Architecture                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│                        GitLab (gitlab.com)                               │
│                        ────────────────────                              │
│                                 │                                        │
│                                 │ Jobs                                   │
│                                 ▼                                        │
│                  ┌──────────────────────────┐                           │
│                  │   Job Queue              │                           │
│                  │   tags: [docker, linux]  │                           │
│                  └──────────┬───────────────┘                           │
│                             │                                            │
│           ┌─────────────────┼─────────────────┐                         │
│           │                 │                 │                         │
│           ▼                 ▼                 ▼                         │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                │
│   │ Runner 01    │  │ Runner 02    │  │ Runner 03    │                │
│   │              │  │              │  │              │                │
│   │ Tags: docker │  │ Tags: docker │  │ Tags: docker │  Total:15      │
│   │       linux  │  │       linux  │  │       linux  │  jobs parallel  │
│   └──────────────┘  └──────────────┘  └──────────────┘                │
│                                                                          │
│   ✅ Automatic load distribution (gitlab_ci_runners_concurrent: 15)     │
│   ✅ High availability (runner failure tolerance)                       │
│   ✅ Horizontal scaling                                                 │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Note:** Concurrent setting is GLOBAL (not per-runner). Use `gitlab_ci_runners_concurrent: 15` to allow 15 total jobs across all 3 runners.

### Pattern 3: Environment-Based Segregation

```
Development         │  Staging           │  Production
──────────────────  │  ────────────────  │  ──────────────────
dev-runner-01       │  stage-runner-01   │  prod-runner-01
• not_protected     │  • not_protected   │  • ref_protected
• run_untagged:true │  • run_untagged:no │  • ref_protected
• unlocked          │  • unlocked        │  • locked
```

**Concurrency:** Set globally per host/environment:
- Development host: `gitlab_ci_runners_concurrent: 10`
- Staging host: `gitlab_ci_runners_concurrent: 5`
- Production host: `gitlab_ci_runners_concurrent: 1`

---

## Multi-Runner Deployment

### Complete Multi-Runner Playbook

```yaml
---
- name: Production Multi-Runner Deployment
  hosts: gitlab_runners
  become: true

  vars_files:
    - vars/gitlab_secrets.yml

  vars:
    gitlab_ci_runners_api_token: "{{ vault_gitlab_api_token }}"
    gitlab_ci_runners_gitlab_url: "https://gitlab.com"
    
    # Global settings
    gitlab_ci_runners_update_tags_via_api: true
    gitlab_ci_runners_auto_create_group: true
    gitlab_ci_runners_skip_verification: false
    
    # Global performance settings (apply to ALL runners on this host)
    gitlab_ci_runners_concurrent: 10  # Total concurrent jobs across all runners
    gitlab_ci_runners_request_concurrency: 2  # API request optimization
    
    # Multi-runner list
    gitlab_ci_runners_runners_list:
      # Backend runners (group: backend-team)
      - name: "backend-runner-01"
        api_runner_type: "group_type"
        api_group_full_path: "backend-team"
        description: "Backend team primary runner"
        tags:
          - docker
          - backend
          - linux
          - api
        executor: "shell"  # Note: docker executor requires manual config.toml edits
        access_level: "not_protected"
        run_untagged: false
      
      - name: "backend-runner-02"
        api_runner_type: "group_type"
        api_group_full_path: "backend-team"
        description: "Backend team secondary runner"
        tags:
          - docker
          - backend
          - linux
          - api
        executor: "shell"
        access_level: "not_protected"
        run_untagged: false
      
      # Frontend runners (group: frontend-team)
      - name: "frontend-runner-01"
        api_runner_type: "group_type"
        api_group_full_path: "frontend-team"
        description: "Frontend team primary runner"
        tags:
          - docker
          - frontend
          - linux
          - nodejs
          - react
        executor: "shell"
        access_level: "not_protected"
        run_untagged: false
      
      # Production deployment runner (instance)
      - name: "prod-deploy-runner"
        api_runner_type: "instance_type"
        description: "Production deployment runner (protected)"
        tags:
          - shell
          - production
          - deploy
          - linux
        executor: "shell"
        access_level: "ref_protected"  # Protected branches only
        locked: true
        run_untagged: false

  roles:
    - code3tech.devtools.gitlab_ci_runners

  # Post-deployment verification
  post_tasks:
    - name: Verify all runners are active
      ansible.builtin.systemd:
        name: "gitlab-runner@{{ item.name }}.service"
        state: started
        enabled: true
      loop: "{{ gitlab_ci_runners_runners_list }}"
      register: service_status
    
    - name: Display service status
      ansible.builtin.debug:
        msg: "✅ {{ item.item.name }}: {{ item.status.ActiveState }}"
      loop: "{{ service_status.results }}"
      when: item.status.ActiveState == "active"
```

---

## Performance Optimization

### Concurrency Tuning

```yaml
# Calculate optimal concurrency
# Formula: concurrent = (CPU cores * 2) for total host capacity
#
# Example: 8 CPU cores, 4 runners deployed
# gitlab_ci_runners_concurrent = 8 * 2 = 16 total jobs across all runners

# Global settings (apply to ALL runners on host)
gitlab_ci_runners_concurrent: 16  # Total concurrent jobs for host
gitlab_ci_runners_request_concurrency: 2  # API request optimization

gitlab_ci_runners_runners_list:
  - name: "runner-01"
    executor: "shell"
    tags: [linux, build]
  
  - name: "runner-02"
    executor: "shell"
    tags: [linux, test]
  
  # Note: All runners share the global concurrent limit (16 total)
```

### Docker Executor Configuration

⚠️ **Important**: The role currently supports `shell` executor out-of-the-box. For `docker` executor, you need to:

1. Register runner with `executor: "shell"` first
2. Manually edit `/opt/gitlab-ci-runners/{runner-name}/config.toml` to change executor and add Docker settings
3. Restart runner service: `systemctl restart gitlab-runner@{runner-name}`

**Manual config.toml example for Docker:**
```toml
[[runners]]
  name = "docker-runner-01"
  executor = "docker"
  [runners.docker]
    image = "alpine:latest"
    pull_policy = "if-not-present"
    volumes = ["/cache:/cache:rw", "/var/run/docker.sock:/var/run/docker.sock"]
    environment = ["DOCKER_DRIVER=overlay2", "DOCKER_TLS_CERTDIR=/certs"]
```

**Note**: Docker executor configuration via runner attributes will be supported in a future release.

### Cache Configuration

```toml
# In config.toml (managed by role)
[[runners]]
  [runners.cache]
    Type = "s3"
    Shared = true
    [runners.cache.s3]
      ServerAddress = "s3.amazonaws.com"
      BucketName = "gitlab-runner-cache"
      BucketLocation = "us-east-1"
```

---

## High Availability Setup

### Multi-Host Deployment

```yaml
---
- name: HA Multi-Host Deployment
  hosts: gitlab_runner_cluster
  become: true

  vars:# Global concurrent for each host (5 jobs per host)
        gitlab_ci_runners_concurrent: 5
        
        gitlab_ci_runners_runners_list:
          - name: "cluster-runner-{{ inventory_hostname }}"
            executor: "shell"
            tags:
              - linux
              - cluster
              - "host-{{ inventory_hostname }}"  # Host-specific tag.yml

  tasks:
    # Deploy same configuration to all hosts
    - name: Deploy runners to cluster
      ansible.builtin.include_role:
        name: code3tech.devtools.gitlab_ci_runners
      vars:
        gitlab_ci_runners_list:
          - name: "cluster-runner-{{ inventory_hostname }}"
            tags:
              - docker
              - linux
              - cluster
              - "host-{{ inventory_hostname }}"  # Host-specific tag
```

**Inventory:**
```ini
[gitlab_runner_cluster]
runner01.example.com
runner02.example.com
runner03.example.com
```

**Result:**
- 3 runners deployed (one per host)
- Same tags, auto load-balanced by GitLab
- If one host fails, others continue

---

## Monitoring and Maintenance

### Service Monitoring

```yaml
# Add to playbook for health checks
post_tasks:
  - name: Check runner service status
    ansible.builtin.systemd:
      name: "gitlab-runner@{{ item.name }}.service"
    register: runner_services
    loop: "{{ gitlab_ci_runners_runners_list }}"
  
  # Note: Runner tokens are not accessible after creation
  # Use systemd service status for verification instead
```

### Log Collection

```bash
# Collect logs from all runners
for runner in /etc/systemd/system/gitlab-runner@*.service; do
  name=$(basename "$runner" .service)
  echo "=== $name ==="
  journalctl -u "$name" --since "1 hour ago" --no-pager
done
```

### Metrics and Alerting

```yaml
# Prometheus metrics endpoint (global configuration)
gitlab_ci_runners_enable_metrics: true
gitlab_ci_runners_metrics_listen_address: ":9252"

gitlab_ci_runners_runners_list:
  - name: "monitored-runner"
    executor: "shell"
    tags: [linux]
```

**Note**: Metrics are configured globally for all runners on the host.

---

## Complete Production Example

### Infrastructure

```
Deployment:
├── 3 runner hosts (ci-runner-01, 02, 03)
├── 2 runners per host (6 total)
├── Load balanced by GitLab
└── Monitoring via systemd + logs

Groups:
├── backend-team (2 runners)
├── frontend-team (2 runners)
└── deploy-team (2 runners)
```

### Full Playbook

```yaml
---
- name: Production GitLab Runners Deployment
  hosts: gitlab_runner_cluster
  become: true
  gather_facts: true

  vars_files:
    - vars/gitlab_secrets.yml
    - vars/runner_config.yml

  vars:
    # Authentication
    gitlab_ci_runners_api_token: "{{ vault_gitlab_api_token }}"
    gitlab_ci_runners_gitlab_url: "https://gitlab.com"
    
    # Global settings
    gitlab_ci_runners_update_tags_via_api: true
    gitlab_ci_runners_auto_create_group: true
    gitlab_ci_runners_skip_verification: false
    gitlab_ci_runners_no_log: true
    
    # Performance (global for entire host)
    gitlab_ci_runners_concurrent: 10  # Total concurrent jobs for host
    gitlab_ci_runners_request_concurrency: 2
    
    # Runners per host
    gitlab_ci_runners_runners_list:
      - name: "backend-{{ inventory_hostname_short }}"
        api_runner_type: "group_type"
        api_group_full_path: "backend-team"
        description: "Backend runner on {{ inventory_hostname }}"
        tags:
          - backend
          - linux
          - "host-{{ inventory_hostname_short }}"
        executor: "shell"
        
      - name: "frontend-{{ inventory_hostname_short }}"
        api_runner_type: "group_type"
        api_group_full_path: "frontend-team"
        description: "Frontend runner on {{ inventory_hostname }}"
        tags:
          - frontend
          - linux
          - "host-{{ inventory_hostname_short }}"
        executor: "shell"

  pre_tasks:
    - name: Ensure Docker is installed
      ansible.builtin.package:
        name: docker.io
        state: present
    
    - name: Ensure Docker service is running
      ansible.builtin.systemd:
        name: docker
        state: started
        enabled: true

  roles:
    - code3tech.devtools.gitlab_ci_runners

  post_tasks:
    - name: Verify all runner services
      ansible.builtin.systemd:
        name: "gitlab-runner@{{ item.name }}.service"
        state: started
        enabled: true
      loop: "{{ gitlab_ci_runners_runners_list }}"
    
    - name: Create monitoring script
      ansible.builtin.copy:
        dest: /usr/local/bin/check-gitlab-runners.sh
        mode: '0755'
        content: |
          #!/bin/bash
          echo "=== GitLab Runner Status ==="
          systemctl list-units --type=service --state=running | grep 'gitlab-runner@'
          echo ""
          echo "=== Recent Errors ==="
          journalctl -u 'gitlab-runner@*' -p err --since "1 hour ago" --no-pager
    
    - name: Display deployment summary
      ansible.builtin.debug:
        msg: |
          ✅ Deployment Complete!
          
          Host: {{ inventory_hostname }}
          Runners: {{ gitlab_ci_runners_runners_list | length }}
          
          Services:
          {% for runner in gitlab_ci_runners_runners_list %}
          - gitlab-runner@{{ runner.name }}.service
          {% endfor %}
```

### Deployment

```bash
# Deploy to all hosts
ansible-playbook production-runners.yml \
  -i inventory/production \
  --vault-password-file ~/.ansible_vault_pass

# Verify deployment
ansible gitlab_runner_cluster \
  -i inventory/production \
  -m shell \
  -a "/usr/local/bin/check-gitlab-runners.sh"
```

---

## Next Steps

Your production runners are deployed! Continue to:

- **[Part 7: Security](07-security.md)** - Security best practices
- **[Part 8: Troubleshooting](08-troubleshooting.md)** - Common issues

---

[← Back to Guide Index](README.md)
