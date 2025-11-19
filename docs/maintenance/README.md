# 🔄 Maintenance Documentation

Documentation for maintaining and upgrading the code3tech.devtools collection.

## 📋 Available Guides

### [Upgrade Guide](UPGRADE_GUIDE.md)
Instructions for upgrading between collection versions.
- Breaking changes
- Migration steps
- Compatibility notes
- Version-specific instructions

### [Version Information](VERSIONS.md)
Current versions of tools and dependencies.
- Ansible version
- Python version
- Ansible-lint version
- Molecule version
- Other dependencies

---

## 🎯 Upgrading

### Check Current Version
```bash
ansible-galaxy collection list | grep code3tech
```

### Upgrade to Latest
```bash
ansible-galaxy collection install code3tech.devtools --upgrade
```

### Review Changes
Always check [CHANGELOG.md](../../CHANGELOG.md) before upgrading.

---

## 📊 Version Matrix

See [Version Information](VERSIONS.md) for the complete version matrix and compatibility information.

---

[← Back to Documentation Index](../README.md)
