# Part 1: Introduction & Concepts

> 🎬 **Video Tutorial Section**: This section covers the foundational concepts you need to understand before deploying GitHub Actions runners. Perfect for beginners who want to understand "why" before "how".

## 📋 Table of Contents

- [What is GitHub Actions?](#what-is-github-actions)
- [What are Self-Hosted Runners?](#what-are-self-hosted-runners)
- [Why Use Self-Hosted Runners?](#why-use-self-hosted-runners)
- [GitHub-Hosted vs Self-Hosted Comparison](#github-hosted-vs-self-hosted-comparison)
- [How This Role Helps](#how-this-role-helps)
- [Key Concepts Explained](#key-concepts-explained)
- [Architecture Overview](#architecture-overview)

---

## What is GitHub Actions?

### The Simple Explanation

**GitHub Actions** is GitHub's built-in automation platform. Think of it as a robot that can:
- Build your code automatically
- Run tests when you push changes
- Deploy your application to servers
- Any automation task you can imagine

### How It Works (Visual)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        GitHub Actions Flow                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────────┐      ┌──────────────┐      ┌──────────────┐          │
│   │  Developer   │      │   GitHub     │      │   Runner     │          │
│   │  pushes code │ ───▶ │   Detects    │ ───▶ │   Executes   │          │
│   │              │      │   trigger    │      │   workflow   │          │
│   └──────────────┘      └──────────────┘      └──────────────┘          │
│                                                      │                   │
│                                                      ▼                   │
│                                               ┌──────────────┐          │
│                                               │   Results    │          │
│                                               │   (logs,     │          │
│                                               │   artifacts) │          │
│                                               └──────────────┘          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Example Workflow File

```yaml
# .github/workflows/build.yml
# This file tells GitHub Actions WHAT to do

name: Build and Test          # Name shown in GitHub UI

on:                           # WHEN to run
  push:                       # When code is pushed
    branches: [main]          # To the main branch
  pull_request:               # When a PR is opened
    branches: [main]

jobs:                         # WHAT to run
  build:                      # Job name
    runs-on: ubuntu-latest    # WHERE to run (this is the RUNNER!)
    
    steps:                    # Steps to execute
      - uses: actions/checkout@v4    # Clone the repo
      - name: Run tests
        run: npm test                 # Run the tests
```

**Key point**: The `runs-on: ubuntu-latest` line specifies WHERE the job runs. This is the **runner**.

---

## What are Self-Hosted Runners?

### The Two Types of Runners

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Types of Runners                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────────────────────┐   ┌─────────────────────────────┐    │
│   │    GitHub-Hosted Runners    │   │    Self-Hosted Runners      │    │
│   ├─────────────────────────────┤   ├─────────────────────────────┤    │
│   │                             │   │                             │    │
│   │  🏢 Managed by GitHub       │   │  🏠 Managed by YOU          │    │
│   │                             │   │                             │    │
│   │  📍 runs-on: ubuntu-latest  │   │  📍 runs-on: self-hosted    │    │
│   │                             │   │                             │    │
│   │  💰 Limited free minutes    │   │  💰 You pay for server      │    │
│   │     (2000 min/month free)   │   │     (unlimited usage)       │    │
│   │                             │   │                             │    │
│   │  🔧 Pre-configured          │   │  🔧 YOU configure           │    │
│   │     environment             │   │     everything              │    │
│   │                             │   │                             │    │
│   │  🌐 Public internet         │   │  🔒 Your private network    │    │
│   │                             │   │                             │    │
│   │  ⏱️ Max 6 hours per job     │   │  ⏱️ No time limit           │    │
│   │                             │   │                             │    │
│   │  💾 Fresh VM each time      │   │  💾 Persistent or ephemeral │    │
│   │     (no caching)            │   │     (your choice)           │    │
│   │                             │   │                             │    │
│   └─────────────────────────────┘   └─────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Self-Hosted Runner: Simple Definition

A **self-hosted runner** is a computer (server, VM, or container) that YOU control, connected to GitHub to run your workflows.

**Think of it like this:**
- GitHub-hosted = Renting a car (someone else maintains it)
- Self-hosted = Your own car (you maintain it, but it's always available)

---

## Why Use Self-Hosted Runners?

### Decision Matrix: When to Use What

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     When to Use Each Type                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  USE GITHUB-HOSTED WHEN:              USE SELF-HOSTED WHEN:             │
│  ────────────────────────             ─────────────────────             │
│                                                                          │
│  ✅ Quick, simple builds              ✅ Need specific hardware         │
│     (under 6 hours)                      (GPU, ARM, special CPU)        │
│                                                                          │
│  ✅ Standard environments             ✅ Need private network access    │
│     (Node, Python, etc.)                 (internal databases, APIs)     │
│                                                                          │
│  ✅ Don't want to manage              ✅ Long-running jobs              │
│     infrastructure                       (more than 6 hours)            │
│                                                                          │
│  ✅ Low to moderate usage             ✅ High volume CI/CD              │
│     (under 2000 min/month)               (save money)                   │
│                                                                          │
│  ✅ Public open source                ✅ Compliance requirements        │
│     projects                             (data must stay on-prem)       │
│                                                                          │
│  ✅ Quick experimentation             ✅ Pre-installed tools            │
│                                          (cached dependencies)          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Real-World Use Cases for Self-Hosted

| Use Case | Why Self-Hosted? |
|----------|------------------|
| **Deploy to private servers** | Runners can access your internal network |
| **Build Docker images** | Faster with cached layers, no pull limits |
| **Run Molecule tests** | Need Docker-in-Docker capabilities |
| **Large monorepo builds** | Persistent workspace avoids re-cloning |
| **GPU-accelerated ML training** | GitHub doesn't offer GPU runners (free) |
| **Compliance (HIPAA, SOC2)** | Data never leaves your infrastructure |
| **Cost optimization** | Fixed server cost vs. per-minute billing |

### Cost Comparison Example

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Cost Comparison: 10,000 min/month                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   GITHUB-HOSTED (Team Plan):                                            │
│   ─────────────────────────                                             │
│   • 3,000 min free                                                      │
│   • 7,000 min × $0.008/min = $56/month                                  │
│   • Total: $56/month                                                    │
│                                                                          │
│   SELF-HOSTED (VPS):                                                    │
│   ─────────────────                                                     │
│   • 4 vCPU, 8GB RAM VPS ≈ $20/month                                     │
│   • Unlimited minutes                                                   │
│   • Total: $20/month (fixed)                                            │
│                                                                          │
│   SAVINGS: $36/month ($432/year)                                        │
│                                                                          │
│   ⚠️ Note: Self-hosted requires your time to manage                     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## GitHub-Hosted vs Self-Hosted Comparison

### Complete Feature Comparison

| Feature | GitHub-Hosted | Self-Hosted |
|---------|--------------|-------------|
| **Setup Time** | ⚡ Instant | 🔧 Requires configuration |
| **Maintenance** | ✅ Zero (GitHub handles) | ⚠️ You maintain |
| **Cost Model** | 💰 Per-minute | 💰 Fixed (server cost) |
| **Execution Time Limit** | ⏱️ 6 hours max | ⏱️ Unlimited |
| **Concurrent Jobs** | 📊 Limited by plan | 📊 Limited by hardware |
| **Hardware** | 🖥️ 2-4 vCPU, 7-14GB RAM | 🖥️ Whatever you provide |
| **GPU Support** | ❌ Not available (free) | ✅ If you have GPUs |
| **Private Network** | ❌ No access | ✅ Full access |
| **Pre-installed Tools** | ✅ Many tools included | 🔧 You install what you need |
| **Caching** | ⚠️ action/cache required | ✅ Persistent disk |
| **Security** | 🔒 Ephemeral (clean VM) | ⚠️ Persistent (needs hardening) |
| **Availability** | ✅ 99.9% SLA | ⚠️ Depends on your infra |
| **Scaling** | ✅ Automatic | 🔧 Manual or with tools |

---

## How This Role Helps

### The Problem This Role Solves

**Without this role**, setting up a self-hosted runner requires:

```bash
# 1. Download the runner package
curl -o actions-runner.tar.gz -L https://github.com/actions/runner/releases/...

# 2. Extract it
tar xzf actions-runner.tar.gz

# 3. Get a registration token (expires in 1 hour!)
# Go to GitHub → Settings → Actions → Runners → New runner → Copy token

# 4. Configure the runner
./config.sh --url https://github.com/myorg --token XXXXX

# 5. Install as a service
sudo ./svc.sh install
sudo ./svc.sh start

# 6. Repeat for each runner...
# 7. Manage updates manually...
# 8. Handle errors and edge cases...
```

**With this role**, you just write:

```yaml
# One playbook to deploy any number of runners
- hosts: runner_servers
  become: true
  vars:
    github_actions_runners_token: "{{ vault_github_token }}"
    github_actions_runners_organization: "myorg"
    github_actions_runners_list:
      - name: "runner-01"
      - name: "runner-02"
      - name: "runner-03"
  roles:
    - code3tech.devtools.github_actions_runners
```

### What This Role Does for You

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Role Automation Features                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  📥 INSTALLATION                                                        │
│  ────────────────                                                       │
│  ✅ Downloads latest runner automatically                               │
│  ✅ Caches download to avoid re-downloading                             │
│  ✅ Detects architecture (x64, arm64)                                   │
│  ✅ Installs OS dependencies (Debian/RedHat)                            │
│                                                                          │
│  🔧 CONFIGURATION                                                       │
│  ────────────────                                                       │
│  ✅ Gets registration token via API                                     │
│  ✅ Configures runner non-interactively                                 │
│  ✅ Sets up systemd service                                             │
│  ✅ Creates dedicated user (ghrunner)                                   │
│                                                                          │
│  🏷️ MANAGEMENT                                                          │
│  ────────────────                                                       │
│  ✅ Updates labels via API (no restart needed)                          │
│  ✅ Creates runner groups automatically                                 │
│  ✅ Handles runner removal cleanly                                      │
│  ✅ Cleans old work folders automatically                               │
│                                                                          │
│  🔐 SECURITY                                                            │
│  ────────────────                                                       │
│  ✅ no_log: true on all sensitive operations                            │
│  ✅ Runs as non-root user                                               │
│  ✅ Proper file permissions                                             │
│                                                                          │
│  🧪 VALIDATION                                                          │
│  ────────────────                                                       │
│  ✅ Validates all inputs before execution                               │
│  ✅ Clear error messages in ASCII box format                            │
│  ✅ Service health verification                                         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Key Concepts Explained

### Concept 1: Runner Scopes

**What is a "scope"?**

The scope determines WHERE the runner can be used:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Runner Scopes                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   REPOSITORY SCOPE                                                       │
│   ────────────────                                                       │
│   • Runner belongs to ONE repository                                     │
│   • Can only run workflows from that repo                                │
│   • Simplest to set up, most restricted                                  │
│                                                                          │
│   Example: Runner for "myorg/backend-api" only                           │
│                                                                          │
│   ─────────────────────────────────────────────────────────────────     │
│                                                                          │
│   ORGANIZATION SCOPE                                                     │
│   ──────────────────                                                     │
│   • Runner belongs to the organization                                   │
│   • Can run workflows from ANY repo in the org                           │
│   • Can be restricted using Runner Groups                                │
│                                                                          │
│   Example: Runner for all repos in "myorg"                               │
│                                                                          │
│   ─────────────────────────────────────────────────────────────────     │
│                                                                          │
│   ENTERPRISE SCOPE                                                       │
│   ─────────────────                                                      │
│   • Runner belongs to the enterprise                                     │
│   • Can run workflows from ANY org/repo in enterprise                    │
│   • Maximum flexibility, requires enterprise plan                        │
│                                                                          │
│   Example: Runner for "my-enterprise" covering all orgs                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Concept 2: Labels

**What are labels?**

Labels are tags that help GitHub match jobs to runners:

```yaml
# In your workflow file:
jobs:
  build:
    runs-on: [self-hosted, linux, docker]  # ← These are labels!
    
# The job will ONLY run on runners that have ALL these labels:
# - self-hosted
# - linux
# - docker
```

**How labels work:**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Label Matching                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   WORKFLOW REQUESTS:                  AVAILABLE RUNNERS:                │
│   [self-hosted, linux, docker]        ┌──────────────────────┐          │
│                                       │ runner-01            │          │
│                              ────────▶│ Labels:              │ ✅ MATCH │
│                                       │ - self-hosted        │          │
│                                       │ - linux              │          │
│                                       │ - docker             │          │
│                                       │ - nodejs             │          │
│                                       └──────────────────────┘          │
│                                                                          │
│                                       ┌──────────────────────┐          │
│                              ────────▶│ runner-02            │ ❌ NO    │
│                                       │ Labels:              │          │
│                                       │ - self-hosted        │ Missing  │
│                                       │ - linux              │ "docker" │
│                                       │ - python             │          │
│                                       └──────────────────────┘          │
│                                                                          │
│   RULE: Runner must have ALL requested labels (can have more)           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Concept 3: Runner Groups

**What are runner groups?**

Runner groups provide **access control** - they determine which repositories can use which runners.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Runner Groups                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   GROUP: "Default"                                                       │
│   ─────────────────                                                      │
│   visibility: all                                                        │
│   └── ALL repositories can use these runners                            │
│                                                                          │
│   ─────────────────────────────────────────────────────────────────     │
│                                                                          │
│   GROUP: "production"                                                    │
│   ───────────────────                                                    │
│   visibility: selected                                                   │
│   selected_repositories:                                                 │
│     - "frontend-app"                                                     │
│     - "backend-api"                                                      │
│   └── ONLY these 2 repos can use these runners                          │
│                                                                          │
│   ─────────────────────────────────────────────────────────────────     │
│                                                                          │
│   GROUP: "open-source"                                                   │
│   ────────────────────                                                   │
│   visibility: all                                                        │
│   allows_public_repos: true                                              │
│   └── Any repo (including PUBLIC) can use these runners                 │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Concept 4: Ephemeral vs Persistent Runners

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Ephemeral vs Persistent Runners                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   PERSISTENT RUNNER (Default)                                            │
│   ────────────────────────────                                           │
│   • Runs continuously                                                    │
│   • Executes job after job                                               │
│   • Keeps cache and workspace between jobs                               │
│   • ⚠️ Security: Previous job could leave malicious files               │
│                                                                          │
│   Use when: Trusted internal repos, need speed/caching                   │
│                                                                          │
│   ─────────────────────────────────────────────────────────────────     │
│                                                                          │
│   EPHEMERAL RUNNER                                                       │
│   ────────────────                                                       │
│   • Runs ONE job, then deletes itself                                    │
│   • Must be re-created for next job                                      │
│   • Clean environment every time                                         │
│   • ✅ Security: No state persists between jobs                          │
│                                                                          │
│   Use when: Public repos, untrusted code, maximum security               │
│                                                                          │
│   Enable with: ephemeral: true                                           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Architecture Overview

### How the Role Works

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Role Execution Flow                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   1. VALIDATE                                                            │
│   ───────────                                                            │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ • Check required variables (token, scope, organization)        │   │
│   │ • Validate runner names and configuration                       │   │
│   │ • Display clear error messages if something is wrong            │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                              │                                           │
│                              ▼                                           │
│   2. PREPARE                                                             │
│   ──────────                                                             │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ • Install OS dependencies (curl, tar, git)                      │   │
│   │ • Create runner user (ghrunner)                                  │   │
│   │ • Create base directory (/opt/github-actions-runners)           │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                              │                                           │
│                              ▼                                           │
│   3. DOWNLOAD                                                            │
│   ───────────                                                            │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ • Get latest version from GitHub API                            │   │
│   │ • Download runner package (or use cache)                        │   │
│   │ • Extract to runner directory                                    │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                              │                                           │
│                              ▼                                           │
│   4. REGISTER                                                            │
│   ───────────                                                            │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ • Get registration token via GitHub API                         │   │
│   │ • Run config.sh with token and labels                           │   │
│   │ • Create runner group if needed                                  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                              │                                           │
│                              ▼                                           │
│   5. SERVICE                                                             │
│   ──────────                                                             │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ • Install systemd service                                        │   │
│   │ • Enable and start service                                       │   │
│   │ • Verify service is running                                      │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                              │                                           │
│                              ▼                                           │
│   6. VERIFY                                                              │
│   ─────────                                                              │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ • Check service status                                           │   │
│   │ • Verify runner appears in GitHub UI                             │   │
│   │ • Report success or failure                                      │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Directory Structure Created

```
/opt/github-actions-runners/              ← Base path (configurable)
│
├── .downloads/                           ← Cached runner packages
│   └── actions-runner-linux-x64-2.321.0.tar.gz
│
├── runner-01/                            ← First runner
│   ├── config.sh                         ← Configuration script
│   ├── run.sh                            ← Manual run script
│   ├── svc.sh                            ← Service management
│   ├── bin/                              ← Runner binaries
│   ├── externals/                        ← Node.js, etc.
│   ├── _work/                            ← Job execution directory
│   │   ├── myrepo/                       ← Cloned repository
│   │   └── _temp/                        ← Temporary files
│   ├── _diag/                            ← Diagnostic logs
│   ├── .runner                           ← Runner configuration
│   ├── .credentials                      ← Encrypted credentials
│   └── .service                          ← Service name file
│
├── runner-02/                            ← Second runner
│   └── ...
│
└── runner-03/                            ← Third runner
    └── ...
```

### Systemd Service Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Systemd Service Architecture                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Each runner = One independent systemd service                          │
│                                                                          │
│   Service Name Pattern:                                                  │
│   actions.runner.{org}.{runner-name}.service                            │
│                                                                          │
│   Examples:                                                              │
│   • actions.runner.myorg.runner-01.service                              │
│   • actions.runner.myorg.runner-02.service                              │
│   • actions.runner.myorg.prod-runner.service                            │
│                                                                          │
│   ─────────────────────────────────────────────────────────────────     │
│                                                                          │
│   Benefits of systemd integration:                                       │
│   ✅ Auto-start on boot                                                  │
│   ✅ Auto-restart on crash                                               │
│   ✅ Central logging (journalctl)                                        │
│   ✅ Resource management (limits)                                        │
│   ✅ Service status monitoring                                           │
│                                                                          │
│   ─────────────────────────────────────────────────────────────────     │
│                                                                          │
│   Common commands:                                                       │
│   # Status                                                               │
│   sudo systemctl status actions.runner.myorg.runner-01                  │
│                                                                          │
│   # Logs                                                                 │
│   sudo journalctl -u actions.runner.myorg.runner-01 -f                  │
│                                                                          │
│   # Restart                                                              │
│   sudo systemctl restart actions.runner.myorg.runner-01                 │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Summary: What You've Learned

After reading this section, you should understand:

| Concept | Key Takeaway |
|---------|--------------|
| **GitHub Actions** | Automation platform that runs workflows in response to events |
| **Self-Hosted Runners** | Your own servers connected to GitHub to run workflows |
| **Why Self-Hosted** | Cost savings, private network access, custom hardware, no time limits |
| **Scopes** | Repository, Organization, or Enterprise level |
| **Labels** | Tags that match jobs to runners |
| **Runner Groups** | Access control for which repos can use which runners |
| **Ephemeral** | Runners that run one job then delete themselves |
| **This Role** | Automates all the complexity of deploying and managing runners |

---

**Next Section**: [Part 2: Prerequisites & Setup](02-prerequisites.md) →

---

[← Back to User Guides](../README.md)
