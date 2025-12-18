# Common Patterns

Production-ready patterns for managing infrastructure with **code3tech.devtools** collection.

## 📋 Table of Contents

- [Multi-Environment Management](#multi-environment-management)
- [Ansible Vault for Secrets](#ansible-vault-for-secrets)
- [Using Tags](#using-tags)
- [Template-Based Configuration](#template-based-configuration)
- [Role Dependencies](#role-dependencies)
- [Conditional Execution](#conditional-execution)
- [Error Handling](#error-handling)
- [Performance Optimization](#performance-optimization)

---

## Multi-Environment Management

### Separate Inventory Files

**Structure:**
```
inventories/
├── production/
│   ├── hosts.yml
│   └── group_vars/
│       ├── all.yml
│       └── docker_hosts.yml
├── staging/
│   ├── hosts.yml
│   └── group_vars/
│       ├── all.yml
│       └── docker_hosts.yml
└── development/
    ├── hosts.yml
    └── group_vars/
        ├── all.yml
        └── docker_hosts.yml
```

**Production inventory** (`inventories/production/hosts.yml`):
```yaml
all:
  children:
    docker_hosts:
      hosts:
        prod-docker-01:
          ansible_host: 10.0.1.10
        prod-docker-02:
          ansible_host: 10.0.1.11
    
    ci_servers:
      hosts:
        prod-ci-01:
          ansible_host: 10.0.2.10
```

**Production variables** (`inventories/production/group_vars/all.yml`):
```yaml
---
environment: production

docker_daemon_config:
  log-driver: "json-file"
  log-opts:
    max-size: "10m"
    max-file: "5"          # More logs in production
  storage-driver: "overlay2"
  max-concurrent-downloads: 20  # Faster in production

github_actions_runners_list:
  - name: "prod-runner-01"
    labels:
      - "production"
      - "linux"
      - "docker"
```

**Staging variables** (`inventories/staging/group_vars/all.yml`):
```yaml
---
environment: staging

docker_daemon_config:
  log-driver: "json-file"
  log-opts:
    max-size: "10m"
    max-file: "3"          # Fewer logs in staging
  storage-driver: "overlay2"

github_actions_runners_list:
  - name: "staging-runner-01"
    labels:
      - "staging"
      - "linux"
```

**Usage:**
```bash
# Deploy to staging
ansible-playbook site.yml -i inventories/staging/hosts.yml

# Deploy to production
ansible-playbook site.yml -i inventories/production/hosts.yml

# Limit to specific group
ansible-playbook site.yml -i inventories/production/hosts.yml --limit ci_servers
```

---

## Ansible Vault for Secrets

### Creating Encrypted Files

**Create vault file:**
```bash
# Create new encrypted file
ansible-vault create secrets.yml

# Edit existing vault file
ansible-vault edit secrets.yml

# Change vault password
ansible-vault rekey secrets.yml
```

**Vault content** (`secrets.yml`):
```yaml
---
vault_github_pat: "ghp_xxxxxxxxxxxxxxxxxxxx"
vault_azure_pat: "xxxxxxxxxxxxxxxxxxxx"
vault_gitlab_api_token: "glpat-xxxxxxxxxxxxxxxxxxxx"

vault_docker_registry_password: "supersecret123"
vault_podman_quay_token: "qtoken456"
```

**Encrypt string:**
```bash
# Encrypt single value
ansible-vault encrypt_string 'supersecret123' --name 'vault_registry_password'
```

Output:
```yaml
vault_registry_password: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          66386439653964336164636264643065393134653333666664653264333836...
```

### Using Vault in Playbooks

**Playbook with vault:**
```yaml
---
- name: Deploy CI/CD infrastructure with secrets
  hosts: ci_servers
  become: true
  
  vars_files:
    - secrets.yml                    # Load encrypted variables
  
  vars:
    github_actions_runners_org: "your-org"
    github_actions_runners_pat: "{{ vault_github_pat }}"  # Use vault variable
    
    docker_registries_auth:
      - registry: "ghcr.io"
        username: "ciuser"
        password: "{{ vault_github_pat }}"
  
  roles:
    - code3tech.devtools.docker
    - code3tech.devtools.github_actions_runners
```

**Run with vault password:**
```bash
# Prompt for password
ansible-playbook site.yml --ask-vault-pass

# Use password file
echo "my-vault-password" > .vault_password
ansible-playbook site.yml --vault-password-file .vault_password

# Use environment variable
export ANSIBLE_VAULT_PASSWORD_FILE=~/.vault_pass
ansible-playbook site.yml
```

**Best practices:**
- ✅ Never commit `.vault_password` to git
- ✅ Use `.gitignore` to exclude vault password files
- ✅ Rotate vault passwords regularly
- ✅ Use separate vaults per environment
- ✅ Prefix vault variables with `vault_`

---

## Using Tags

### Tag Strategy

**Playbook with tags:**
```yaml
---
- name: Complete infrastructure setup
  hosts: all
  become: true
  
  roles:
    - role: code3tech.devtools.docker
      tags:
        - docker
        - containers
    
    - role: code3tech.devtools.podman
      tags:
        - podman
        - containers
    
    - role: code3tech.devtools.asdf
      tags:
        - asdf
        - development
    
    - role: code3tech.devtools.github_actions_runners
      tags:
        - github
        - cicd
        - runners
    
    - role: code3tech.devtools.azure_devops_agents
      tags:
        - azure
        - cicd
        - agents
```

**Usage:**
```bash
# Install only Docker
ansible-playbook site.yml --tags docker

# Install all container runtimes
ansible-playbook site.yml --tags containers

# Install all CI/CD tools
ansible-playbook site.yml --tags cicd

# Skip specific role
ansible-playbook site.yml --skip-tags azure

# Multiple tags
ansible-playbook site.yml --tags "docker,github"

# List available tags
ansible-playbook site.yml --list-tags
```

### Task-Level Tags

```yaml
---
- name: Configure Docker with granular control
  hosts: docker_hosts
  become: true
  
  roles:
    - code3tech.devtools.docker
  
  tasks:
    - name: Pull commonly used images
      community.docker.docker_image:
        name: "{{ item }}"
        source: pull
      loop:
        - nginx:latest
        - redis:latest
        - postgres:15
      tags:
        - docker
        - images
        - pull
    
    - name: Deploy application containers
      community.docker.docker_container:
        name: webapp
        image: myapp:latest
        state: started
        ports:
          - "80:8080"
      tags:
        - docker
        - containers
        - deploy
```

**Usage:**
```bash
# Only pull images
ansible-playbook site.yml --tags images

# Deploy without pulling
ansible-playbook site.yml --tags deploy --skip-tags pull
```

---

## Template-Based Configuration

### Jinja2 Templates

**Docker daemon config template** (`templates/docker-daemon.json.j2`):
```json
{
  "log-driver": "{{ docker_log_driver | default('json-file') }}",
  "log-opts": {
    "max-size": "{{ docker_log_max_size | default('10m') }}",
    "max-file": "{{ docker_log_max_file | default('3') }}"
  },
  "storage-driver": "overlay2",
  "max-concurrent-downloads": {{ docker_max_downloads | default(10) }},
  {% if environment == 'production' %}
  "live-restore": true,
  "userland-proxy": false
  {% endif %}
}
```

**Playbook using template:**
```yaml
---
- name: Configure Docker with template
  hosts: docker_hosts
  become: true
  
  vars:
    docker_log_driver: "json-file"
    docker_log_max_size: "{{ '20m' if environment == 'production' else '10m' }}"
    docker_log_max_file: "{{ 5 if environment == 'production' else 3 }}"
    docker_max_downloads: "{{ 20 if environment == 'production' else 10 }}"
  
  roles:
    - code3tech.devtools.docker
  
  tasks:
    - name: Deploy custom Docker daemon config
      ansible.builtin.template:
        src: templates/docker-daemon.json.j2
        dest: /etc/docker/daemon.json
        owner: root
        group: root
        mode: '0644'
      notify: restart docker
  
  handlers:
    - name: restart docker
      ansible.builtin.service:
        name: docker
        state: restarted
```

### Dynamic Configuration

**GitHub runner config with conditionals:**
```yaml
---
- name: Deploy GitHub runners based on environment
  hosts: ci_servers
  become: true
  
  vars:
    github_actions_runners_org: "your-org"
    github_actions_runners_pat: "{{ vault_github_pat }}"
    
    # Dynamic runner configuration
    github_actions_runners_list: "{{ runner_config[environment] }}"
    
    runner_config:
      production:
        - name: "prod-runner-01"
          labels: ["production", "linux", "docker", "high-memory"]
          runner_group: "Production"
        
        - name: "prod-runner-02"
          labels: ["production", "linux", "docker", "high-memory"]
          runner_group: "Production"
      
      staging:
        - name: "staging-runner-01"
          labels: ["staging", "linux", "docker"]
      
      development:
        - name: "dev-runner-01"
          labels: ["development", "linux"]
  
  roles:
    - code3tech.devtools.github_actions_runners
```

---

## Role Dependencies

### Defining Dependencies

**With Docker role (GitHub runner needs Docker):**
```yaml
---
- name: Deploy GitHub Actions runner with Docker
  hosts: ci_servers
  become: true
  
  vars_files:
    - secrets.yml
  
  pre_tasks:
    - name: Update apt cache
      ansible.builtin.apt:
        update_cache: true
        cache_valid_time: 3600
      when: ansible_os_family == "Debian"
  
  roles:
    # Install Docker first (dependency)
    - role: code3tech.devtools.docker
      vars:
        docker_users:
          - runner
    
    # Install asdf for Node.js (if needed)
    - role: code3tech.devtools.asdf
      vars:
        asdf_users:
          - runner
        asdf_plugins:
          - name: nodejs
            versions: ["20.10.0"]
            global: "20.10.0"
    
    # Install GitHub runner (depends on Docker + Node.js)
    - role: code3tech.devtools.github_actions_runners
      vars:
        github_actions_runners_org: "{{ vault_github_org }}"
        github_actions_runners_pat: "{{ vault_github_pat }}"
```

### Verification Tasks

```yaml
---
- name: Complete CI/CD setup with verification
  hosts: ci_servers
  become: true
  
  roles:
    - code3tech.devtools.docker
    - code3tech.devtools.github_actions_runners
  
  post_tasks:
    - name: Verify Docker is running
      ansible.builtin.service:
        name: docker
        state: started
      check_mode: true
      register: docker_status
      failed_when: docker_status is changed
    
    - name: Verify runner user is in docker group
      ansible.builtin.command:
        cmd: groups runner
      register: runner_groups
      changed_when: false
      failed_when: "'docker' not in runner_groups.stdout"
    
    - name: Test Docker access as runner user
      ansible.builtin.command:
        cmd: docker ps
      become: true
      become_user: runner
      changed_when: false
    
    - name: Verify GitHub runner service
      ansible.builtin.service:
        name: "actions.runner.{{ github_actions_runners_org }}.runner-01"
        state: started
      check_mode: true
      register: runner_status
      failed_when: runner_status is changed
```

---

## Conditional Execution

### Based on Environment

```yaml
---
- name: Environment-specific deployment
  hosts: all
  become: true
  
  vars:
    is_production: "{{ environment == 'production' }}"
    is_staging: "{{ environment == 'staging' }}"
  
  roles:
    - code3tech.devtools.docker
  
  tasks:
    - name: Enable production monitoring (production only)
      ansible.builtin.service:
        name: node_exporter
        enabled: true
        state: started
      when: is_production
    
    - name: Install debug tools (non-production only)
      ansible.builtin.apt:
        name:
          - strace
          - tcpdump
          - netcat
        state: present
      when: not is_production
    
    - name: Deploy production SSL certificates
      ansible.builtin.copy:
        src: "certs/{{ inventory_hostname }}.crt"
        dest: /etc/ssl/certs/
        mode: '0644'
      when:
        - is_production
        - ansible_os_family == "Debian"
```

### Based on Distribution

```yaml
---
- name: Cross-platform deployment
  hosts: all
  become: true
  
  vars:
    is_debian: "{{ ansible_os_family == 'Debian' }}"
    is_redhat: "{{ ansible_os_family == 'RedHat' }}"
  
  roles:
    - code3tech.devtools.docker
  
  tasks:
    - name: Install monitoring (Debian/Ubuntu)
      ansible.builtin.apt:
        name: prometheus-node-exporter
        state: present
      when: is_debian
    
    - name: Install monitoring (RHEL/Rocky)
      ansible.builtin.dnf:
        name: golang-github-prometheus-node-exporter
        state: present
      when: is_redhat
```

---

## Error Handling

### Graceful Failures

```yaml
---
- name: Deploy with error handling
  hosts: ci_servers
  become: true
  
  vars:
    continue_on_error: false
  
  tasks:
    - name: Try to pull Docker image
      community.docker.docker_image:
        name: myapp:latest
        source: pull
      register: pull_result
      ignore_errors: true
    
    - name: Build image if pull fails
      community.docker.docker_image:
        name: myapp:latest
        source: build
        build:
          path: /path/to/dockerfile
      when: pull_result is failed
    
    - name: Fail if both pull and build fail
      ansible.builtin.fail:
        msg: "Cannot obtain myapp:latest image"
      when:
        - pull_result is failed
        - build_result is failed
        - not continue_on_error
```

### Retry Logic

```yaml
---
- name: Deploy with retry logic
  hosts: ci_servers
  become: true
  
  tasks:
    - name: Pull Docker image with retries
      community.docker.docker_image:
        name: nginx:latest
        source: pull
      register: pull_result
      retries: 3
      delay: 5
      until: pull_result is succeeded
    
    - name: Start container with health check
      community.docker.docker_container:
        name: nginx
        image: nginx:latest
        state: started
        healthcheck:
          test: ["CMD", "curl", "-f", "http://localhost"]
          interval: 30s
          timeout: 10s
          retries: 3
```

### Rollback on Failure

```yaml
---
- name: Deploy with automatic rollback
  hosts: ci_servers
  become: true
  
  tasks:
    - name: Stop current container
      community.docker.docker_container:
        name: webapp
        state: stopped
      register: stop_result
    
    - name: Deploy new version
      community.docker.docker_container:
        name: webapp
        image: myapp:v2.0
        state: started
      register: deploy_result
  
  rescue:
    - name: Rollback to previous version
      community.docker.docker_container:
        name: webapp
        image: myapp:v1.0
        state: started
    
    - name: Send alert
      ansible.builtin.debug:
        msg: "Deployment failed! Rolled back to v1.0"
```

---

## Performance Optimization

### Parallel Execution

**Increase forks** (`ansible.cfg`):
```ini
[defaults]
forks = 20                          # Default is 5
```

**Use strategy:**
```yaml
---
- name: Fast deployment with parallel execution
  hosts: all
  become: true
  strategy: free                    # Don't wait for all hosts
  
  roles:
    - code3tech.devtools.docker
```

**Strategies:**
- `linear` (default): Wait for all hosts to complete each task
- `free`: Each host proceeds independently
- `host_pinned`: Reuse connections (faster for many tasks)

### Fact Caching

**Enable fact caching** (`ansible.cfg`):
```ini
[defaults]
gathering = smart                   # Only gather when needed
fact_caching = jsonfile
fact_caching_connection = /tmp/ansible_facts
fact_caching_timeout = 86400        # 24 hours
```

**Disable facts when not needed:**
```yaml
---
- name: Quick deployment without facts
  hosts: all
  become: true
  gather_facts: false               # Skip fact gathering
  
  roles:
    - code3tech.devtools.docker
```

### Connection Optimization

**Persistent connections** (`ansible.cfg`):
```ini
[defaults]
host_key_checking = False

[ssh_connection]
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
pipelining = True
control_path = /tmp/ansible-ssh-%%h-%%p-%%r
```

### Reduced Output

```yaml
---
- name: Silent deployment (faster)
  hosts: all
  become: true
  
  roles:
    - code3tech.devtools.docker
  
  tasks:
    - name: Pull multiple images
      community.docker.docker_image:
        name: "{{ item }}"
        source: pull
      loop:
        - nginx:latest
        - redis:latest
        - postgres:15
      no_log: true                  # Suppress output (faster)
```

---

## Complete Example: Production Playbook

```yaml
---
- name: Production CI/CD infrastructure deployment
  hosts: ci_servers
  become: true
  strategy: free
  
  vars_files:
    - "inventories/{{ environment }}/secrets.yml"
  
  vars:
    is_production: "{{ environment == 'production' }}"
  
  pre_tasks:
    - name: Update package cache
      ansible.builtin.apt:
        update_cache: true
        cache_valid_time: 3600
      when: ansible_os_family == "Debian"
      tags: always
  
  roles:
    # Install Docker
    - role: code3tech.devtools.docker
      vars:
        docker_users:
          - runner
          - deploy
        docker_daemon_config:
          log-driver: "json-file"
          log-opts:
            max-size: "{{ '20m' if is_production else '10m' }}"
            max-file: "{{ 5 if is_production else 3 }}"
      tags:
        - docker
        - containers
    
    # Install asdf for version management
    - role: code3tech.devtools.asdf
      vars:
        asdf_users:
          - runner
        asdf_plugins:
          - name: nodejs
            versions: ["20.10.0"]
            global: "20.10.0"
      tags:
        - asdf
        - development
    
    # Install GitHub Actions runner
    - role: code3tech.devtools.github_actions_runners
      vars:
        github_actions_runners_org: "{{ vault_github_org }}"
        github_actions_runners_pat: "{{ vault_github_pat }}"
        github_actions_runners_list:
          - name: "{{ inventory_hostname }}-runner-01"
            labels:
              - "{{ environment }}"
              - "linux"
              - "docker"
      tags:
        - github
        - cicd
  
  post_tasks:
    - name: Verify all services are running
      ansible.builtin.service:
        name: "{{ item }}"
        state: started
      check_mode: true
      loop:
        - docker
        - "actions.runner.{{ vault_github_org }}.{{ inventory_hostname }}-runner-01"
      tags: verify
    
    - name: Send deployment notification
      ansible.builtin.debug:
        msg: "Deployment to {{ environment }} completed successfully!"
      tags: always
```

**Run this playbook:**
```bash
# Staging deployment
ansible-playbook site.yml \
  -i inventories/staging/hosts.yml \
  -e environment=staging \
  --ask-vault-pass

# Production deployment (Docker only)
ansible-playbook site.yml \
  -i inventories/production/hosts.yml \
  -e environment=production \
  --tags docker \
  --ask-vault-pass

# Production deployment (full, with verification)
ansible-playbook site.yml \
  -i inventories/production/hosts.yml \
  -e environment=production \
  --ask-vault-pass \
  -v
```

---

## Best Practices Summary

✅ **Multi-Environment:**
- Separate inventories per environment
- Use `group_vars/` for environment-specific configuration
- Never mix environment credentials

✅ **Secrets:**
- Always use Ansible Vault for credentials
- Prefix vault variables with `vault_`
- Rotate vault passwords regularly
- Use `.gitignore` for password files

✅ **Tags:**
- Tag all roles and important tasks
- Use hierarchical tags (e.g., `cicd` > `github`, `azure`)
- Document available tags in README

✅ **Templates:**
- Use templates for complex configuration
- Leverage Jinja2 conditionals for environment-specific config
- Keep templates readable and commented

✅ **Error Handling:**
- Use `ignore_errors` sparingly
- Implement retry logic for network operations
- Add rollback tasks in `rescue` blocks
- Verify deployments in `post_tasks`

✅ **Performance:**
- Enable fact caching
- Increase `forks` for large inventories
- Use `strategy: free` when order doesn't matter
- Disable fact gathering when not needed

---

## Next Steps

✅ **Mastered common patterns!** Final step:

1. **[Troubleshooting](06-troubleshooting.md)** - Fix common execution issues

Or dive deeper:
- **[User Guides](../user-guides/)** - Role-specific advanced topics
- **[Variables Reference](../reference/VARIABLES.md)** - Complete variable documentation

---

[← Back: Using Roles](04-using-roles.md) | [Next: Troubleshooting →](06-troubleshooting.md)
