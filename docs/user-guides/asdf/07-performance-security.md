# Performance & Security

Optimization strategies and security best practices for asdf deployments.

---

## 📋 Table of Contents

- [Performance Optimization](#performance-optimization)
- [Storage Optimization](#storage-optimization)
- [Security Best Practices](#security-best-practices)
- [Version Pinning](#version-pinning)
- [Maintenance](#maintenance)

---

## Performance Optimization

### 1. Use SSD for Installation Directory

Place asdf on fast storage for significantly faster plugin compilation:

```yaml
# Default (on SSD)
asdf_install_dir: "/opt/asdf"

# Custom data directory (on faster SSD)
asdf_data_dir: "/fast-ssd/asdf"
```

**Expected Improvement:** 30-50% faster plugin compilation

### 2. Choose Lightweight Plugins for Testing

When testing or in CI/CD, prefer binary-download plugins:

```yaml
# ⚡ Fast (10-15 seconds total)
asdf_plugins:
  - name: "direnv"
    versions: ["2.35.0"]
    global: "2.35.0"
  - name: "jq"
    versions: ["1.7.1"]
    global: "1.7.1"

# 🐢 Slow (5-15 minutes each)
asdf_plugins:
  - name: "nodejs"
    versions: ["22.11.0"]
    global: "22.11.0"
  - name: "python"
    versions: ["3.13.0"]
    global: "3.13.0"
```

### 3. Install Only Needed Versions

Minimize installation time by installing only required versions:

```yaml
# ❌ Too many versions (slow installation)
asdf_plugins:
  - name: "python"
    versions:
      - "3.13.0"
      - "3.12.7"
      - "3.11.10"
      - "3.10.15"
      - "3.9.20"
    global: "3.13.0"

# ✅ Only what you need (fast installation)
asdf_plugins:
  - name: "python"
    versions:
      - "3.13.0"      # Latest for new projects
      - "3.12.7"      # Stable fallback
    global: "3.13.0"
```

### 4. Use .tool-versions for Per-Project

Instead of installing many versions globally, let developers install on-demand:

```bash
# In project directory
cat .tool-versions
nodejs 20.18.0
python 3.12.7

# Developers run:
asdf install
# Only installs versions they don't have locally
```

### 5. Pre-Install Dependencies

Ensure build tools are installed before heavy plugins:

```yaml
asdf_install_dependencies: true  # Role handles this automatically

# Or manually ensure before role:
pre_tasks:
  - name: Install build dependencies (Debian)
    ansible.builtin.apt:
      name:
        - build-essential
        - libssl-dev
        - libffi-dev
        - zlib1g-dev
      state: present
    when: ansible_os_family == 'Debian'
```

### Installation Time Reference

| Scenario | Time | Configuration |
|----------|------|---------------|
| asdf only | ~10-20s | No plugins |
| Lightweight tools | ~15-30s | direnv, jq, yq |
| DevOps tools | ~30-60s | kubectl, helm, terraform |
| Node.js (1 version) | ~3-8 min | nodejs 22.11.0 |
| Python (1 version) | ~2-7 min | python 3.13.0 |
| Full dev stack | ~15-30 min | nodejs, python, golang |

---

## Storage Optimization

### Disk Space Requirements

| Component | Approximate Size |
|-----------|------------------|
| asdf core | ~10 MB |
| Per plugin (metadata) | ~1-5 MB |
| Node.js per version | ~100-200 MB |
| Python per version | ~200-400 MB |
| Ruby per version | ~300-500 MB |
| Go per version | ~500 MB - 1 GB |

### Prune Unused Versions

Regularly clean up old versions:

```bash
# List all installed versions
asdf list

# Check disk usage
du -sh /opt/asdf/installs/*

# Uninstall unused version
asdf uninstall nodejs 18.0.0
asdf uninstall python 3.9.20
```

### Automated Cleanup Playbook

```yaml
---
- name: Cleanup old asdf versions
  hosts: all
  become: true
  
  vars:
    cleanup_versions:
      nodejs:
        - "18.0.0"
        - "16.0.0"
      python:
        - "3.9.20"
        - "3.8.18"
  
  tasks:
    - name: Remove old versions
      ansible.builtin.command:
        cmd: "{{ asdf_install_dir }}/bin/asdf uninstall {{ item.0.key }} {{ item.1 }}"
      loop: "{{ cleanup_versions | dict2items | subelements('value') }}"
      loop_control:
        label: "{{ item.0.key }} {{ item.1 }}"
      environment:
        ASDF_DIR: "{{ asdf_install_dir }}"
        ASDF_DATA_DIR: "{{ asdf_install_dir }}"
      ignore_errors: true
```

### Shared Storage Considerations

For NFS or shared storage:

```yaml
# Ensure data directory is on fast local storage
asdf_install_dir: "/opt/asdf"           # NFS mount OK
asdf_data_dir: "/local-ssd/asdf-data"   # Fast local storage for builds
```

---

## Security Best Practices

### 1. Limit Group Membership

Only add trusted users to the asdf group:

```yaml
# ✅ Only trusted users
asdf_users:
  - developer
  - jenkins
  - deploy

# ❌ Avoid temporary or untrusted users
# - temp-contractor
# - guest
```

### 2. Pin Specific Versions in Production

Avoid "latest" in production environments:

```yaml
# ❌ Don't use in production
asdf_version: "latest"
asdf_plugins:
  - name: "nodejs"
    versions: ["latest"]

# ✅ Pin specific versions
asdf_version: "v0.18.0"
asdf_plugins:
  - name: "nodejs"
    versions: ["22.11.0"]
    global: "22.11.0"
```

### 3. Verify Plugin Sources

Only use plugins from trusted sources:

```bash
# Check plugin source before installing
asdf plugin list all | grep nodejs
# nodejs  https://github.com/asdf-vm/asdf-nodejs.git

# Trusted sources:
# - https://github.com/asdf-vm/    (official)
# - https://github.com/asdf-community/  (community maintained)
```

**Trust levels:**
| Source | Trust Level | Examples |
|--------|-------------|----------|
| `asdf-vm/*` | Highest | nodejs, python, ruby |
| `asdf-community/*` | High | terraform, kubectl |
| Third-party verified | Medium | Check repository activity |
| Unknown | Low | Avoid in production |

### 4. Use .tool-versions for Reproducibility

Ensure consistent environments across development, CI, and production:

```bash
# In repository root
cat .tool-versions
nodejs 22.11.0
python 3.13.0
terraform 1.9.0

# All environments get exact same versions
```

### 5. Audit Installed Plugins

Regularly audit what's installed:

```bash
# List all plugins
asdf plugin list

# Check plugin versions
asdf list

# Verify plugin source
asdf plugin list --urls
```

### 6. Restrict Write Access

The default permissions are secure:

```
/opt/asdf/
├── Owner: root          # Only root can modify structure
├── Group: asdf          # Group can use, not modify core
└── Mode: 0775           # Restricted write access
```

### 7. Use Ansible Vault for Sensitive Configuration

If plugins need credentials:

```yaml
# vars/secrets.yml (encrypted with ansible-vault)
npm_token: "npm_xxx..."
pypi_token: "pypi_xxx..."
```

```yaml
# playbook.yml
vars_files:
  - vars/secrets.yml

post_tasks:
  - name: Configure npm authentication
    ansible.builtin.command:
      cmd: npm config set //registry.npmjs.org/:_authToken={{ npm_token }}
    become_user: "{{ item }}"
    loop: "{{ asdf_users }}"
    no_log: true
```

---

## Version Pinning

### Global Version Pinning

Set default versions for all users:

```yaml
asdf_plugins:
  - name: "nodejs"
    versions: ["22.11.0"]
    global: "22.11.0"     # All users get this by default
```

This creates `/opt/asdf/.tool-versions`:
```
nodejs 22.11.0
```

### Project Version Pinning

Create `.tool-versions` in project directories:

```bash
# /path/to/project/.tool-versions
nodejs 20.18.0
python 3.12.7
terraform 1.8.0
```

### Version Lock File

For reproducible CI/CD, commit `.tool-versions`:

```bash
# Add to git
git add .tool-versions
git commit -m "chore: pin tool versions"

# CI/CD installs exact versions
asdf install
```

### Version Resolution

asdf resolves versions in this priority:

```
1. ASDF_*_VERSION environment variable
2. .tool-versions in current directory
3. .tool-versions in parent directories
4. .tool-versions in home directory
5. Global version (asdf global)
6. System version
```

---

## Maintenance

### Regular Updates

Keep asdf and plugins updated:

```bash
# Update asdf core
asdf update

# Update all plugins
asdf plugin update --all

# Update specific plugin
asdf plugin update nodejs
```

### Automated Update Playbook

```yaml
---
- name: Update asdf and plugins
  hosts: all
  become: true
  
  tasks:
    - name: Update asdf core
      ansible.builtin.command:
        cmd: "{{ asdf_install_dir }}/bin/asdf update"
      environment:
        ASDF_DIR: "{{ asdf_install_dir }}"
        ASDF_DATA_DIR: "{{ asdf_install_dir }}"
      changed_when: true
    
    - name: Update all plugins
      ansible.builtin.command:
        cmd: "{{ asdf_install_dir }}/bin/asdf plugin update --all"
      environment:
        ASDF_DIR: "{{ asdf_install_dir }}"
        ASDF_DATA_DIR: "{{ asdf_install_dir }}"
      changed_when: true
```

### Health Check Playbook

```yaml
---
- name: asdf Health Check
  hosts: all
  become: true
  
  tasks:
    - name: Check asdf version
      ansible.builtin.command: "{{ asdf_install_dir }}/bin/asdf --version"
      register: asdf_version
      changed_when: false
    
    - name: List installed plugins
      ansible.builtin.command: "{{ asdf_install_dir }}/bin/asdf plugin list"
      register: plugins
      environment:
        ASDF_DIR: "{{ asdf_install_dir }}"
        ASDF_DATA_DIR: "{{ asdf_install_dir }}"
      changed_when: false
    
    - name: Check disk usage
      ansible.builtin.command: "du -sh {{ asdf_install_dir }}"
      register: disk_usage
      changed_when: false
    
    - name: Display health report
      ansible.builtin.debug:
        msg: |
          ═══════════════════════════════════════
          ASDF HEALTH REPORT
          ═══════════════════════════════════════
          Version: {{ asdf_version.stdout }}
          Disk Usage: {{ disk_usage.stdout }}
          
          Installed Plugins:
          {{ plugins.stdout }}
          ═══════════════════════════════════════
```

### Backup Strategy

Backup installed versions for disaster recovery:

```bash
# Create backup
tar -czf asdf-backup-$(date +%Y%m%d).tar.gz /opt/asdf

# Restore
tar -xzf asdf-backup-20240101.tar.gz -C /
```

### Migration Between Servers

Transfer asdf installation:

```bash
# On source server
tar -czf asdf-full.tar.gz /opt/asdf

# Transfer
scp asdf-full.tar.gz target-server:/tmp/

# On target server
tar -xzf /tmp/asdf-full.tar.gz -C /
# Re-run role to configure users and permissions
```

---

## Performance Checklist

- [ ] asdf installed on SSD storage
- [ ] Only necessary plugin versions installed
- [ ] Build dependencies pre-installed
- [ ] Lightweight plugins used for testing/CI
- [ ] Unused versions pruned regularly
- [ ] .tool-versions used for project-specific versions

## Security Checklist

- [ ] Only trusted users in asdf group
- [ ] Specific versions pinned (no "latest" in production)
- [ ] Plugins from trusted sources only
- [ ] .tool-versions committed to repositories
- [ ] Regular plugin audits scheduled
- [ ] Credentials managed with Ansible Vault

---

## Next Steps

- **[Troubleshooting](08-troubleshooting.md)** - Common issues and solutions
- **[Plugin Management](04-plugin-management.md)** - Detailed plugin configuration

---

[← Back to asdf Documentation](README.md) | [Previous: Production Deployment](06-production-deployment.md) | [Next: Troubleshooting →](08-troubleshooting.md)
