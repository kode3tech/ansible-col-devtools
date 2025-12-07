# Part 1: Introduction & Architecture

Welcome to the complete guide for asdf version manager! This first part covers the foundational concepts you need to understand before installation.

## 📋 Table of Contents

- [What is asdf?](#what-is-asdf)
- [Why Use asdf?](#why-use-asdf)
- [asdf Architecture](#asdf-architecture)
- [Comparison with Other Tools](#comparison-with-other-tools)
- [Role Overview](#role-overview)
- [Supported Platforms](#supported-platforms)
- [Next Steps](#next-steps)

## What is asdf?

asdf is an **extendable version manager** that allows you to manage multiple runtime versions for different programming languages and tools with a single CLI.

### Key Characteristics

```
┌─────────────────────────────────────────────────────────────────────┐
│                         What is asdf?                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  One Tool → Many Languages                                          │
│  ═══════════════════════════                                        │
│                                                                     │
│  ┌─────────┐                                                        │
│  │  asdf   │──────► Node.js 22.11.0, 20.18.0, 18.20.0              │
│  │         │──────► Python 3.13.0, 3.12.7, 3.11.10                 │
│  │         │──────► Ruby 3.3.0, 3.2.2                              │
│  │         │──────► Go 1.23.0, 1.22.5                              │
│  │         │──────► Terraform 1.9.0                                │
│  │         │──────► kubectl 1.31.0                                 │
│  │         │──────► And 300+ more plugins...                       │
│  └─────────┘                                                        │
│                                                                     │
│  Single CLI: `asdf install nodejs 22.11.0`                         │
│  Per-Project: `.tool-versions` file                                │
│  Shell Integration: bash, zsh, fish                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Core Concepts

| Concept | Description |
|---------|-------------|
| **Plugin** | Extension that adds support for a specific tool (nodejs, python, etc.) |
| **Version** | Specific release of a tool (nodejs 22.11.0) |
| **Shim** | Wrapper script that routes commands to correct version |
| **Global** | Default version used system-wide |
| **Local** | Version specific to a directory (via `.tool-versions`) |

## Why Use asdf?

### Problem: Version Manager Chaos

Without asdf, you need multiple tools:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Without asdf (Multiple Tools)                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Node.js   →  nvm install 22.11.0                                   │
│  Python    →  pyenv install 3.13.0                                  │
│  Ruby      →  rbenv install 3.3.0                                   │
│  Go        →  gvm install go1.23.0                                  │
│  Terraform →  tfenv use 1.9.0                                       │
│                                                                     │
│  ❌ Different commands for each tool                                │
│  ❌ Different configuration files                                   │
│  ❌ Different update mechanisms                                     │
│  ❌ Potential conflicts                                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Solution: One Tool for Everything

```
┌─────────────────────────────────────────────────────────────────────┐
│                      With asdf (Single Tool)                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Node.js   →  asdf install nodejs 22.11.0                          │
│  Python    →  asdf install python 3.13.0                           │
│  Ruby      →  asdf install ruby 3.3.0                              │
│  Go        →  asdf install golang 1.23.0                           │
│  Terraform →  asdf install terraform 1.9.0                         │
│                                                                     │
│  ✅ Same commands for all tools                                     │
│  ✅ Single configuration file (.tool-versions)                      │
│  ✅ One update mechanism                                            │
│  ✅ No conflicts                                                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Use Case 1: Development Teams

```yaml
# .tool-versions (shared in repository)
nodejs 22.11.0
python 3.13.0
terraform 1.9.0
```

Every developer runs `asdf install` and gets **exactly the same versions**.

### Use Case 2: CI/CD Pipelines

```yaml
# In CI pipeline
- name: Install tool versions
  run: |
    asdf install
    node --version  # Exact version from .tool-versions
```

### Use Case 3: Multiple Projects

```
~/projects/
├── project-a/
│   └── .tool-versions    # nodejs 22.11.0
├── project-b/
│   └── .tool-versions    # nodejs 20.18.0
└── project-c/
    └── .tool-versions    # nodejs 18.20.0
```

Each project automatically uses its correct version!

## asdf Architecture

### Directory Structure

```
┌─────────────────────────────────────────────────────────────────────┐
│                    asdf Directory Structure                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  /opt/asdf/                           # Installation directory      │
│  ├── bin/                                                           │
│  │   └── asdf                         # Main binary                 │
│  │                                                                  │
│  ├── plugins/                         # Installed plugins           │
│  │   ├── nodejs/                                                    │
│  │   │   ├── bin/                     # Plugin scripts              │
│  │   │   └── lib/                     # Plugin libraries            │
│  │   ├── python/                                                    │
│  │   └── terraform/                                                 │
│  │                                                                  │
│  ├── installs/                        # Installed versions          │
│  │   ├── nodejs/                                                    │
│  │   │   ├── 22.11.0/                 # Node.js 22.11.0             │
│  │   │   │   ├── bin/                                               │
│  │   │   │   └── lib/                                               │
│  │   │   └── 20.18.0/                 # Node.js 20.18.0             │
│  │   └── python/                                                    │
│  │       └── 3.13.0/                  # Python 3.13.0               │
│  │                                                                  │
│  └── shims/                           # Shim executables            │
│      ├── node                         # → nodejs/22.11.0/bin/node   │
│      ├── npm                          # → nodejs/22.11.0/bin/npm    │
│      ├── python                       # → python/3.13.0/bin/python  │
│      └── pip                          # → python/3.13.0/bin/pip     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### How Shims Work

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Shim Resolution Flow                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  User runs: $ node --version                                        │
│                    │                                                │
│                    ▼                                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 1. Shell finds /opt/asdf/shims/node (shim)                  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                    │                                                │
│                    ▼                                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 2. Shim checks for version:                                  │   │
│  │    a. .tool-versions in current directory? → Use that       │   │
│  │    b. .tool-versions in parent directories? → Use that      │   │
│  │    c. Global version set? → Use that                         │   │
│  │    d. None? → Error: No version set                          │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                    │                                                │
│                    ▼                                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 3. Shim executes: /opt/asdf/installs/nodejs/22.11.0/bin/node│   │
│  └─────────────────────────────────────────────────────────────┘   │
│                    │                                                │
│                    ▼                                                │
│  Output: v22.11.0                                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Group-Based Multi-User Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│               Centralized Group-Based Architecture                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  /opt/asdf/                                                         │
│  ├── Owner: root                                                    │
│  ├── Group: asdf                                                    │
│  └── Mode: 0775 (rwxrwxr-x)                                        │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    asdf Group Members                        │   │
│  │                                                              │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │   │
│  │  │developer │  │ devops   │  │ jenkins  │  │ deploy   │    │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │   │
│  │       │             │             │             │           │   │
│  │       └─────────────┴──────┬──────┴─────────────┘           │   │
│  │                            │                                │   │
│  │                            ▼                                │   │
│  │            All users share same plugins & versions          │   │
│  │                                                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Benefits:                                                          │
│  ✅ No duplication (single installation)                           │
│  ✅ No conflicts (group permissions)                               │
│  ✅ Simplified management (central config)                         │
│  ✅ Disk efficient (shared versions)                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Comparison with Other Tools

### Feature Comparison

| Feature | asdf | nvm | pyenv | rbenv |
|---------|------|-----|-------|-------|
| **Languages** | 300+ plugins | Node.js only | Python only | Ruby only |
| **Single CLI** | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **Per-Project Versions** | ✅ `.tool-versions` | ✅ `.nvmrc` | ✅ `.python-version` | ✅ `.ruby-version` |
| **Shell Support** | bash, zsh, fish | bash, zsh | bash, zsh | bash, zsh |
| **Plugin Ecosystem** | ✅ Extensive | ❌ N/A | ❌ N/A | ❌ N/A |
| **Multi-Language** | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **Team File** | `.tool-versions` | Need multiple files | Need multiple files | Need multiple files |

### When to Use asdf

| Scenario | Recommendation |
|----------|----------------|
| Single language project | Use nvm/pyenv/rbenv (simpler) |
| Multi-language project | ✅ **Use asdf** |
| Team standardization | ✅ **Use asdf** |
| CI/CD pipelines | ✅ **Use asdf** |
| Quick prototyping | Use nvm/pyenv (faster setup) |
| DevOps tooling | ✅ **Use asdf** (kubectl, terraform, helm) |

## Role Overview

### What This Role Does

The `code3tech.devtools.asdf` role automates:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Download      │───►│   Install       │───►│  Configure      │
│   asdf binary   │    │   to /opt/asdf  │    │  Permissions    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                      │
         ┌────────────────────────────────────────────┘
         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Create asdf    │───►│  Install        │───►│  Configure      │
│  Group          │    │  Plugins        │    │  User Shells    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                      │
         ┌────────────────────────────────────────────┘
         ▼
┌─────────────────┐    ┌─────────────────┐
│  Install        │───►│  Set Global     │
│  Versions       │    │  Versions       │
└─────────────────┘    └─────────────────┘
```

### Key Capabilities

| Feature | Description |
|---------|-------------|
| **Centralized Installation** | Single installation shared by all users |
| **Group-Based Access** | `asdf` group controls access permissions |
| **Multi-Shell Support** | bash, zsh, fish configuration |
| **Plugin Management** | Install and configure any asdf plugin |
| **Version Management** | Install specific versions, set globals |
| **System-Wide PATH** | `/etc/profile.d/asdf.sh` for all users |
| **Multi-Platform** | Ubuntu, Debian, RHEL/Rocky/Alma |

## Supported Platforms

### Operating Systems

| Distribution | Versions | Status |
|--------------|----------|--------|
| **Ubuntu** | 22.04, 24.04, 25.04 | ✅ Tested |
| **Debian** | 11, 12, 13 | ✅ Tested |
| **RHEL/Rocky/Alma** | 9, 10 | ✅ Tested |

### Shell Support

| Shell | Configuration File | Status |
|-------|-------------------|--------|
| **Bash** | `~/.bashrc` | ✅ Supported |
| **Zsh** | `~/.zshrc` | ✅ Supported |
| **Fish** | `~/.config/fish/config.fish` | ✅ Supported |

### Requirements

- **Ansible**: >= 2.15
- **Python**: >= 3.9 (on control node)
- **Network**: Internet access for downloads
- **Privileges**: Root or sudo on target hosts

## Next Steps

Now that you understand the concepts, proceed to:

➡️ **[Part 2: Prerequisites & Setup](02-prerequisites.md)** - Prepare your environment for asdf installation.

---

## Quick Reference

### Documentation Map

```
You are here: [1. Introduction] → 2. Prerequisites → 3. Basic Install → ...
```

### Key Terminology

| Term | Definition |
|------|------------|
| **asdf** | Extendable version manager for multiple tools |
| **Plugin** | Extension adding support for a specific tool |
| **Shim** | Wrapper script routing to correct version |
| **Global** | Default version for all directories |
| **Local** | Version specific to a directory |
| `.tool-versions` | File specifying versions per project |

---

[← Back to Guide Index](README.md) | [Next: Prerequisites →](02-prerequisites.md)
