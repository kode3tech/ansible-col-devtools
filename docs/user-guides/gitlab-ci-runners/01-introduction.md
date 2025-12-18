# Part 1: Introduction & Concepts

## 📋 Table of Contents

- [What is GitLab CI/CD?](#what-is-gitlab-cicd)
- [What are GitLab Runners?](#what-are-gitlab-runners)
- [Why Use Self-Hosted Runners?](#why-use-self-hosted-runners)
- [SaaS vs Self-Hosted Comparison](#saas-vs-self-hosted-comparison)
- [How This Role Helps](#how-this-role-helps)
- [Key Concepts Explained](#key-concepts-explained)
- [Architecture Overview](#architecture-overview)

---

## What is GitLab CI/CD?

### The Simple Explanation

**GitLab CI/CD** is GitLab's built-in automation platform. Think of it as a robot that can:
- Build your code automatically
- Run tests when you push changes
- Deploy your application to servers
- Any automation task you can imagine

### How It Works (Visual)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        GitLab CI/CD Flow                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────────┐      ┌──────────────┐      ┌──────────────┐          │
│   │  Developer   │      │   GitLab     │      │   Runner     │          │
│   │  pushes code │ ───▶ │   Detects    │ ───▶ │   Executes   │          │
│   │              │      │   trigger    │      │   pipeline   │          │
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

### Example Pipeline File

```yaml
# .gitlab-ci.yml
# This file tells GitLab CI WHAT to do

stages:                      # PHASES of your pipeline
  - build
  - test
  - deploy

build-job:                   # Job name
  stage: build               # Which stage it belongs to
  tags:                      # WHICH RUNNER to use (important!)
    - docker
    - linux
  script:                    # WHAT to run
    - npm install
    - npm run build

test-job:
  stage: test
  tags:
    - docker
    - linux
  script:
    - npm test

deploy-job:
  stage: deploy
  tags:
    - production           # This uses a SPECIFIC runner!
  script:
    - ./deploy.sh
```

**Key point**: The `tags:` section specifies WHICH runner executes the job. This is crucial for self-hosted runners.

---

## What are GitLab Runners?

### The Two Types of Runners

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Types of Runners                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────────────────────┐   ┌─────────────────────────────┐    │
│   │    SaaS Runners             │   │    Self-Hosted Runners      │    │
│   │    (GitLab-managed)         │   │    (Your infrastructure)    │    │
│   ├─────────────────────────────┤   ├─────────────────────────────┤    │
│   │                             │   │                             │    │
│   │  🏢 Managed by GitLab       │   │  🏠 Managed by YOU          │    │
│   │                             │   │                             │    │
│   │  📍 tags: [saas-linux]      │   │  📍 tags: [your-custom-tag] │    │
│   │                             │   │                             │    │
│   │  💰 Limited free minutes    │   │  💰 You pay for server      │    │
│   │     (400 min/month free)    │   │     (unlimited usage)       │    │
│   │                             │   │                             │    │
│   │  🔧 Pre-configured          │   │  🔧 YOU configure           │    │
│   │     environment             │   │     everything              │    │
│   │                             │   │                             │    │
│   │  🌍 Public cloud            │   │  🔐 Your network            │    │
│   │     (shared resources)      │   │     (private, isolated)     │    │
│   │                             │   │                             │    │
│   │  ⚡ Auto-scaling            │   │  ⚡ You control scaling     │    │
│   │                             │   │                             │    │
│   └─────────────────────────────┘   └─────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### What is a Runner? (Technical Definition)

A **GitLab Runner** is:
- An agent/service that runs on a server
- Communicates with GitLab to fetch jobs
- Executes pipeline jobs in isolation
- Reports results back to GitLab

Think of it like a worker that:
1. Asks GitLab: "Do you have work for me?"
2. Gets a job: "Yes, run these tests"
3. Executes the job
4. Reports: "Done! Here are the results"

---

## Why Use Self-Hosted Runners?

### Top Reasons Organizations Choose Self-Hosted

```
┌─────────────────────────────────────────────────────────────────────────┐
│                Why Self-Host? (Decision Matrix)                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   💰 COST                                                                │
│   ────────                                                               │
│   • Free minutes exhausted quickly on large projects                    │
│   • Existing server infrastructure can be reused                        │
│   • Predictable costs (server + electricity vs per-minute billing)      │
│                                                                          │
│   🔐 SECURITY & COMPLIANCE                                               │
│   ──────────────────────                                                 │
│   • Keep sensitive data within your network                             │
│   • Meet compliance requirements (HIPAA, SOC2, PCI-DSS)                 │
│   • Access internal resources (databases, APIs, staging environments)   │
│   • No code leaves your infrastructure                                  │
│                                                                          │
│   ⚙️ CUSTOM ENVIRONMENT                                                  │
│   ────────────────────                                                   │
│   • Install specific software versions                                  │
│   • Use proprietary tools                                               │
│   • Custom hardware (GPUs for ML, specific CPUs)                        │
│   • Pre-configured build environments                                   │
│                                                                          │
│   🚀 PERFORMANCE                                                         │
│   ─────────────                                                          │
│   • Faster builds (local caching, faster network)                       │
│   • Dedicated resources (not shared with other users)                   │
│   • Optimize for YOUR workloads                                         │
│                                                                          │
│   🎯 CONTROL                                                             │
│   ──────────                                                             │
│   • Full control over runner configuration                              │
│   • Custom executor types (Docker, Shell, Kubernetes)                   │
│   • Manage runner lifecycle                                             │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Real-World Example Scenarios

#### Scenario 1: Development Team with Private API
```
Problem:
  Your CI/CD pipeline needs to test against an internal API
  that is NOT accessible from the internet.

Solution with Self-Hosted Runner:
  ✅ Runner deployed in your network
  ✅ Can reach internal API directly
  ✅ Tests run successfully
  ✅ No need to expose API publicly
```

#### Scenario 2: High Pipeline Usage
```
Problem:
  Team runs 10,000 minutes/month of CI/CD
  GitLab SaaS: $10/month per user + overages
  10 developers = $100/month + ~$800 overages = $900/month

Solution with Self-Hosted Runner:
  ✅ Buy a $50/month server
  ✅ Run unlimited pipelines
  ✅ Save ~$850/month
```

#### Scenario 3: Compliance Requirements
```
Problem:
  Healthcare app requires HIPAA compliance
  Code cannot leave your infrastructure
  Must maintain audit logs

Solution with Self-Hosted Runner:
  ✅ Runner deployed on-premise
  ✅ All CI/CD data stays internal
  ✅ Full audit trail control
  ✅ Compliance requirements met
```

---

## SaaS vs Self-Hosted Comparison

### Decision Matrix

| Aspect | SaaS Runners | Self-Hosted Runners |
|--------|--------------|---------------------|
| **Setup Time** | ✅ Instant (no setup) | ⚠️ ~15-30 minutes initial setup |
| **Maintenance** | ✅ Zero (GitLab manages) | ⚠️ You maintain OS, updates |
| **Cost** | 💰 Per-minute billing | 💰 Server cost (fixed) |
| **Free Tier** | 400 min/month | ∞ Unlimited |
| **Security** | ⚠️ Code runs on shared infrastructure | ✅ Full control, isolated |
| **Customization** | ❌ Pre-defined environments | ✅ Full customization |
| **Performance** | ⚠️ Shared resources | ✅ Dedicated resources |
| **Scaling** | ✅ Auto-scales | ⚠️ Manual (but this role helps!) |
| **Internal Access** | ❌ No access to private networks | ✅ Full internal access |
| **Compliance** | ⚠️ Depends on GitLab SaaS compliance | ✅ You control compliance |

### When to Use Each

**Use SaaS Runners when:**
- Small team/project (under 400 min/month)
- No compliance requirements
- No internal resource access needed
- Don't want to manage infrastructure
- Public open-source project

**Use Self-Hosted Runners when:**
- High CI/CD usage (>400 min/month)
- Need internal network access
- Compliance/security requirements
- Want full environment control
- Have existing server infrastructure
- Cost optimization is important

---

## How This Role Helps

### The Challenge Without This Role

Setting up GitLab Runners manually involves:

```
❌ MANUAL SETUP (Error-prone, time-consuming)
   ├─ Download correct GitLab Runner binary
   ├─ Create service user and directories
   ├─ Configure systemd service
   ├─ Generate registration token from GitLab
   ├─ Register runner with correct parameters
   ├─ Configure executor (Docker, Shell, etc.)
   ├─ Set up tags, access levels, locked state
   ├─ Manage multiple runners
   ├─ Handle runner updates
   ├─ Troubleshoot configuration issues
   └─ Repeat for every server!
```

### The Solution: `code3tech.devtools.gitlab_ci_runners`

This Ansible role automates EVERYTHING:

```
✅ AUTOMATED SETUP (Reliable, fast, repeatable)
   ├─ ✅ Installs GitLab Runner (correct version for your OS)
   ├─ ✅ Creates all necessary users and directories
   ├─ ✅ Configures systemd services automatically
   ├─ ✅ Uses GitLab API for runner management (no manual token generation!)
   ├─ ✅ Supports all runner types (Instance, Group, Project)
   ├─ ✅ Manages tags dynamically via API
   ├─ ✅ Configures advanced settings (locked, run_untagged, access_level)
   ├─ ✅ Deploys N runners per host with isolated configs
   ├─ ✅ Each runner gets its own systemd service
   ├─ ✅ Handles runner lifecycle (create, update, delete)
   ├─ ✅ Idempotent (safe to run multiple times)
   └─ ✅ Multi-distribution support (Ubuntu, Debian, RHEL)
```

### Key Features

| Feature | Description |
|---------|-------------|
| **🔄 API-First Approach** | Uses GitLab REST API for all operations (no manual registration tokens!) |
| **🎯 Multi-Runner Architecture** | Deploy N runners per host, each with isolated config and systemd service |
| **🏷️ Dynamic Tag Management** | Update tags via API without re-registering runners |
| **🔐 Three Runner Types** | Instance (admin), Group, and Project runners supported |
| **⚙️ Advanced Configuration** | `run_untagged`, `locked`, `access_level` settings |
| **🚀 Auto-Create Resources** | Automatically create groups if they don't exist |
| **🛡️ Production-Ready** | Comprehensive error handling, validation, and service management |
| **📦 Multi-Distribution** | Ubuntu 22+, Debian 11+, RHEL/CentOS/Rocky 9+ |

---

## Key Concepts Explained

### 1. Runner Types (Scopes)

GitLab has **three types** of runners based on WHERE they can be used:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Runner Type Hierarchy                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│                    ┌─────────────────────────────────┐                  │
│                    │      INSTANCE RUNNER            │                  │
│                    │  (All projects in GitLab)       │                  │
│                    │  🔑 Requires: Admin token       │                  │
│                    │                                 │                  │
│                    │   ┌─────────────────────────┐   │                  │
│                    │   │     GROUP RUNNER        │   │                  │
│                    │   │  (All projects in group)│   │                  │
│                    │   │  🔑 Requires: Group PAT │   │                  │
│                    │   │                         │   │                  │
│                    │   │   ┌─────────────────┐   │   │                  │
│                    │   │   │ PROJECT RUNNER  │   │   │                  │
│                    │   │   │ (Single project)│   │   │                  │
│                    │   │   │ 🔑 Project PAT  │   │   │                  │
│                    │   │   └─────────────────┘   │   │                  │
│                    │   │                         │   │                  │
│                    │   └─────────────────────────┘   │                  │
│                    │                                 │                  │
│                    └─────────────────────────────────┘                  │
│                                                                          │
│   Scope:           Broadest ◄──────────────────────► Narrowest         │
│   Sharing:         Most Shared ◄───────────────────► Least Shared      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Quick comparison:**

| Type | Scope | PAT Required | Use Case |
|------|-------|--------------|----------|
| **Instance** | Entire GitLab instance | Admin | Shared infrastructure runners |
| **Group** | All projects in group | Group owner/maintainer | Team/department runners |
| **Project** | Single project only | Project maintainer | Dedicated project runners |

### 2. Tags (How Jobs Find Runners)

**Tags** are labels that connect jobs to runners:

```yaml
# In .gitlab-ci.yml
job-name:
  tags:
    - docker        # This job REQUIRES a runner with "docker" tag
    - linux         # AND "linux" tag
    - production    # AND "production" tag
  script:
    - npm test
```

**How it works:**
1. Job says: "I need tags: docker, linux, production"
2. GitLab finds all runners with ALL these tags
3. Job is assigned to one of those runners

**Important:** With this role, you can update tags via API without re-registering!

### 3. Multi-Runner Architecture

This role supports deploying **multiple runners on a single host**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Server: ci-runner-01                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Runner 1: backend-runner                                              │
│   ├─ Service: gitlab-runner-backend-runner.service                      │
│   ├─ Config: /etc/gitlab-runner/backend-runner/config.toml              │
│   ├─ Tags: [docker, linux, backend]                                     │
│   └─ Type: Group runner (backend-team group)                            │
│                                                                          │
│   Runner 2: frontend-runner                                             │
│   ├─ Service: gitlab-runner-frontend-runner.service                     │
│   ├─ Config: /etc/gitlab-runner/frontend-runner/config.toml             │
│   ├─ Tags: [docker, linux, frontend, nodejs]                            │
│   └─ Type: Group runner (frontend-team group)                           │
│                                                                          │
│   Runner 3: deploy-runner                                               │
│   ├─ Service: gitlab-runner-deploy-runner.service                       │
│   ├─ Config: /etc/gitlab-runner/deploy-runner/config.toml               │
│   ├─ Tags: [shell, production, deploy]                                  │
│   └─ Type: Instance runner (all projects)                               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Benefits:**
- Isolated configurations per runner
- Different executors (Docker, Shell) on same host
- Independent service control (`systemctl restart gitlab-runner@backend-runner`)
- Easy to add/remove runners

### 4. Executors (How Jobs Run)

An **executor** determines HOW the runner executes jobs:

| Executor | How It Works | Use Case |
|----------|--------------|----------|
| **Docker** | Runs jobs in Docker containers | ✅ **Most common**, isolated, clean environment |
| **Shell** | Runs jobs directly on host | Deployments, accessing host resources |
| **Kubernetes** | Runs jobs in K8s pods | Cloud-native, highly scalable |
| **Docker+Machine** | Auto-scales Docker hosts | Large-scale auto-scaling |

**This role defaults to Docker executor** (most popular and isolated).

---

## Architecture Overview

### Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    GitLab CI Self-Hosted Architecture                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────────────────────────────────────────────────────────┐      │
│   │                    GitLab Instance                            │      │
│   │  (gitlab.com or self-hosted GitLab server)                   │      │
│   ├──────────────────────────────────────────────────────────────┤      │
│   │                                                              │      │
│   │  • Stores code in Git repositories                           │      │
│   │  • Manages .gitlab-ci.yml pipeline definitions               │      │
│   │  • Orchestrates job assignment to runners                    │      │
│   │  • Displays pipeline results                                 │      │
│   │  • Provides REST API for runner management                   │      │
│   │                                                              │      │
│   └────────────────────────┬─────────────────────────────────────┘      │
│                            │                                            │
│                            │ HTTPS API + Runner Protocol                │
│                            │                                            │
│   ┌────────────────────────┴─────────────────────────────────────┐      │
│   │                   Self-Hosted Runner Host                     │      │
│   │                  (Your server/VM/container)                   │      │
│   ├──────────────────────────────────────────────────────────────┤      │
│   │                                                              │      │
│   │  gitlab-runner@myrunner.service (systemd)                    │      │
│   │  ├─ Polls GitLab: "Got jobs for me?"                         │      │
│   │  ├─ Receives job: "Yes, run tests"                           │      │
│   │  ├─ Spawns executor (Docker container)                       │      │
│   │  │   └─ Runs job script inside container                     │      │
│   │  ├─ Collects logs and artifacts                              │      │
│   │  └─ Reports results to GitLab                                │      │
│   │                                                              │      │
│   │  Config: /etc/gitlab-runner/myrunner/config.toml             │      │
│   │                                                              │      │
│   └──────────────────────────────────────────────────────────────┘      │
│                                                                          │
│   ┌──────────────────────────────────────────────────────────────┐      │
│   │                   Ansible Controller                          │      │
│   │                  (Your laptop/automation server)              │      │
│   ├──────────────────────────────────────────────────────────────┤      │
│   │                                                              │      │
│   │  • Uses code3tech.devtools.gitlab_ci_runners role            │      │
│   │  • Installs GitLab Runner on target hosts                    │      │
│   │  • Registers runners via GitLab API                          │      │
│   │  • Configures systemd services                               │      │
│   │  • Manages runner lifecycle                                  │      │
│   │                                                              │      │
│   └──────────────────────────────────────────────────────────────┘      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Data Flow: From Code Push to Pipeline Result

```
1. Developer pushes code to GitLab
   ↓
2. GitLab detects .gitlab-ci.yml, creates pipeline
   ↓
3. GitLab creates jobs from pipeline definition
   ↓
4. Runner polls GitLab: "Got jobs for tags: [docker, linux]?"
   ↓
5. GitLab: "Yes! Run these tests"
   ↓
6. Runner downloads job details and code
   ↓
7. Runner spawns Docker container (executor)
   ↓
8. Job script runs inside container
   ↓
9. Runner captures logs and artifacts
   ↓
10. Runner uploads results to GitLab
    ↓
11. GitLab displays results in UI
    ↓
12. Developer sees green ✅ or red ❌
```

---

## Next Steps

Now that you understand the concepts, you're ready to deploy!

**Continue to [Part 2: Prerequisites & Setup](02-prerequisites.md)** to prepare your environment.

Or jump directly to:
- **[Part 3: Basic Installation](03-basic-installation.md)** - If you're ready to deploy
- **[Part 4: Runner Types](04-runner-types.md)** - Learn about Instance vs Group vs Project runners
- **[Part 6: Production Deployment](06-production-deployment.md)** - Production patterns

---

[← Back to Guide Index](README.md)
