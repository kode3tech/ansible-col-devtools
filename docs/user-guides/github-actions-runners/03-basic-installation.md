# Part 3: Basic Installation

> 🎬 **Video Tutorial Section**: Your first GitHub Actions runner deployment! This section walks through the simplest installation scenario step-by-step. Perfect for getting your first runner online quickly.

## 📋 Table of Contents

- [Your First Runner: Step-by-Step](#your-first-runner-step-by-step)
- [Understanding the Playbook](#understanding-the-playbook)
- [Running the Playbook](#running-the-playbook)
- [Verifying the Installation](#verifying-the-installation)
- [Seeing Your Runner in GitHub](#seeing-your-runner-in-github)
- [Running Your First Workflow](#running-your-first-workflow)
- [Common Variations](#common-variations)

---

## Your First Runner: Step-by-Step

### The Goal

We're going to:
1. ✅ Create a simple playbook
2. ✅ Deploy ONE runner to ONE server
3. ✅ Verify it appears in GitHub
4. ✅ Run a test workflow

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
│                                             │ GitHub Actions  │         │
│                                             │ (Cloud)         │         │
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
# Your First GitHub Actions Runner Deployment
# =============================================================================
#
# WHAT THIS PLAYBOOK DOES:
# 1. Connects to your server via SSH
# 2. Installs required dependencies
# 3. Downloads the GitHub Actions runner
# 4. Registers it with your GitHub organization
# 5. Configures it as a systemd service
# 6. Starts the runner
#
# PREREQUISITES:
# - Server accessible via SSH
# - GitHub PAT in vars/github_secrets.yml
# - GitHub organization where you want the runner
#
# HOW TO RUN:
# ansible-playbook install-runner.yml -i inventory.ini --ask-vault-pass
# =============================================================================

- name: Deploy GitHub Actions Runner - Basic Installation
  hosts: github_runners          # Target servers from inventory
  become: true                   # Run with sudo (required for installation)

  # ---------------------------------------------------------------------------
  # LOAD ENCRYPTED SECRETS
  # ---------------------------------------------------------------------------
  # This loads the encrypted vault file with your GitHub token
  # The file should contain: vault_github_token: "ghp_..."
  vars_files:
    - vars/github_secrets.yml

  # ---------------------------------------------------------------------------
  # RUNNER CONFIGURATION
  # ---------------------------------------------------------------------------
  vars:
    # REQUIRED: Your GitHub Personal Access Token
    # This is loaded from the encrypted vault file
    github_actions_runners_token: "{{ vault_github_token }}"

    # REQUIRED: Runner scope (organization, repository, or enterprise)
    # We're using 'organization' - runner can serve any repo in the org
    github_actions_runners_scope: "organization"

    # REQUIRED: Your GitHub organization name
    # This is the name that appears in github.com/YOUR_ORG
    github_actions_runners_organization: "{{ vault_github_org }}"

    # ---------------------------------------------------------------------------
    # RUNNER LIST
    # ---------------------------------------------------------------------------
    # Define the runners to install on this server
    # Each item in this list creates ONE runner
    github_actions_runners_list:
      # Our first runner!
      # The name will appear in GitHub UI
      - name: "my-first-runner"

  # ---------------------------------------------------------------------------
  # EXECUTE THE ROLE
  # ---------------------------------------------------------------------------
  roles:
    - code3tech.devtools.github_actions_runners
```

### Step 2: Review Your Configuration

Let's break down every line:

```yaml
# ===========================================================================
# PLAYBOOK HEADER
# ===========================================================================

- name: Deploy GitHub Actions Runner - Basic Installation
  # ↑ This name appears when you run the playbook (for your reference)

  hosts: github_runners
  # ↑ This MUST match a group in your inventory.ini file
  # Example inventory.ini:
  #   [github_runners]
  #   192.168.1.100

  become: true
  # ↑ Run commands with sudo (root)
  # Required because we:
  #   - Install packages
  #   - Create system users
  #   - Install systemd services
```

```yaml
# ===========================================================================
# LOADING SECRETS
# ===========================================================================

  vars_files:
    - vars/github_secrets.yml
  # ↑ This loads your encrypted vault file
  # The file contains:
  #   vault_github_token: "ghp_YOUR_TOKEN"
  #   vault_github_org: "your-org-name"
```

```yaml
# ===========================================================================
# CONFIGURATION VARIABLES
# ===========================================================================

  vars:
    # The GitHub PAT for authentication
    github_actions_runners_token: "{{ vault_github_token }}"
    # ↑ References the variable from vault file
    # Ansible replaces {{ vault_github_token }} with actual value at runtime

    # Scope determines where runners can be used
    github_actions_runners_scope: "organization"
    # ↑ Options:
    #   - "organization": Any repo in your org can use this runner
    #   - "repository": Only one specific repo can use it
    #   - "enterprise": Any org in your enterprise can use it

    # Your organization name (from vault)
    github_actions_runners_organization: "{{ vault_github_org }}"
    # ↑ This is the org name from github.com/YOUR_ORG_NAME
    # Example: If your org URL is github.com/mycompany
    #          Then this should be "mycompany"
```

```yaml
# ===========================================================================
# RUNNER LIST
# ===========================================================================

    github_actions_runners_list:
      - name: "my-first-runner"
    # ↑ This is a YAML list (note the dash)
    # Each item creates one runner on the server
    # The 'name' will appear in:
    #   - GitHub UI (Settings → Actions → Runners)
    #   - Systemd service name
    #   - Log files
```

```yaml
# ===========================================================================
# ROLE EXECUTION
# ===========================================================================

  roles:
    - code3tech.devtools.github_actions_runners
    # ↑ This tells Ansible to execute our role
    # The role does ALL the heavy lifting:
    #   - Installs dependencies
    #   - Downloads runner
    #   - Registers with GitHub
    #   - Creates service
```

---

## Running the Playbook

### Pre-Flight Check

Before running, verify everything is ready:

```bash
# 1. Verify inventory has your server
cat inventory.ini

# 2. Test SSH connection
ansible github_runners -i inventory.ini -m ping

# 3. Verify vault file exists and is encrypted
cat vars/github_secrets.yml | head -2
# Should show: $ANSIBLE_VAULT;1.1;AES256
```

### Execute the Playbook

```bash
# Run with vault password prompt
ansible-playbook install-runner.yml -i inventory.ini --ask-vault-pass

# OR with vault password file
ansible-playbook install-runner.yml -i inventory.ini --vault-password-file .vault_pass
```

### What You'll See

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Expected Playbook Output                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  $ ansible-playbook install-runner.yml -i inventory.ini --ask-vault-pass│
│  Vault password: ********                                               │
│                                                                          │
│  PLAY [Deploy GitHub Actions Runner - Basic Installation] ************  │
│                                                                          │
│  TASK [Gathering Facts] ***********************************************  │
│  ok: [192.168.1.100]                                                    │
│                                                                          │
│  TASK [code3tech.devtools.github_actions_runners : Validate inputs] *** │
│  ok: [192.168.1.100]                                                    │
│                                                                          │
│  TASK [code3tech.devtools.github_actions_runners : Install deps] ******  │
│  changed: [192.168.1.100]                                               │
│                                                                          │
│  TASK [code3tech.devtools.github_actions_runners : Create user] *******  │
│  changed: [192.168.1.100]                                               │
│                                                                          │
│  TASK [code3tech.devtools.github_actions_runners : Download runner] *** │
│  changed: [192.168.1.100]                                               │
│                                                                          │
│  TASK [code3tech.devtools.github_actions_runners : Configure runner] ** │
│  changed: [192.168.1.100]                                               │
│                                                                          │
│  TASK [code3tech.devtools.github_actions_runners : Install service] *** │
│  changed: [192.168.1.100]                                               │
│                                                                          │
│  TASK [code3tech.devtools.github_actions_runners : Start service] *****  │
│  changed: [192.168.1.100]                                               │
│                                                                          │
│  TASK [code3tech.devtools.github_actions_runners : Verify service] ****  │
│  ok: [192.168.1.100]                                                    │
│                                                                          │
│  PLAY RECAP *************************************************************│
│  192.168.1.100   : ok=12   changed=6    unreachable=0    failed=0       │
│                                                                          │
│  ✅ SUCCESS! Your runner is now online.                                 │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Understanding the Output

| Status | Meaning |
|--------|---------|
| `ok` | Task completed, no changes needed |
| `changed` | Task made changes to the server |
| `failed` | Task failed (check error message) |
| `unreachable` | Cannot connect to server |
| `skipped` | Task was skipped (condition not met) |

---

## Verifying the Installation

### On the Server (SSH)

Connect to your server and verify:

```bash
# SSH to your server
ssh deploy@192.168.1.100

# 1. Check the runner directory exists
ls -la /opt/github-actions-runners/
# Expected:
# drwxr-xr-x  4 ghrunner ghrunner 4096 Dec  7 10:00 .
# drwxr-xr-x  3 root     root     4096 Dec  7 10:00 ..
# drwxr-xr-x  2 ghrunner ghrunner 4096 Dec  7 10:00 .downloads
# drwxr-xr-x 10 ghrunner ghrunner 4096 Dec  7 10:00 my-first-runner

# 2. Check the runner files
ls -la /opt/github-actions-runners/my-first-runner/
# Expected files: config.sh, run.sh, svc.sh, bin/, _work/, etc.

# 3. Check service status
sudo systemctl status actions.runner.*.my-first-runner
# Expected:
# ● actions.runner.myorg.my-first-runner.service - GitHub Actions Runner
#      Loaded: loaded (/etc/systemd/system/actions.runner...)
#      Active: active (running) since Sat 2024-12-07 10:00:00 UTC
#    Main PID: 12345 (Runner.Listener)

# 4. Check service is enabled (starts on boot)
sudo systemctl is-enabled actions.runner.*.my-first-runner
# Expected: enabled

# 5. View recent logs
sudo journalctl -u actions.runner.*.my-first-runner -n 20
# Should show "Listening for Jobs" message
```

### Quick Service Commands

```bash
# Check all runner services
sudo systemctl list-units 'actions.runner.*' --type=service

# View logs in real-time
sudo journalctl -u actions.runner.*.my-first-runner -f

# Restart runner (if needed)
sudo systemctl restart actions.runner.*.my-first-runner

# Stop runner
sudo systemctl stop actions.runner.*.my-first-runner

# Start runner
sudo systemctl start actions.runner.*.my-first-runner
```

---

## Seeing Your Runner in GitHub

### Navigate to Runners

1. Go to **github.com**
2. Navigate to your **organization**
3. Click **Settings** (gear icon)
4. In the left sidebar, click **Actions**
5. Click **Runners**

```
┌───────────────────────────────────────────────────────────────────────────┐
│  GitHub Navigation                                                         │
│  ──────────────────                                                         │
│                                                                            │
│  github.com/YOUR_ORG                                                       │
│       │                                                                    │
│       └──▶ Settings (⚙️)                                                   │
│                 │                                                          │
│                 └──▶ Actions                                               │
│                        │                                                   │
│                        └──▶ Runners  ← YOU ARE HERE                       │
│                                                                            │
└───────────────────────────────────────────────────────────────────────────┘
```

### What You Should See

```
┌───────────────────────────────────────────────────────────────────────────┐
│  Self-hosted runners                                                       │
│  ───────────────────                                                       │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  🟢 my-first-runner                                                 │  │
│  │  ────────────────────                                                │  │
│  │  Status: Idle                                                        │  │
│  │  Labels: self-hosted, Linux, X64                                    │  │
│  │  Group: Default                                                      │  │
│  │                                                                      │  │
│  │  ↑ Your runner should appear here with a GREEN dot!                │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  Status Indicators:                                                        │
│  🟢 Idle     = Online, waiting for jobs                                   │
│  🟢 Active   = Currently running a job                                    │
│  🟡 Offline  = Service not running (check server)                         │
│  🔴 Error    = Something is wrong (check logs)                            │
│                                                                            │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## Running Your First Workflow

### Create a Test Workflow

In any repository in your organization, create a workflow file:

```yaml
# .github/workflows/test-self-hosted-runner.yml
# This workflow tests your new self-hosted runner

name: Test Self-Hosted Runner

# Trigger: Manual run only (for testing)
on:
  workflow_dispatch:              # Allows manual trigger from GitHub UI
    inputs:
      message:
        description: 'Message to display'
        required: false
        default: 'Hello from self-hosted runner!'

jobs:
  test-runner:
    name: Test Runner
    
    # ⭐ THIS IS THE KEY PART!
    # runs-on tells GitHub to use a self-hosted runner
    runs-on: [self-hosted, Linux]
    # ↑ This means: Use a runner with labels "self-hosted" AND "Linux"
    
    steps:
      - name: 👋 Say Hello
        run: |
          echo "======================================"
          echo "${{ github.event.inputs.message }}"
          echo "======================================"
          echo ""
          echo "🖥️  Runner Information:"
          echo "   Hostname: $(hostname)"
          echo "   OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2)"
          echo "   Kernel: $(uname -r)"
          echo "   User: $(whoami)"
          echo ""
          echo "📂 Working Directory:"
          echo "   $(pwd)"
          echo ""
          echo "✅ Self-hosted runner is working correctly!"
      
      - name: 🔍 Check Available Tools
        run: |
          echo "Available tools on this runner:"
          echo ""
          echo "Git: $(git --version 2>/dev/null || echo 'Not installed')"
          echo "Docker: $(docker --version 2>/dev/null || echo 'Not installed')"
          echo "Python: $(python3 --version 2>/dev/null || echo 'Not installed')"
          echo "Node: $(node --version 2>/dev/null || echo 'Not installed')"
      
      - name: 📊 System Resources
        run: |
          echo "System Resources:"
          echo ""
          echo "CPU Cores: $(nproc)"
          echo "Memory: $(free -h | grep Mem | awk '{print $2}')"
          echo "Disk: $(df -h / | tail -1 | awk '{print $4}') available"
```

### Trigger the Workflow

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Click **Test Self-Hosted Runner** in the left sidebar
4. Click **Run workflow** button
5. Optionally enter a custom message
6. Click **Run workflow**

```
┌───────────────────────────────────────────────────────────────────────────┐
│  Running the Test Workflow                                                 │
│  ─────────────────────────                                                 │
│                                                                            │
│  Repository → Actions → Test Self-Hosted Runner                           │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  Run workflow  ▼                                                    │  │
│  │  ─────────────────                                                   │  │
│  │                                                                      │  │
│  │  Use workflow from: [main ▼]                                        │  │
│  │                                                                      │  │
│  │  Message to display:                                                 │  │
│  │  ┌────────────────────────────────────────────────────────────┐     │  │
│  │  │ Testing my new self-hosted runner!                         │     │  │
│  │  └────────────────────────────────────────────────────────────┘     │  │
│  │                                                                      │  │
│  │  [Run workflow] ← CLICK THIS                                        │  │
│  │                                                                      │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
└───────────────────────────────────────────────────────────────────────────┘
```

### View the Results

After clicking "Run workflow", you'll see the job running:

```
┌───────────────────────────────────────────────────────────────────────────┐
│  Workflow Run Results                                                      │
│  ────────────────────                                                      │
│                                                                            │
│  Test Self-Hosted Runner  #1                                              │
│  ═════════════════════════                                                 │
│                                                                            │
│  ✅ test-runner                                                           │
│     │                                                                      │
│     ├── ✅ Set up job                          (1s)                       │
│     ├── ✅ 👋 Say Hello                        (0s)                       │
│     ├── ✅ 🔍 Check Available Tools            (0s)                       │
│     ├── ✅ 📊 System Resources                 (0s)                       │
│     └── ✅ Complete job                        (0s)                       │
│                                                                            │
│  Duration: 3s                                                              │
│  Runner: my-first-runner                                                  │
│                                                                            │
│  🎉 Your self-hosted runner successfully executed the workflow!          │
│                                                                            │
└───────────────────────────────────────────────────────────────────────────┘
```

### Troubleshooting: Workflow Stuck at "Queued"

If your workflow stays at "Queued" and never starts:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Workflow Stuck? Common Causes                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. RUNNER NOT ONLINE                                                   │
│     Check: GitHub Settings → Actions → Runners                          │
│     Should show: 🟢 Idle                                                │
│     Fix: Check service on server                                        │
│          sudo systemctl status actions.runner.*                         │
│                                                                          │
│  2. LABELS DON'T MATCH                                                  │
│     Workflow says: runs-on: [self-hosted, Linux, docker]               │
│     Runner has: self-hosted, Linux, X64                                │
│     Problem: Runner doesn't have "docker" label                        │
│     Fix: Add label to runner or remove from workflow                   │
│                                                                          │
│  3. RUNNER GROUP RESTRICTIONS                                           │
│     If runner is in a group with visibility: "selected"                │
│     And your repo is not in selected_repositories                      │
│     The workflow can't use that runner                                 │
│     Fix: Add repo to group or use different runner                     │
│                                                                          │
│  4. RUNNER IS BUSY                                                      │
│     If runner shows: 🟢 Active                                         │
│     It's running another job                                           │
│     Fix: Wait or add more runners                                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Common Variations

### Variation 1: Multiple Runners on One Server

```yaml
# Deploy 3 runners on the same server
github_actions_runners_list:
  # Runner 1: General purpose
  - name: "runner-01"
  
  # Runner 2: General purpose
  - name: "runner-02"
  
  # Runner 3: General purpose
  - name: "runner-03"
```

**Why?** One runner = one job at a time. Multiple runners allow parallel jobs.

### Variation 2: Runner with Custom Labels

```yaml
# Deploy runner with specific capabilities
github_actions_runners_list:
  - name: "docker-runner"
    labels:
      - "docker"       # Has Docker installed
      - "nodejs"       # Has Node.js
      - "python"       # Has Python
```

**Usage in workflow:**
```yaml
jobs:
  build:
    runs-on: [self-hosted, docker, nodejs]
    # ↑ Will only run on runners with ALL these labels
```

### Variation 3: Dynamic Runner Name (Using Hostname)

```yaml
# Runner name includes server hostname
github_actions_runners_list:
  - name: "runner-{{ inventory_hostname }}"
```

**Result:** On server `web01`, runner name will be `runner-web01`

### Variation 4: Runner with Specific Version

```yaml
# Pin to specific runner version (for stability)
github_actions_runners_version: "2.321.0"

github_actions_runners_list:
  - name: "stable-runner"
```

### Variation 5: Complete Example with All Options

```yaml
---
- name: Deploy GitHub Actions Runner - Complete Example
  hosts: github_runners
  become: true

  vars_files:
    - vars/github_secrets.yml

  vars:
    # Authentication
    github_actions_runners_token: "{{ vault_github_token }}"
    
    # Scope
    github_actions_runners_scope: "organization"
    github_actions_runners_organization: "{{ vault_github_org }}"
    
    # Installation settings
    github_actions_runners_version: ""              # Empty = latest
    github_actions_runners_base_path: "/opt/github-actions-runners"
    github_actions_runners_user: "ghrunner"
    github_actions_runners_group: "ghrunner"
    
    # Service settings
    github_actions_runners_service_enabled: true
    github_actions_runners_service_state: "started"
    
    # Runner definitions
    github_actions_runners_list:
      - name: "prod-runner-{{ inventory_hostname }}"
        labels:
          - "production"
          - "docker"
          - "nodejs-18"

  roles:
    - code3tech.devtools.github_actions_runners
```

---

## Summary: What You've Accomplished

| Step | Status | Description |
|------|--------|-------------|
| Created playbook | ✅ | Basic installation playbook |
| Ran playbook | ✅ | Deployed runner to server |
| Verified on server | ✅ | Service running correctly |
| Verified in GitHub | ✅ | Runner appears in UI |
| Ran test workflow | ✅ | Confirmed runner executes jobs |

### What's Next?

Now that you have a basic runner working, you can:

- **Add labels** to categorize runners (Part 5)
- **Create runner groups** for access control (Part 5)
- **Deploy to multiple servers** (Part 4)
- **Configure for specific scopes** (Part 4)
- **Enable advanced features** (Part 6)

---

**Next Section**: [Part 4: Runner Scopes](04-runner-scopes.md) →

← **Previous Section**: [Part 2: Prerequisites & Setup](02-prerequisites.md)

---

[← Back to User Guides](../README.md)
