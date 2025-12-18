# Part 3: Basic Installation

## 📋 Table of Contents

- [Your First Runner: Step-by-Step](#your-first-runner-step-by-step)
- [Understanding the Playbook](#understanding-the-playbook)
- [Running the Playbook](#running-the-playbook)
- [Verifying the Installation](#verifying-the-installation)
- [Seeing Your Runner in GitLab](#seeing-your-runner-in-gitlab)
- [Running Your First Pipeline](#running-your-first-pipeline)
- [Common Variations](#common-variations)

---

## Your First Runner: Step-by-Step

### The Goal

We're going to:
1. ✅ Create a simple playbook
2. ✅ Deploy ONE runner to ONE server
3. ✅ Verify it appears in GitLab
4. ✅ Run a test pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        What We're Building                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   YOUR COMPUTER                              YOUR SERVER                 │
│   ─────────────                              ───────────                 │
│   ┌─────────────────┐                       ┌─────────────────┐         │
│   │ Ansible         │   SSH + Automation    │ Ubuntu/Debian/  │         │
│   │ + Playbook      │ ─────────────────────▶│ Rocky Linux     │         │
│   │ + Vault         │                       │                 │         │
│   └─────────────────┘                       │ ┌─────────────┐ │         │
│                                             │ │ Runner      │ │         │
│                                             │ │ Service     │ │         │
│                                             │ └──────┬──────┘ │         │
│                                             └────────┼────────┘         │
│                                                      │                   │
│                                                      │ Connects to       │
│                                                      ▼                   │
│                                             ┌─────────────────┐         │
│                                             │ GitLab          │         │
│                                             │ (gitlab.com)    │         │
│                                             └─────────────────┘         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Step 1: Create the Playbook File

Create a file named `install-runner.yml`:

```yaml
---
# =============================================================================
# install-runner.yml
# Your First GitLab Runner Deployment
# =============================================================================

- name: Deploy GitLab Runner - Basic Installation
  hosts: gitlab_runners
  become: true

  vars_files:
    - vars/gitlab_secrets.yml

  vars:
    # API token from vault
    gitlab_ci_runners_api_token: "{{ vault_gitlab_api_token }}"
    
    # Runner type and scope
    gitlab_ci_runners_api_runner_type: "group_type"
    gitlab_ci_runners_api_group_full_path: "myteam"
    
    # GitLab URL
    gitlab_ci_runners_gitlab_url: "https://gitlab.com"
    
    # Runners to deploy
    gitlab_ci_runners_runners_list:
      - name: "my-first-runner"
        tags:
          - docker
          - linux

  roles:
    - code3tech.devtools.gitlab_ci_runners
```

### Step 2: Review Your Configuration

Key settings explained:

| Setting | Value | Meaning |
|---------|-------|---------|
| `api_token` | From vault | Authenticates with GitLab API |
| `runner_type` | `group_type` | Runner available to group |
| `group_full_path` | `myteam` | Your GitLab group name |
| `gitlab_url` | `https://gitlab.com` | GitLab instance URL |
| `name` | `my-first-runner` | Runner display name |
| `tags` | `[docker, linux]` | How pipelines find this runner |

---

## Understanding the Playbook

### Playbook Structure

```yaml
# Target specification
- name: Deploy GitLab Runner - Basic Installation
  hosts: gitlab_runners          # Which servers to configure
  become: true                   # Use sudo privileges

  # Load secrets
  vars_files:
    - vars/gitlab_secrets.yml    # Encrypted vault file

  # Configuration
  vars:
    # API authentication
    gitlab_ci_runners_api_token: "{{ vault_gitlab_api_token }}"
    
    # Runner placement (WHERE it can be used)
    gitlab_ci_runners_api_runner_type: "group_type"
    gitlab_ci_runners_api_group_full_path: "myteam"
    
    # Runners definition (WHAT to install)
    gitlab_ci_runners_runners_list:
      - name: "my-first-runner"
        tags: [docker, linux]

  # Execute installation
  roles:
    - code3tech.devtools.gitlab_ci_runners
```

### What Happens When You Run This

```
Step 1: Ansible connects to server
  ↓
Step 2: Install GitLab Runner package
  ↓
Step 3: Create runner directory structure
  ├─ /opt/gitlab-ci-runners/my-first-runner/
  └─ /etc/gitlab-runner/my-first-runner/config.toml
  ↓
Step 4: Create runner via GitLab API
  ├─ POST to https://gitlab.com/api/v4/user/runners
  ├─ Receive runner token
  └─ Save runner ID
  ↓
Step 5: Configure runner (config.toml)
  ├─ GitLab URL
  ├─ Runner token
  ├─ Executor (docker)
  └─ Default image
  ↓
Step 6: Create systemd service
  ├─ gitlab-runner@my-first-runner.service
  └─ Enable and start
  ↓
Step 7: Verify runner is running
  ├─ Check systemd status
  ├─ Check GitLab API
  └─ ✅ Runner online!
```

---

## Running the Playbook

### Pre-Flight Checks

Before running, verify:

```bash
# 1. Check vault file exists
ls -la vars/gitlab_secrets.yml
# Should show: -rw------- 1 user user ... gitlab_secrets.yml

# 2. Verify vault can decrypt
ansible-vault view vars/gitlab_secrets.yml \
  --vault-password-file ~/.ansible_vault_pass
# Should show: vault_gitlab_api_token: "glpat-..."

# 3. Test inventory connectivity
ansible gitlab_runners -i inventory/hosts.ini -m ping
# Should show: SUCCESS

# 4. Syntax check playbook
ansible-playbook install-runner.yml --syntax-check
# Should show: playbook: install-runner.yml
```

### Run the Playbook

```bash
# Full deployment
ansible-playbook install-runner.yml \
  -i inventory/hosts.ini \
  --vault-password-file ~/.ansible_vault_pass

# With verbose output (for debugging)
ansible-playbook install-runner.yml \
  -i inventory/hosts.ini \
  --vault-password-file ~/.ansible_vault_pass \
  -v
```

### Expected Output

```
PLAY [Deploy GitLab Runner - Basic Installation] **********************

TASK [Gathering Facts] ************************************************
ok: [runner01.example.com]

TASK [code3tech.devtools.gitlab_ci_runners : Install GitLab Runner] ***
changed: [runner01.example.com]

TASK [code3tech.devtools.gitlab_ci_runners : Create runner directory] *
changed: [runner01.example.com]

TASK [code3tech.devtools.gitlab_ci_runners : Create runner via API] ***
changed: [runner01.example.com]

TASK [code3tech.devtools.gitlab_ci_runners : Configure runner] ********
changed: [runner01.example.com]

TASK [code3tech.devtools.gitlab_ci_runners : Create systemd service] **
changed: [runner01.example.com]

TASK [code3tech.devtools.gitlab_ci_runners : Start runner service] ****
changed: [runner01.example.com]

PLAY RECAP ************************************************************
runner01.example.com    : ok=7  changed=6  unreachable=0  failed=0
```

Key indicators of success:
- ✅ `failed=0` - No errors
- ✅ `changed=6` - Configuration applied
- ✅ No error messages

---

## Verifying the Installation

### On the Server

SSH to your server and verify:

```bash
# 1. Check runner service is active
systemctl status gitlab-runner-my-first-runner.service

# Expected output:
# ● gitlab-runner-my-first-runner.service - GitLab Runner (my-first-runner)
#      Loaded: loaded (/etc/systemd/system/gitlab-runner-my-first-runner.service)
#      Active: active (running) since Mon 2025-01-13 10:00:00 UTC
#    Main PID: 12345 (gitlab-runner)
#       Tasks: 11 (limit: 2319)
#      Memory: 45.2M
#         CPU: 1.234s
#      CGroup: /system.slice/gitlab-runner-my-first-runner.service
#              └─12345 /usr/bin/gitlab-runner run --config ...

# ✅ Look for "active (running)"

# 2. Check runner configuration
cat /etc/gitlab-runner/my-first-runner/config.toml

# Expected output:
# concurrent = 1
# check_interval = 0
# 
# [[runners]]
#   name = "my-first-runner"
#   url = "https://gitlab.com"
#   token = "glrt-..."
#   executor = "docker"
#   [runners.docker]
#     image = "alpine:latest"

# 3. Check runner directories exist
ls -la /opt/gitlab-ci-runners/
# Should show: my-first-runner/

# 4. Verify Docker executor (if using Docker)
docker ps
# Should show: No errors (Docker is accessible)

# 5. Check runner logs
journalctl -u gitlab-runner-my-first-runner.service -f

# Expected output:
# Configuration loaded                     builds=0
# listen_address not defined, metrics & debug endpoints disabled
# Checking for jobs... received             job=12345 repo_url=...
```

---

## Seeing Your Runner in GitLab

### Navigate to Runners Page

**For Group Runners:**
1. Go to GitLab
2. Navigate to your group: `https://gitlab.com/groups/myteam`
3. Click **Settings** → **CI/CD**
4. Expand **Runners**

**For Project Runners:**
1. Go to your project
2. Click **Settings** → **CI/CD**
3. Expand **Runners**

### Verify Runner Status

You should see:

```
┌─────────────────────────────────────────────────────────────┐
│  my-first-runner                                   🟢 Online │
│  ─────────────────────────────────────────────────────────  │
│  Tags: docker, linux                                         │
│  Executor: Docker                                            │
│  Last contact: 2 minutes ago                                 │
│  Projects: All group projects                                │
│  Description: GitLab Runner deployed via Ansible             │
│                                                              │
│  📊 Statistics:                                              │
│  ├─ Jobs run: 0                                              │
│  ├─ Jobs succeeded: 0                                        │
│  └─ Jobs failed: 0                                           │
└─────────────────────────────────────────────────────────────┘
```

**Key status indicators:**
- 🟢 **Online** (green) = Runner is healthy
- 🔴 **Offline** (red) = Runner not responding
- ⚪ **Paused** = Runner disabled

---

## Running Your First Pipeline

### Create a Test Pipeline

In any project within your group, create `.gitlab-ci.yml`:

```yaml
# .gitlab-ci.yml
# Test pipeline to verify runner is working

stages:
  - test

test-runner:
  stage: test
  tags:
    - docker        # Must match runner tags
    - linux         # Must match runner tags
  script:
    - echo "Hello from GitLab CI!"
    - echo "Runner name: $CI_RUNNER_DESCRIPTION"
    - echo "Runner ID: $CI_RUNNER_ID"
    - echo "Job ID: $CI_JOB_ID"
    - uname -a
    - cat /etc/os-release
```

### Trigger the Pipeline

1. Commit and push `.gitlab-ci.yml`
2. Go to project → **CI/CD** → **Pipelines**
3. You should see a new pipeline running

### Expected Output

```
Running with gitlab-runner 16.x (...)
  on my-first-runner abcdef12

Preparing the "docker" executor
  Using Docker executor with image alpine:latest ...
  Pulling docker image alpine:latest ...
  Using docker image sha256:... for alpine:latest ...

Preparing environment
  Running on runner-abcdef12-project-123-concurrent-0 via runner01...

Getting source from Git repository
  Fetching changes...
  Checking out abc123de...

Executing "step_script" stage of the job script
  $ echo "Hello from GitLab CI!"
  Hello from GitLab CI!
  $ echo "Runner name: $CI_RUNNER_DESCRIPTION"
  Runner name: my-first-runner
  $ echo "Runner ID: $CI_RUNNER_ID"
  Runner ID: 12345
  $ echo "Job ID: $CI_JOB_ID"
  Job ID: 67890
  $ uname -a
  Linux runner-abcdef12-project-123-concurrent-0 6.5.0 #1 SMP x86_64 GNU/Linux

Job succeeded
```

✅ **Success indicators:**
- "Running on my-first-runner" - Correct runner executed job
- "Job succeeded" - Pipeline passed
- No errors in output

---

## Common Variations

### Add More Tags

```yaml
gitlab_ci_runners_list:
  - name: "my-first-runner"
    tags:
      - docker
      - linux
      - nodejs       # For Node.js projects
      - production   # Production deployments
```

### Use Different Executor

```yaml
gitlab_ci_runners_list:
  - name: "shell-runner"
    executor: "shell"        # Run directly on host
    tags:
      - shell
      - deploy
```

### Configure Global Concurrency

```yaml
# Adjust total concurrent jobs for all runners on the host
gitlab_ci_runners_concurrent: 5  # Total concurrent jobs (default: 4)
```

**Note:** Docker executor image cannot be configured via role variables. To use a specific Docker image like `node:20-alpine`, you must manually edit `/etc/gitlab-runner/{name}/config.toml` after runner registration.

---

## What's Next?

🎉 **Congratulations!** You've deployed your first GitLab Runner!

Now explore:

- **[Part 4: Runner Types](04-runner-types.md)** - Instance vs Group vs Project runners
- **[Part 5: Advanced Features](05-advanced-features.md)** - Tag management, locked runners
- **[Part 6: Production Deployment](06-production-deployment.md)** - Multi-runner setups

---

## Troubleshooting

### "Runner appears offline"

```bash
# Check service status
systemctl status gitlab-runner-my-first-runner.service

# Check runner logs
journalctl -u gitlab-runner-my-first-runner.service -n 50

# Restart runner
systemctl restart gitlab-runner-my-first-runner.service
```

### "No jobs picked up"

```bash
# Verify tags match
# In .gitlab-ci.yml: tags: [docker, linux]
# In runner config: tags = ["docker", "linux"]

# Check runner isn't locked
# GitLab UI → Runners → Edit → Uncheck "Lock to current projects"
```

### "Docker executor fails"

```bash
# Verify Docker is running
systemctl status docker

# Test Docker access
sudo -u gitlab-runner docker ps

# Add user to docker group (if needed)
sudo usermod -aG docker gitlab-runner
```

---

[← Back to Guide Index](README.md)
