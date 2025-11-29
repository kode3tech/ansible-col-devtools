# asdf Example Playbooks

This directory contains example playbooks demonstrating how to use the `asdf` role from the `code3tech.devtools` collection.

📖 **Complete Guide:** [asdf Complete Guide](../../docs/user-guides/ASDF_COMPLETE_GUIDE.md) - Comprehensive documentation with architecture, performance optimization, and troubleshooting.

## Available Examples

### Quick Testing (Lightweight Plugins)

#### 1. [install-asdf-basic.yml](install-asdf-basic.yml) ⚡ **RECOMMENDED FOR TESTING**
Install asdf with lightweight plugins (direnv, jq, yq) - **Fast installation (~15-30 seconds)**

**Use case**: Quick tests, CI/CD pipelines, validation

**Plugins**:
- `direnv` - Shell environment manager (shell script only)
- `jq` - JSON processor (pre-compiled binary)
- `yq` - YAML processor (pre-compiled binary)

**Installation time**: ~15-30 seconds total

```bash
ansible-playbook -i inventory playbooks/asdf/install-asdf-basic.yml
```

### Production (Heavy Plugins)

#### 2. [install-asdf-full.yml](install-asdf-full.yml) 🐢 **FOR PRODUCTION**
Install asdf with Node.js and Python - **Requires compilation (~5-15 minutes)**

**Use case**: Development servers, production environments

**Plugins**:
- `nodejs` - JavaScript runtime (requires compilation)
- `python` - Programming language (requires compilation)

**Installation time**: ~5-15 minutes total

```bash
ansible-playbook -i inventory playbooks/asdf/install-asdf-full.yml
```

### Basic Installation

#### 3. [install-asdf.yml](install-asdf.yml)
Basic asdf installation without any plugins.

**Use case**: Initial asdf setup on a server.

```bash
ansible-playbook -i inventory playbooks/asdf/install-asdf.yml
```

### Advanced Examples

#### 4. [setup-nodejs-python.yml](setup-nodejs-python.yml)
Install asdf with Node.js and Python plugins for development users.

**Use case**: Development server with multiple language versions.

```bash
ansible-playbook -i inventory playbooks/asdf/setup-nodejs-python.yml
```

#### 5. [setup-multi-user.yml](setup-multi-user.yml)
Configure asdf for multiple users with different plugin requirements.

**Use case**: Shared development environment with different team needs.

```bash
ansible-playbook -i inventory playbooks/asdf/setup-multi-user.yml
```

#### 6. [setup-multi-shell.yml](setup-multi-shell.yml)
Configure asdf for users with different shells (bash, zsh, fish) and custom data directory.

**Use case**: Multi-user environment with different shell preferences.

**Features**:
- Bash, ZSH, and Fish shell configuration
- Custom asdf data directory
- Shell-specific completions
- Different plugins per user

```bash
ansible-playbook -i inventory playbooks/asdf/setup-multi-shell.yml
```

## Usage

All playbooks assume you have:

1. A valid Ansible inventory file
2. Proper SSH access to target hosts
3. Sudo privileges on target hosts
4. The `kode3tech.devtools` collection installed

### Installing the Collection

```bash
ansible-galaxy collection install kode3tech.devtools
```

### Running Playbooks

```bash
# Basic syntax
ansible-playbook -i <inventory> playbooks/asdf/<playbook>.yml

# With custom variables
ansible-playbook -i <inventory> playbooks/asdf/<playbook>.yml -e "asdf_version=v0.13.1"

# With vault (for sensitive data)
ansible-playbook -i <inventory> playbooks/asdf/<playbook>.yml --ask-vault-pass
```

## Customization

You can customize these playbooks by:

1. **Modifying variables** in the playbook
2. **Creating variable files** and including them
3. **Using Ansible Vault** for sensitive data
4. **Combining with other roles** from the collection

## Related Documentation

- [asdf Complete Guide](../../docs/user-guides/ASDF_COMPLETE_GUIDE.md) - Comprehensive documentation
- [asdf Role README](../../roles/asdf/README.md) - Role reference
- [Collection README](../../README.md) - Main collection documentation
- [asdf Official Documentation](https://asdf-vm.com/) - asdf project documentation

## Support

For issues or questions:
- GitHub Issues: https://github.com/kode3tech/ansible-col-devtools/issues
- Email: suporte@kode3.tech
