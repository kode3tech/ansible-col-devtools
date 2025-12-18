# Collection Upgrade Guide

This guide helps you upgrade between major versions of the `code3tech.devtools` Ansible Collection.

## 📋 Table of Contents

- [Version Overview](#version-overview)
- [Upgrade Path](#upgrade-path)
- [Version-Specific Guides](#version-specific-guides)
  - [Upgrading to v2.0.0 (asdf Breaking Changes)](#upgrading-to-v200-asdf-breaking-changes)
  - [Upgrading to v1.4.0 (GitLab CI Runners)](#upgrading-to-v140-gitlab-ci-runners)
  - [Upgrading to v1.3.0 (Documentation Restructure)](#upgrading-to-v130-documentation-restructure)
  - [Upgrading to v1.2.0 (GitHub Actions Runners)](#upgrading-to-v120-github-actions-runners)
  - [Upgrading to v1.1.0 (Azure DevOps Agents + Podman Changes)](#upgrading-to-v110-azure-devops-agents--podman-changes)
- [Role-Specific Upgrade Guides](#role-specific-upgrade-guides)
- [General Upgrade Process](#general-upgrade-process)
- [Support](#support)

---

## Version Overview

| Version | Release Date | Type | Key Changes |
|---------|--------------|------|-------------|
| **1.4.0** | 2025-12-16 | Feature | GitLab CI Runners role added |
| **1.3.1** | 2025-12-12 | Patch | CI/CD workflow fixes |
| **1.3.0** | 2025-01-27 | Feature | Documentation restructure (modular guides) |
| **1.2.0** | 2025-12-07 | Feature | GitHub Actions Runners role added, RHEL 9+ support |
| **1.1.0** | 2025-12-05 | Feature | Azure DevOps Agents role added, **Podman breaking changes** |
| **1.0.0** | 2025-11-05 | Major | Initial release (Docker, Podman) |

---

## Upgrade Path

### Safe Upgrade Path

```
v1.0.0 → v1.1.0 → v1.2.0 → v1.3.0 → v1.3.1 → v1.4.0
```

### Direct Upgrade (Current Version → Latest)

```bash
# Install latest collection
ansible-galaxy collection install code3tech.devtools --force

# Verify version
ansible-galaxy collection list | grep code3tech.devtools
```

**⚠️ Important:** Review all version-specific changes below before upgrading.

---

## Version-Specific Guides

### Upgrading to v2.0.0 (asdf Breaking Changes)

**Status:** Future release  
**Impact:** 🔴 **BREAKING CHANGES** in asdf role

#### What Changed?

**asdf role** was redesigned from per-user to centralized group-based architecture:

**Before (v1.x):**
```yaml
asdf_users:
  - name: "user1"
    shell: "bash"
    plugins:
      - name: "nodejs"
        versions: ["20.11.0"]
        global: "20.11.0"
```

**Now (v2.x):**
```yaml
asdf_plugins:
  - name: "nodejs"
    versions: ["20.11.0"]
    global: "20.11.0"

asdf_users:
  - "user1"
  - "user2"
```

#### Migration Steps

1. **Update playbook variables** to new format
2. **Run playbook** to apply centralized configuration
3. **Verify** all users can access asdf

📖 **Complete guide:** See [asdf v1.x to v2.x Migration](../user-guides/asdf/upgrade-v1-to-v2.md)

---

### Upgrading to v1.4.0 (GitLab CI Runners)

**Impact:** 🟢 **No breaking changes** - New role added

#### What's New?

- **New role:** `gitlab_ci_runners` for managing GitLab CI runners
- **Three runner types:** Instance, Group, Project
- **API-based management:** Create, update, delete runners via REST API
- **Advanced features:** Tag management, run_untagged, locked runners

#### Upgrade Steps

```bash
# 1. Install collection
ansible-galaxy collection install code3tech.devtools:1.4.0 --force

# 2. Install dependencies
ansible-galaxy collection install -r requirements.yml

# 3. Use new role (optional)
# See: playbooks/gitlab_ci_runners/install-production.yml
```

📖 **Complete guide:** [GitLab CI Runners Documentation](../user-guides/gitlab-ci-runners/)

---

### Upgrading to v1.3.0 (Documentation Restructure)

**Impact:** 🟡 **Documentation changes only** - No code changes

#### What Changed?

- **Modular documentation:** All roles now have 8-part modular guides
- **Removed:** Monolithic `COMPLETE_GUIDE.md` files
- **Removed:** Centralized `REGISTRY_AUTHENTICATION.md`
- **New:** Per-role `04-registry-auth.md` guides

#### Upgrade Steps

No playbook changes required. Update your bookmarks:

- **Old:** `docs/DOCKER_COMPLETE_GUIDE.md`
- **New:** `docs/user-guides/docker/README.md`

---

### Upgrading to v1.2.0 (GitHub Actions Runners)

**Impact:** 🟢 **No breaking changes** - New role + RHEL support added

#### What's New?

- **New role:** `github_actions_runners` for self-hosted runners
- **RHEL 9+ support:** Docker and Podman now support RHEL/CentOS/Rocky/Alma
- **Enhanced registry authentication:** Automatic permission fixes on RHEL
- **SELinux support:** Proper context restoration

#### Upgrade Steps

```bash
# 1. Install collection
ansible-galaxy collection install code3tech.devtools:1.2.0 --force

# 2. Install dependencies
ansible-galaxy collection install -r requirements.yml

# 3. Use new features (optional)
# See: playbooks/github_actions_runners/
```

📖 **Complete guides:**
- [GitHub Actions Runners Documentation](../user-guides/github-actions-runners/)
- [RHEL Support Documentation](../user-guides/docker/02-prerequisites.md#rhel-specific-requirements)

---

### Upgrading to v1.1.0 (Azure DevOps Agents + Podman Changes)

**Impact:** 🔴 **BREAKING CHANGES** in Podman role

#### What Changed?

1. **New role:** `azure_devops_agents` for Azure Pipelines agents
2. **Podman:** Configuration files separated (BREAKING)
3. **Performance:** Optimizations for Docker and Podman

#### Critical: Podman Configuration Changes

**⚠️ WARNING:** Requires storage reset (removes containers/images/volumes)

Podman configurations were reorganized:

- **Before:** Mixed `[storage]` + `[engine]` in `storage.conf`
- **Now:** Separated into `storage.conf` + `containers.conf`

📖 **Complete guide:** [Podman v1.0 to v1.1 Upgrade](../user-guides/podman/upgrade-v1.0-to-v1.1.md)

#### Upgrade Steps

```bash
# 1. Install collection
ansible-galaxy collection install code3tech.devtools:1.1.0 --force

# 2. Run Podman playbook (applies new configuration)
ansible-playbook -i inventory.ini playbooks/podman/install-podman.yml

# 3. Reset Podman storage (REMOVES containers/images!)
ansible -i inventory.ini all -m shell \
  -a 'rm -rf /var/lib/containers/storage/* /run/containers/storage/*' \
  --become

# 4. Verify
ansible -i inventory.ini all -m shell \
  -a 'podman info' \
  --become
```

**⚠️ Impact:**
- ❌ Removes: All containers, images, volumes, networks
- ✅ Preserves: Registry auth, rootless config, Docker

---

## Role-Specific Upgrade Guides

Some roles have complex upgrade procedures. See role-specific guides:

| Role | Upgrade Guide | Impact |
|------|---------------|--------|
| **Podman** | [Podman v1.0 → v1.1](../user-guides/podman/upgrade-v1.0-to-v1.1.md) | 🔴 HIGH (storage reset) |
| **asdf** | [asdf v1.x → v2.x](../user-guides/asdf/upgrade-v1-to-v2.md) | 🔴 HIGH (variable changes) |
| **Docker** | No breaking changes | 🟢 LOW |
| **Azure DevOps Agents** | No breaking changes | 🟢 LOW |
| **GitHub Actions Runners** | No breaking changes | 🟢 LOW |
| **GitLab CI Runners** | No breaking changes | 🟢 LOW |

---

## General Upgrade Process

### Step 1: Check Current Version

```bash
ansible-galaxy collection list | grep code3tech.devtools
```

### Step 2: Review CHANGELOG

```bash
# View changes between versions
cat CHANGELOG.md
```

### Step 3: Install New Version

```bash
# Install specific version
ansible-galaxy collection install code3tech.devtools:1.4.0 --force

# Or install latest
ansible-galaxy collection install code3tech.devtools --force
```

### Step 4: Update Dependencies

```bash
# Update required collections
ansible-galaxy collection install -r requirements.yml --force
```

### Step 5: Test in Non-Production

```bash
# Test on staging/dev environment first
ansible-playbook -i staging.ini your-playbook.yml --check
```

### Step 6: Apply to Production

```bash
# After testing, apply to production
ansible-playbook -i production.ini your-playbook.yml
```

---

## Support

If you encounter problems during upgrade:

1. **Review CHANGELOG:** Check [CHANGELOG.md](../../CHANGELOG.md) for breaking changes
2. **Check role documentation:** See [roles/](../../roles/) for role-specific guides
3. **Open an issue:** https://github.com/kode3tech/ansible-col-devtools/issues
4. **Email support:** suporte@code3tech.com

---

[← Back to Maintenance Documentation](README.md)

**Current version:** v1.4.0
