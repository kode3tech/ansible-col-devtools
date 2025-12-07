# Part 6: Production Deployment

This guide provides production-ready templates and best practices for deploying Azure DevOps agents at scale.

## 📋 Table of Contents

- [Production Architecture](#production-architecture)
- [Playbook Templates](#playbook-templates)
- [Inventory Patterns](#inventory-patterns)
- [Deployment Strategies](#deployment-strategies)
- [CI/CD Integration](#cicd-integration)
- [Validation and Testing](#validation-and-testing)
- [Next Steps](#next-steps)

## Production Architecture

### Multi-Environment Setup

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Production Agent Architecture                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Azure DevOps Organization                                                  │
│  ═════════════════════════                                                  │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │   Linux-Pool    │  │  Windows-Pool   │  │   GPU-Pool      │             │
│  │   (Org-level)   │  │   (Org-level)   │  │   (Org-level)   │             │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘             │
│           │                    │                    │                       │
│  ┌────────┴────────┐  ┌────────┴────────┐  ┌────────┴────────┐             │
│  │ build-agent-01  │  │ win-agent-01    │  │ gpu-agent-01    │             │
│  │ build-agent-02  │  │ win-agent-02    │  │                 │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│                                                                             │
│  Project: WebApplication                                                    │
│  ═══════════════════════                                                    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────┐           │
│  │ Environments (YAML Pipelines)                                │           │
│  ├──────────────┬──────────────┬──────────────┬────────────────┤           │
│  │ development  │   staging    │  production  │   dr-site      │           │
│  ├──────────────┼──────────────┼──────────────┼────────────────┤           │
│  │ dev-web-01   │ stg-web-01   │ prd-web-01   │ dr-web-01      │           │
│  │              │ stg-web-02   │ prd-web-02   │                │           │
│  │              │              │ prd-api-01   │                │           │
│  │              │              │ prd-api-02   │                │           │
│  └──────────────┴──────────────┴──────────────┴────────────────┘           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
azure-agents-production/
├── ansible.cfg
├── requirements.yml
├── Makefile
├── inventory/
│   ├── development/
│   │   ├── hosts.yml
│   │   └── group_vars/
│   │       ├── all.yml
│   │       └── vault.yml
│   ├── staging/
│   │   ├── hosts.yml
│   │   └── group_vars/
│   │       ├── all.yml
│   │       └── vault.yml
│   └── production/
│       ├── hosts.yml
│       └── group_vars/
│           ├── all.yml
│           └── vault.yml
├── playbooks/
│   ├── install-agents.yml
│   ├── remove-agents.yml
│   ├── update-tags.yml
│   └── health-check.yml
└── vars/
    └── common.yml
```

## Playbook Templates

### Production Install Playbook

```yaml
---
# playbooks/install-agents.yml
- name: Deploy Azure DevOps Agents - Production
  hosts: agent_servers
  become: true
  gather_facts: true

  vars_files:
    - ../vars/common.yml

  vars:
    # Azure DevOps Configuration
    azure_devops_agents_url: "https://dev.azure.com/{{ azure_org }}"
    azure_devops_agents_pat: "{{ vault_azure_devops_pat }}"

    # Agent Configuration
    azure_devops_agents_version: ""  # Empty = latest
    azure_devops_agents_base_path: "/opt/azure-devops-agents"
    azure_devops_agents_user: "azagent"
    azure_devops_agents_group: "azagent"

    # Service Configuration
    azure_devops_agents_run_as_service: true
    azure_devops_agents_service_enabled: true
    azure_devops_agents_service_state: started

    # Agent List (from inventory group_vars)
    azure_devops_agents_list: "{{ agent_config }}"

  pre_tasks:
    - name: Validate required variables
      ansible.builtin.assert:
        that:
          - azure_org is defined
          - vault_azure_devops_pat is defined
          - agent_config is defined
        fail_msg: "Required variables not defined"

    - name: Display deployment info
      ansible.builtin.debug:
        msg: |
          Deploying to: {{ inventory_hostname }}
          Organization: {{ azure_org }}
          Agents: {{ agent_config | map(attribute='name') | list }}

    - name: Validate time synchronization
      ansible.builtin.command: timedatectl status
      changed_when: false
      register: time_status

    - name: Ensure time is synchronized
      ansible.builtin.assert:
        that:
          - "'synchronized: yes' in time_status.stdout or 'System clock synchronized: yes' in time_status.stdout"
        fail_msg: "System time is not synchronized. Please configure NTP."

  roles:
    - code3tech.devtools.azure_devops_agents

  post_tasks:
    - name: Verify agent services are running
      ansible.builtin.systemd:
        name: "vsts.agent.{{ azure_org }}.{{ item.name }}"
        state: started
      loop: "{{ agent_config }}"
      when: item.state | default('present') == 'present'

    - name: Display deployment summary
      ansible.builtin.debug:
        msg: |
          ✅ Deployment Complete
          Host: {{ inventory_hostname }}
          Agents deployed: {{ agent_config | selectattr('state', 'undefined') | list | length + agent_config | selectattr('state', 'equalto', 'present') | list | length }}
```

### Health Check Playbook

```yaml
---
# playbooks/health-check.yml
- name: Azure DevOps Agents Health Check
  hosts: agent_servers
  become: true
  gather_facts: true

  vars_files:
    - ../vars/common.yml

  tasks:
    - name: Get all agent services
      ansible.builtin.shell: |
        set -o pipefail
        systemctl list-units 'vsts.agent.*' --no-legend | awk '{print $1}'
      register: agent_services
      changed_when: false

    - name: Check each service status
      ansible.builtin.systemd:
        name: "{{ item }}"
      loop: "{{ agent_services.stdout_lines }}"
      register: service_status
      when: agent_services.stdout_lines | length > 0

    - name: Display service status
      ansible.builtin.debug:
        msg: |
          {% for svc in service_status.results | default([]) %}
          {{ svc.item }}: {{ svc.status.ActiveState | default('unknown') }}
          {% endfor %}

    - name: Check disk usage
      ansible.builtin.shell: df -h {{ azure_devops_agents_base_path | default('/opt/azure-devops-agents') }}
      register: disk_usage
      changed_when: false

    - name: Display disk usage
      ansible.builtin.debug:
        var: disk_usage.stdout_lines

    - name: Test Azure DevOps connectivity
      ansible.builtin.uri:
        url: "https://dev.azure.com/{{ azure_org }}/_apis/projects?api-version=7.0"
        headers:
          Authorization: "Basic {{ ('' ~ ':' ~ vault_azure_devops_pat) | b64encode }}"
        status_code: 200
        timeout: 10
      register: api_test
      delegate_to: localhost
      run_once: true

    - name: Display API connectivity
      ansible.builtin.debug:
        msg: "✅ Azure DevOps API accessible - {{ api_test.json.count }} projects found"
      run_once: true
```

### Update Tags Playbook

```yaml
---
# playbooks/update-tags.yml
- name: Update Agent Tags
  hosts: agent_servers
  become: true

  vars_files:
    - ../vars/common.yml

  vars:
    azure_devops_agents_url: "https://dev.azure.com/{{ azure_org }}"
    azure_devops_agents_pat: "{{ vault_azure_devops_pat }}"

    # Enable tag updates
    azure_devops_agents_list: >-
      {{ agent_config | map('combine', {'update_tags': true}) | list }}

  roles:
    - code3tech.devtools.azure_devops_agents
```

## Inventory Patterns

### Environment-Based Inventory

```yaml
# inventory/production/hosts.yml
all:
  children:
    # Build Agents (Self-Hosted)
    build_servers:
      hosts:
        build01.prod.example.com:
        build02.prod.example.com:
      vars:
        agent_config:
          - name: "build-agent"
            type: "self-hosted"
            pool: "Linux-Production"
            tags:
              - "docker"
              - "nodejs"
              - "production"

    # Web Servers (Environment Agents)
    web_servers:
      hosts:
        web01.prod.example.com:
        web02.prod.example.com:
      vars:
        agent_config:
          - name: "web-agent"
            type: "environment"
            project: "WebApp"
            environment: "production"
            auto_create: false    # Pre-created with approvals
            open_access: false    # Explicit authorization
            tags:
              - "web"
              - "nginx"
              - "production"

    # API Servers (Environment Agents)
    api_servers:
      hosts:
        api01.prod.example.com:
        api02.prod.example.com:
      vars:
        agent_config:
          - name: "api-agent"
            type: "environment"
            project: "WebApp"
            environment: "production"
            auto_create: false
            open_access: false
            tags:
              - "api"
              - "dotnet"
              - "production"

    # All agent servers
    agent_servers:
      children:
        build_servers:
        web_servers:
        api_servers:
```

### Group Variables

```yaml
# inventory/production/group_vars/all.yml
---
# Azure DevOps Organization
azure_org: "myorganization"

# Agent Base Configuration
azure_devops_agents_base_path: "/opt/azure-devops-agents"
azure_devops_agents_user: "azagent"
azure_devops_agents_group: "azagent"

# Service Configuration
azure_devops_agents_run_as_service: true
azure_devops_agents_service_enabled: true
azure_devops_agents_service_state: started

# Common tags for all agents in this environment
common_tags:
  - "production"
  - "linux"
```

```yaml
# inventory/production/group_vars/vault.yml (encrypted)
---
vault_azure_devops_pat: "your-encrypted-pat-here"
```

### Dynamic Inventory with Tags

```yaml
# inventory/production/hosts.yml - Advanced pattern
all:
  vars:
    # Base tags applied to all agents
    base_tags:
      - "linux"
      - "{{ env_name }}"

  children:
    agent_servers:
      hosts:
        server01.prod.example.com:
          host_tags: ["zone-a", "primary"]
        server02.prod.example.com:
          host_tags: ["zone-b", "secondary"]
      vars:
        env_name: "production"
        agent_config:
          - name: "agent"
            type: "environment"
            project: "WebApp"
            environment: "{{ env_name }}"
            tags: "{{ base_tags + host_tags }}"
```

## Deployment Strategies

### Rolling Deployment

Deploy to hosts one at a time:

```bash
# Deploy with serial execution
ansible-playbook playbooks/install-agents.yml \
  -i inventory/production/hosts.yml \
  --ask-vault-pass \
  -e "serial=1"
```

Modify playbook for serial execution:

```yaml
---
- name: Deploy Agents (Rolling)
  hosts: agent_servers
  become: true
  serial: "{{ serial | default(omit) }}"  # Control via variable
  # ... rest of playbook
```

### Canary Deployment

Deploy to a subset first:

```bash
# Deploy to canary hosts first
ansible-playbook playbooks/install-agents.yml \
  -i inventory/production/hosts.yml \
  --limit "web01.prod.example.com" \
  --ask-vault-pass

# Verify, then deploy to all
ansible-playbook playbooks/install-agents.yml \
  -i inventory/production/hosts.yml \
  --ask-vault-pass
```

### Blue-Green Deployment

Use host groups for blue/green:

```yaml
# inventory/production/hosts.yml
all:
  children:
    blue_servers:
      hosts:
        blue-web01.prod.example.com:
        blue-web02.prod.example.com:

    green_servers:
      hosts:
        green-web01.prod.example.com:
        green-web02.prod.example.com:

    agent_servers:
      children:
        blue_servers:
        green_servers:
```

```bash
# Deploy to blue
ansible-playbook playbooks/install-agents.yml \
  -i inventory/production/hosts.yml \
  --limit "blue_servers" \
  --ask-vault-pass
```

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy-agents.yml
name: Deploy Azure DevOps Agents

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        type: choice
        options:
          - development
          - staging
          - production
      limit:
        description: 'Limit to specific hosts (optional)'
        required: false
        type: string

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ github.event.inputs.environment }}

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Ansible
        run: |
          pip install ansible
          ansible-galaxy collection install -r requirements.yml

      - name: Create vault password file
        run: echo "${{ secrets.VAULT_PASSWORD }}" > .vault_pass

      - name: Setup SSH key
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.SSH_PRIVATE_KEY }}" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa

      - name: Deploy agents
        run: |
          ansible-playbook playbooks/install-agents.yml \
            -i inventory/${{ github.event.inputs.environment }}/hosts.yml \
            --vault-password-file .vault_pass \
            ${{ github.event.inputs.limit && format('--limit {0}', github.event.inputs.limit) || '' }}

      - name: Cleanup
        if: always()
        run: |
          rm -f .vault_pass
          rm -f ~/.ssh/id_rsa
```

### Azure DevOps Pipeline

```yaml
# azure-pipelines.yml
trigger: none

parameters:
  - name: environment
    displayName: 'Target Environment'
    type: string
    default: 'development'
    values:
      - development
      - staging
      - production

  - name: limit
    displayName: 'Limit to hosts (optional)'
    type: string
    default: ''

variables:
  - group: ansible-secrets  # Variable group with vault password

stages:
  - stage: Deploy
    displayName: 'Deploy Agents to ${{ parameters.environment }}'
    jobs:
      - job: DeployAgents
        pool:
          vmImage: 'ubuntu-latest'
        steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '3.11'

          - script: |
              pip install ansible
              ansible-galaxy collection install -r requirements.yml
            displayName: 'Install Ansible'

          - script: |
              echo "$(VAULT_PASSWORD)" > .vault_pass
            displayName: 'Create vault password file'

          - task: InstallSSHKey@0
            inputs:
              knownHostsEntry: '$(KNOWN_HOSTS)'
              sshPublicKey: '$(SSH_PUBLIC_KEY)'
              sshKeySecureFile: 'ansible-ssh-key'

          - script: |
              ansible-playbook playbooks/install-agents.yml \
                -i inventory/${{ parameters.environment }}/hosts.yml \
                --vault-password-file .vault_pass \
                ${{ if ne(parameters.limit, '') }}--limit ${{ parameters.limit }}${{ endif }}
            displayName: 'Deploy Agents'

          - script: rm -f .vault_pass
            displayName: 'Cleanup'
            condition: always()
```

### Makefile for Convenience

```makefile
# Makefile
.PHONY: help install deploy-dev deploy-stg deploy-prod health lint

ANSIBLE_OPTS ?=
LIMIT ?=

help:
	@echo "Available targets:"
	@echo "  install      - Install Ansible dependencies"
	@echo "  deploy-dev   - Deploy to development"
	@echo "  deploy-stg   - Deploy to staging"
	@echo "  deploy-prod  - Deploy to production"
	@echo "  health       - Run health check on all environments"
	@echo "  lint         - Lint playbooks"

install:
	pip install -r requirements.txt
	ansible-galaxy collection install -r requirements.yml

deploy-dev:
	ansible-playbook playbooks/install-agents.yml \
		-i inventory/development/hosts.yml \
		--ask-vault-pass \
		$(if $(LIMIT),--limit $(LIMIT)) \
		$(ANSIBLE_OPTS)

deploy-stg:
	ansible-playbook playbooks/install-agents.yml \
		-i inventory/staging/hosts.yml \
		--ask-vault-pass \
		$(if $(LIMIT),--limit $(LIMIT)) \
		$(ANSIBLE_OPTS)

deploy-prod:
	ansible-playbook playbooks/install-agents.yml \
		-i inventory/production/hosts.yml \
		--ask-vault-pass \
		$(if $(LIMIT),--limit $(LIMIT)) \
		$(ANSIBLE_OPTS)

health:
	@for env in development staging production; do \
		echo "=== $$env ==="; \
		ansible-playbook playbooks/health-check.yml \
			-i inventory/$$env/hosts.yml \
			--ask-vault-pass; \
	done

lint:
	ansible-lint playbooks/
	yamllint playbooks/ inventory/
```

Usage:

```bash
# Deploy to development
make deploy-dev

# Deploy to production, specific host
make deploy-prod LIMIT="web01.prod.example.com"

# Deploy with extra options
make deploy-stg ANSIBLE_OPTS="--check --diff"
```

## Validation and Testing

### Pre-Deployment Validation

```yaml
# playbooks/validate.yml
---
- name: Pre-Deployment Validation
  hosts: agent_servers
  become: true
  gather_facts: true

  tasks:
    - name: Check OS compatibility
      ansible.builtin.assert:
        that:
          - ansible_os_family in ['Debian', 'RedHat']
          - ansible_distribution_major_version | int >= 9 or ansible_distribution in ['Ubuntu', 'Debian']
        fail_msg: "Unsupported OS: {{ ansible_distribution }} {{ ansible_distribution_version }}"

    - name: Check available disk space
      ansible.builtin.assert:
        that:
          - ansible_mounts | selectattr('mount', 'equalto', '/') | map(attribute='size_available') | first > 5368709120
        fail_msg: "Insufficient disk space (need 5GB+)"

    - name: Check network connectivity to Azure DevOps
      ansible.builtin.uri:
        url: "https://dev.azure.com/{{ azure_org }}"
        method: HEAD
        status_code: [200, 302, 401]
        timeout: 10
      delegate_to: localhost
      run_once: true
```

### Post-Deployment Validation

```yaml
# playbooks/verify.yml
---
- name: Post-Deployment Verification
  hosts: agent_servers
  become: true

  vars_files:
    - ../vars/common.yml

  tasks:
    - name: Verify all services are running
      ansible.builtin.systemd:
        name: "vsts.agent.{{ azure_org }}.{{ item.name }}"
        state: started
      loop: "{{ agent_config }}"
      register: service_check

    - name: Check agents in Azure DevOps
      ansible.builtin.uri:
        url: "https://dev.azure.com/{{ azure_org }}/_apis/distributedtask/pools?api-version=7.0"
        headers:
          Authorization: "Basic {{ ('' ~ ':' ~ vault_azure_devops_pat) | b64encode }}"
        status_code: 200
      delegate_to: localhost
      run_once: true
      register: pools

    - name: Display verification results
      ansible.builtin.debug:
        msg: |
          ✅ All services running
          ✅ Azure DevOps API accessible
          ✅ Found {{ pools.json.count }} agent pools
```

## Next Steps

Secure your deployment with security best practices:

➡️ **[Part 7: Security Best Practices](07-security.md)** - PAT protection, isolation, and network hardening.

---

## Quick Reference

### Documentation Map

```
... → 5. Advanced Features → [6. Production Deployment] → 7. Security → ...
```

### Common Commands

```bash
# Deploy to environment
ansible-playbook playbooks/install-agents.yml \
  -i inventory/production/hosts.yml \
  --ask-vault-pass

# Health check
ansible-playbook playbooks/health-check.yml \
  -i inventory/production/hosts.yml \
  --ask-vault-pass

# Dry run
ansible-playbook playbooks/install-agents.yml \
  -i inventory/production/hosts.yml \
  --ask-vault-pass \
  --check --diff
```

---

[← Previous: Advanced Features](05-advanced-features.md) | [Back to Guide Index](README.md) | [Next: Security →](07-security.md)
