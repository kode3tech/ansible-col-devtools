# Installed Versions

## Environment
- **Python**: 3.11.2 (managed via asdf)
- **Shell**: zsh
- **OS**: macOS/Linux

## Ansible Tools

| Tool | Version |
|------|--------|
| Ansible | 12.1.0 |
| Ansible Core | 2.19.3 |
| Ansible Lint | 25.9.2 |
| Molecule | 25.9.0 |
| Molecule Plugins | 25.8.12 |
| Ansible Navigator | 25.9.0 |
| Ansible Runner | 2.4.2 |
| Ansible Builder | 3.1.1 |

## Python Dependencies

| Library | Version |
|---------|--------|
| Jinja2 | 3.1.6 |
| PyYAML | 6.0.3 |
| Cryptography | 46.0.3 |
| pytest | 8.4.2 |
| pytest-testinfra | 10.2.2 |
| yamllint | 1.37.1 |
| black | 25.9.0 |
| docker (Python SDK) | 7.1.0 |

## Verification Commands

```bash
# Ansible version
ansible --version

# Ansible Lint version
ansible-lint --version

# Molecule version
molecule --version

# List all dependencies
pip list
```

## Updating

To update all dependencies:

```bash
pip install --upgrade -r requirements.txt
```

---

[← Back to Maintenance](README.md)

*Last updated: November 4, 2025*
