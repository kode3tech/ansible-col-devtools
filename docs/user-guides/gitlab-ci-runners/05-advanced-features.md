# Part 5: Advanced Features

## 📋 Table of Contents

- [Dynamic Tag Management via API](#dynamic-tag-management-via-api)
- [Runner Access Levels](#runner-access-levels)
- [Locked Runners](#locked-runners)
- [Run Untagged Jobs](#run-untagged-jobs)
- [Advanced Configuration](#advanced-configuration)
- [Auto-Create Groups](#auto-create-groups)

---

## Dynamic Tag Management via API

### The Problem with Traditional Tags

```
❌ TRADITIONAL APPROACH (Manual)
───────────────────────────────────
1. Register runner with tags: [docker, linux]
2. Need to add "nodejs" tag
3. Must UNREGISTER runner
4. Register again with [docker, linux, nodejs]
5. Lose runner history and metrics

✅ THIS ROLE (API-Based)
────────────────────────
1. Register runner with tags: [docker, linux]
2. Need to add "nodejs" tag
3. Update playbook: tags: [docker, linux, nodejs]
4. Run playbook
5. Tags updated via API (NO re-registration!)
```

### Enabling Dynamic Tag Updates

```yaml
---
- name: Dynamic Tag Management Example
  hosts: gitlab_runners
  become: true

  vars:
    gitlab_ci_runners_api_token: "{{ vault_gitlab_api_token }}"
    gitlab_ci_runners_api_runner_type: "group_type"
    gitlab_ci_runners_api_group_full_path: "myteam"
    gitlab_ci_runners_gitlab_url: "https://gitlab.com"
    
    # Enable dynamic tag updates (default: true)
    gitlab_ci_runners_update_tags_via_api: true
    
    gitlab_ci_runners_list:
      - name: "flexible-runner"
        tags:
          - docker
          - linux
          # Add more tags anytime, no re-registration needed!

  roles:
    - code3tech.devtools.gitlab_ci_runners
```

### Example: Adding Tags Without Downtime

**Initial deployment:**
```yaml
gitlab_ci_runners_list:
  - name: "app-runner"
    tags: [docker, linux]
```

**Later, add more capabilities:**
```yaml
gitlab_ci_runners_list:
  - name: "app-runner"
    tags:
      - docker
      - linux
      - nodejs        # NEW
      - python        # NEW
      - production    # NEW
```

**Run playbook:**
```bash
ansible-playbook deploy-runners.yml --vault-password-file ~/.ansible_vault_pass
```

**Result:**
- ✅ Tags updated via API
- ✅ Runner stays online
- ✅ No service restart needed
- ✅ Runner history preserved

---

## Runner Access Levels

### Understanding Access Levels

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Access Level Impact                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ACCESS LEVEL: not_protected (default)                                 │
│   ──────────────────────────────────────                                 │
│   ✅ Can run jobs from ANY branch                                       │
│   ✅ Can run jobs from ANY tag                                          │
│   ✅ No restrictions                                                     │
│                                                                          │
│   Use case: Development, testing, general CI/CD                         │
│                                                                          │
│   ─────────────────────────────────────────────────────────────────     │
│                                                                          │
│   ACCESS LEVEL: ref_protected                                           │
│   ────────────────────────────                                           │
│   ✅ Can run jobs from PROTECTED branches only (main, production)       │
│   ✅ Can run jobs from PROTECTED tags only (v1.0.0, release-*)          │
│   ❌ Cannot run jobs from feature branches                              │
│                                                                          │
│   Use case: Production deployments, critical releases                   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Configuring Access Levels

```yaml
---
- name: Access Level Configuration
  hosts: gitlab_runners
  become: true

  vars:
    gitlab_ci_runners_api_token: "{{ vault_gitlab_api_token }}"
    gitlab_ci_runners_api_runner_type: "group_type"
    gitlab_ci_runners_api_group_full_path: "production-team"
    gitlab_ci_runners_gitlab_url: "https://gitlab.com"
    
    gitlab_ci_runners_list:
      # Development runner - accepts all jobs
      - name: "dev-runner"
        tags: [docker, dev, linux]
        access_level: "not_protected"
      
      # Production runner - protected branches only
      - name: "prod-runner"
        tags: [docker, production, linux]
        access_level: "ref_protected"

  roles:
    - code3tech.devtools.gitlab_ci_runners
```

### Real-World Security Pattern

```yaml
# Three-tier runner architecture
gitlab_ci_runners_list:
  # Tier 1: Development (unrestricted)
  - name: "dev-runner-01"
    tags: [docker, dev, linux]
    access_level: "not_protected"
    run_untagged: true
  
  # Tier 2: Staging (semi-restricted)
  - name: "staging-runner-01"
    tags: [docker, staging, linux]
    access_level: "not_protected"
    run_untagged: false
  
  # Tier 3: Production (highly restricted)
  - name: "prod-runner-01"
    tags: [docker, production, deploy, linux]
    access_level: "ref_protected"  # Protected branches only!
    locked: true                    # Cannot be shared
    run_untagged: false            # Must explicitly tag jobs
```

---

## Locked Runners

### What Are Locked Runners?

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Locked vs Unlocked                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   UNLOCKED (default for group/instance runners)                         │
│   ────────────────────────────────────────────────                       │
│   Group: backend-team                                                   │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐                                │
│   │ Repo A  │  │ Repo B  │  │ Repo C  │                                │
│   └────┬────┘  └────┬────┘  └────┬────┘                                │
│        │            │            │                                      │
│        └────────────┼────────────┘                                      │
│                     ▼                                                    │
│              ┌──────────────┐                                           │
│              │ Runner       │ ✅ All repos can use                      │
│              │ (unlocked)   │                                           │
│              └──────────────┘                                           │
│                                                                          │
│   ─────────────────────────────────────────────────────────────────     │
│                                                                          │
│   LOCKED                                                                 │
│   ──────                                                                 │
│   Group: backend-team                                                   │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐                                │
│   │ Repo A  │  │ Repo B  │  │ Repo C  │                                │
│   └────┬────┘  └────┬────┘  └────┬────┘                                │
│        │            ✗            ✗                                      │
│        ▼                                                                 │
│   ┌──────────────┐                                                      │
│   │ Runner       │ ⚠️  ONLY Repo A can use (first project that used it)│
│   │ (locked)     │                                                      │
│   └──────────────┘                                                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### When to Lock Runners

**Lock runners when:**
- High-security projects (payments, healthcare)
- Dedicated hardware (GPU, large RAM)
- Compliance requirements (audit trail)
- Prevent resource sharing

**Don't lock when:**
- Shared team runners
- Cost optimization needed
- Multiple projects should share

### Configuring Locked Runners

```yaml
---
- name: Locked Runner Configuration
  hosts: gitlab_runners
  become: true

  vars:
    gitlab_ci_runners_api_token: "{{ vault_gitlab_api_token }}"
    gitlab_ci_runners_api_runner_type: "project_type"
    gitlab_ci_runners_api_project_id: "12345678"
    gitlab_ci_runners_gitlab_url: "https://gitlab.com"
    
    gitlab_ci_runners_list:
      - name: "payment-api-runner"
        tags: [docker, payment, secure, linux]
        locked: true  # Only this project can use this runner
        access_level: "ref_protected"  # Protected branches only

  roles:
    - code3tech.devtools.gitlab_ci_runners
```

---

## Run Untagged Jobs

### Understanding Untagged Jobs

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       Tagged vs Untagged Jobs                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   TAGGED JOB (.gitlab-ci.yml)                                           │
│   ───────────────────────────────                                        │
│   test:                                                                  │
│     tags: [docker, linux]  ← Explicit tags                              │
│     script: npm test                                                     │
│                                                                          │
│   ✅ Runner MUST have matching tags                                     │
│                                                                          │
│   ─────────────────────────────────────────────────────────────────     │
│                                                                          │
│   UNTAGGED JOB (.gitlab-ci.yml)                                         │
│   ─────────────────────────────                                          │
│   test:                                                                  │
│     # No tags specified!                                                │
│     script: npm test                                                     │
│                                                                          │
│   ⚠️  Runner must have run_untagged: true                               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Configuring Run Untagged

```yaml
---
- name: Run Untagged Configuration
  hosts: gitlab_runners
  become: true

  vars:
    gitlab_ci_runners_api_token: "{{ vault_gitlab_api_token }}"
    gitlab_ci_runners_api_runner_type: "group_type"
    gitlab_ci_runners_api_group_full_path: "myteam"
    gitlab_ci_runners_gitlab_url: "https://gitlab.com"
    
    gitlab_ci_runners_list:
      # Accept untagged jobs (development)
      - name: "dev-runner"
        tags: [docker, dev, linux]
        run_untagged: true  # Will pick up jobs without tags
      
      # Require tags (production)
      - name: "prod-runner"
        tags: [docker, production, linux]
        run_untagged: false  # Only explicit tagged jobs

  roles:
    - code3tech.devtools.gitlab_ci_runners
```

**Best practice:** Set `run_untagged: false` for production runners to prevent accidental job execution.

---

## Advanced Configuration

### Complete Feature Showcase

```yaml
---
- name: Advanced Runner Configuration
  hosts: gitlab_runners
  become: true

  vars:
    gitlab_ci_runners_api_token: "{{ vault_gitlab_api_token }}"
    gitlab_ci_runners_api_runner_type: "group_type"
    gitlab_ci_runners_api_group_full_path: "platform-team"
    gitlab_ci_runners_gitlab_url: "https://gitlab.com"
    
    # Global settings
    gitlab_ci_runners_update_tags_via_api: true
    gitlab_ci_runners_auto_create_group: true
    gitlab_ci_runners_group_visibility: "private"
    
    gitlab_ci_runners_runners_list:
      # Production deployment runner
      - name: "prod-deploy-runner"
        description: "Production deployment runner with security hardening"
        tags:
          - docker
          - production
          - deploy
          - linux
        executor: "docker"
        locked: true
        access_level: "ref_protected"
        run_untagged: false
        paused: false
        
      # High-throughput development runner
      - name: "dev-parallel-runner"
        description: "Development runner for parallel testing"
        tags:
          - docker
          - dev
          - test
          - linux
        executor: "docker"
        locked: false
        access_level: "not_protected"
        run_untagged: true
        paused: false

  roles:
    - code3tech.devtools.gitlab_ci_runners
```

**Note:** Docker executor requires manual configuration. To use specific Docker images, edit `/etc/gitlab-runner/{name}/config.toml` after registration.

### Global Concurrency Tuning

```yaml
# Adjust total concurrent jobs for the entire host
gitlab_ci_runners_concurrent: 20  # Maximum parallel jobs (default: 4)
```

---

## Auto-Create Groups

### Automatic Group Creation

```yaml
---
- name: Auto-Create Groups
  hosts: gitlab_runners
  become: true

  vars:
    gitlab_ci_runners_api_token: "{{ vault_gitlab_api_token }}"
    gitlab_ci_runners_api_runner_type: "group_type"
    gitlab_ci_runners_api_group_full_path: "new-team"
    gitlab_ci_runners_gitlab_url: "https://gitlab.com"
    
    # Auto-create group if it doesn't exist
    gitlab_ci_runners_auto_create_group: true
    gitlab_ci_runners_group_visibility: "private"  # or "internal", "public"
    
    gitlab_ci_runners_list:
      - name: "new-team-runner"
        tags: [docker, linux]

  roles:
    - code3tech.devtools.gitlab_ci_runners
```

**What happens:**
1. Role checks if group "new-team" exists
2. If not found, creates it with `private` visibility
3. Continues with runner registration

---

## Next Steps

Master these advanced features, then:

- **[Part 6: Production Deployment](06-production-deployment.md)** - Multi-runner production patterns
- **[Part 7: Security](07-security.md)** - Security best practices
- **[Part 8: Troubleshooting](08-troubleshooting.md)** - Common issues and solutions

---

[← Back to Guide Index](README.md)
