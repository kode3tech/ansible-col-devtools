# Ansible Role: asdf

Ansible role for installing and configuring **asdf** - the extendable version manager for multiple runtime versions.

📖 **Complete Guide:** [asdf Complete Guide](../../docs/user-guides/ASDF_COMPLETE_GUIDE.md) - Comprehensive documentation with architecture, performance optimization, and troubleshooting.

## 📋 Table of Contents

- [Features](#-features)
- [Requirements](#-requirements)
- [Role Variables](#-role-variables)
- [Dependencies](#-dependencies)
- [Example Playbooks](#-example-playbooks)
- [Plugin Recommendations](#-plugin-recommendations)
- [Performance Considerations](#-performance-considerations)
- [Troubleshooting](#-troubleshooting)
- [Testing](#-testing)
- [License](#-license)
- [Author Information](#-author-information)

## 🎯 Features

- ✅ **Binary installation** - Fast, reliable installation from official releases
- ✅ **Multi-distribution support** - Ubuntu 22+, Debian 11+, RHEL/Rocky 9+
- ✅ **Centralized plugin management** - Configure plugins once for all users
- ✅ **Group-based permissions** - Uses `asdf` group for shared access
- ✅ **Multi-user support** - No permission conflicts between users
- ✅ **System-wide PATH** - Available in `/etc/profile.d/asdf.sh`
- ✅ **User validation** - Validates users exist before configuration
- ✅ **Shell configuration** - Automatic setup for bash, zsh, and fish
- ✅ **Internet connectivity check** - Graceful handling of offline environments
- ✅ **RedHat optimizations** - Handles curl-minimal conflicts and DNF cache
- ✅ **Simplified variables** - Clean, easy-to-understand configuration

## 📋 Requirements

- Ansible >= 2.15
- Target system: Ubuntu 22.04+, Debian 11+, or RHEL 9+
- Root or sudo privileges on target hosts
- Internet connection for downloading asdf binary and plugins

### Supported Distributions

| Distribution | Versions | Status |
|--------------|----------|--------|
| **Ubuntu** | 22.04 (Jammy), 24.04 (Noble), 25.04 (Plucky) | ✅ Tested |
| **Debian** | 11 (Bullseye), 12 (Bookworm), 13 (Trixie) | ✅ Tested |
| **RHEL/Rocky/Alma** | 9, 10 | ✅ Tested |

## 🔧 Role Variables

### 🎯 **NEW: Simplified Group-Based Architecture**

**This role now uses a centralized approach with group-based permissions - NO MORE per-user complexity!**

```yaml
# ✅ NEW: Simple centralized configuration
asdf_plugins:
  - name: "nodejs"
    versions: ["20.11.0"]
    global: "20.11.0"

asdf_users:
  - "user1"  # Simple username list
  - "user2"  # All users get same plugins
```

**Key improvements:**
- ✅ **Centralized plugins** - Configure once, applies to all users
- ✅ **Group permissions** - Users added to `asdf` group for shared access
- ✅ **System-wide installation** - Plugins installed once in `/opt/asdf`
- ✅ **Multi-user support** - No more permission conflicts between users
- ✅ **Simplified variables** - Just usernames, no complex per-user structures

### Basic Configuration

```yaml
# asdf version to install (latest by default)
# Use release tag like 'v0.18.0' or 'latest'
asdf_version: "latest"

# asdf installation directory
asdf_install_dir: "/opt/asdf"

# Install system dependencies required by asdf plugins
asdf_install_dependencies: true

# Configure shell profiles automatically
asdf_configure_shell: true
```

### User and Plugin Configuration

```yaml
# Centralized plugin configuration (applies to all users)
asdf_plugins:
  - name: "nodejs"
    versions:
      - "20.11.0"
      - "18.19.0"
    global: "20.11.0"
  - name: "python"
    versions:
      - "3.12.1"
    global: "3.12.1"

# Simple user list (users must exist on system)
asdf_users:
  - "developer"
  - "jenkins"
  - "deploy"

# Shell configuration (applies to all users)
asdf_shell_profile: "bashrc"  # bashrc, zshrc, or config/fish/config.fish
```

### Advanced Configuration

```yaml
# Custom data directory (optional)
# Default: uses asdf_install_dir
asdf_data_dir: ""

# asdf binary download URL
asdf_binary_url: "https://github.com/asdf-vm/asdf/releases/download"

# Shell profile files by shell type
asdf_shell_profiles:
  bash: ".bashrc"
  zsh: ".zshrc"
  fish: ".config/fish/config.fish"
```

## 📦 Dependencies

None.

## 🚀 Example Playbooks

### Basic Installation (No Plugins)

```yaml
- hosts: servers
  become: true
  roles:
    - kode3tech.devtools.asdf
```

### Quick Testing with Lightweight Plugins (⚡ Fast ~15 seconds)

```yaml
- hosts: servers
  become: true
  vars:
    asdf_plugins:
      # Lightweight plugins - no compilation needed
      - name: "direnv"
        versions:
          - "2.32.3"
        global: "2.32.3"
      - name: "jq"
        versions:
          - "1.7.1"
        global: "1.7.1"
    
    asdf_users:
      - "{{ ansible_user }}"
  
  roles:
    - kode3tech.devtools.asdf
```

### Development Environment with Node.js and Python (🐢 Slower ~5-15 min)

```yaml
- hosts: developers
  become: true
  vars:
    asdf_plugins:
      - name: "nodejs"
        versions:
          - "20.11.0"
          - "18.19.0"
        global: "20.11.0"
      - name: "python"
        versions:
          - "3.12.1"
          - "3.11.7"
        global: "3.12.1"
    
    asdf_users:
      - "devuser"
    
    asdf_shell_profile: "bashrc"  # or "zshrc"
  
  roles:
    - kode3tech.devtools.asdf
```

### Multi-User Configuration

```yaml
- hosts: servers
  become: true
  vars:
    # All users get the same plugins (centralized)
    asdf_plugins:
      - name: "nodejs"
        versions: ["20.11.0"]
        global: "20.11.0"
      - name: "python"
        versions: ["3.12.1"]
        global: "3.12.1"
      - name: "terraform"
        versions: ["1.6.0"]
        global: "1.6.0"
    
    # Simple user list
    asdf_users:
      - "frontend"
      - "backend"
      - "devops"
    
    # Shell configuration applies to all users
    asdf_shell_profile: "bashrc"  # All users get same shell config
  
  roles:
    - kode3tech.devtools.asdf
```

## 🎨 Plugin Recommendations

### Lightweight Plugins (Fast Installation)

Perfect for testing and CI/CD:

| Plugin | Installation Time | Description |
|--------|------------------|-------------|
| **direnv** | ~5-10 seconds | Environment variable manager |
| **jq** | ~3-5 seconds | JSON processor |
| **yq** | ~3-5 seconds | YAML processor |
| **kubectl** | ~5-10 seconds | Kubernetes CLI |
| **helm** | ~5-10 seconds | Kubernetes package manager |

### Heavy Plugins (Requires Compilation)

For production environments:

| Plugin | Installation Time | Description |
|--------|------------------|-------------|
| **nodejs** | ~3-8 minutes | JavaScript runtime |
| **python** | ~2-7 minutes | Python interpreter |
| **ruby** | ~5-15 minutes | Ruby interpreter |
| **golang** | ~2-5 minutes | Go compiler |
| **rust** | ~10-30 minutes | Rust toolchain |

## 🔍 Features in Detail

### 1. Centralized Plugin Management

Plugins are installed once in `/opt/asdf` and shared among all users:

```yaml
# ✅ NEW: Centralized approach
asdf_plugins:
  - name: "nodejs"
    versions: ["20.11.0"]
    global: "20.11.0"

asdf_users:
  - "user1"  # Gets nodejs 20.11.0
  - "user2"  # Also gets nodejs 20.11.0
```

### 2. Group-Based Permissions

Users are added to the `asdf` group for shared access to the installation:

```bash
# Automatic group creation and user assignment
sudo groupadd asdf
sudo usermod -aG asdf user1
sudo usermod -aG asdf user2

# Directory permissions
chown -R root:asdf /opt/asdf
chmod -R 775 /opt/asdf
```

### 2. Internet Connectivity Check
### 3. RedHat Optimizations

Special handling for RedHat-based systems:

- **curl-minimal conflict**: Automatically replaces curl-minimal with full curl
- **DNF cache management**: Cleans and refreshes cache before operations
- **PATH configuration**: Ensures `/usr/local/bin` is in system PATH

### 4. Shell Configuration

Automatic shell profile configuration for:

- **bash**: `.bashrc`
- **zsh**: `.zshrc` (with completions and fpath)
- **fish**: `.config/fish/config.fish`

Each shell gets appropriate configuration with:
- asdf binary in PATH
- Shims directory in PATH
- Custom data directory (if configured)
- Shell-specific completions

### 5. Idempotency

The role is fully idempotent:

- ✅ Binary version checking (updates only if needed)
- ✅ Plugin installation (skips if already added)
- ✅ Version installation (skips if already installed)
- ✅ Global version setting (compares before setting)

## 🧪 Testing

This role includes comprehensive Molecule tests for the **new v2.0 centralized architecture**:

```bash
cd roles/asdf
molecule test
```

### Test Platforms

- **Ubuntu 22.04** (geerlingguy/docker-ubuntu2204-ansible)
- **Debian 12** (geerlingguy/docker-debian12-ansible)  
- **Rocky Linux 9** (geerlingguy/docker-rockylinux9-ansible)

### Test Coverage

#### Ansible Tests (verify.yml)
✅ **Basic Installation**
- Binary installation verification
- Directory structure and permissions
- Version command functionality

✅ **Group-Based Architecture**
- `asdf` group creation and user assignment
- Group-based file permissions (0775)
- Multi-user access validation

✅ **System-Wide Configuration**
- `/etc/profile.d/asdf.sh` script creation
- Correct PATH configuration
- Global availability verification

✅ **Centralized Plugin Management**
- Plugin installation in shared location
- Version installation and management
- Global version configuration

✅ **User Shell Configuration**
- Individual user `.bashrc` setup
- Ansible managed block verification
- Path and environment variables

✅ **Shims and Functionality**
- Shim creation and execution
- Functional command testing
- Binary vs git installation verification

#### Python Tests (test_default.py)
✅ **Infrastructure Tests**
- File system permissions and ownership
- Directory structure validation
- Executable bit verification

✅ **Integration Tests**
- Group membership verification
- System-wide PATH configuration
- Plugin functionality testing

### Test Plugin

Tests use **direnv 2.32.3** - a lightweight plugin perfect for testing:
- ⚡ **Fast installation** (~5-10 seconds)
- 🪶 **Minimal dependencies** (shell script only)
- 🔧 **Real functionality** (environment management)
- ✅ **Cross-platform** (works on all test platforms)

### Running Specific Tests

```bash
# Full test suite
molecule test

# Syntax check only
molecule syntax

# Converge only (apply role)
molecule converge

# Verify only (run tests)
molecule verify

# Test on specific platform
molecule test --scenario-name default -- --limit ubuntu2204
```

### Test Architecture Validation

The tests specifically validate the **v2.0 centralized approach**:

1. **No per-user complexity** - Simple configuration structure
2. **Group-based permissions** - Shared access without conflicts  
3. **Centralized plugins** - Single installation point
4. **System-wide availability** - Global PATH configuration
5. **Binary installation** - Fast, reliable installation method

## 📊 Performance

### Installation Times

| Scenario | Time | Details |
|----------|------|---------|
| **asdf binary only** | ~10-20 seconds | No plugins |
| **+ lightweight plugins** | ~15-30 seconds | direnv, jq |
| **+ nodejs (1 version)** | ~3-8 minutes | Includes compilation |
| **+ python (1 version)** | ~2-7 minutes | Includes compilation |
| **Full stack** | ~5-15 minutes | nodejs + python |

### Tips for Fast Testing

1. Use lightweight plugins (direnv, jq) for testing
2. Use heavy plugins (nodejs, python) only in production
3. Enable offline mode if plugins are pre-installed
4. Use binary installation (default)

## 🔧 Troubleshooting

### Plugin Installation Issues

If plugins fail to install, ensure:

1. Internet connectivity is available
2. The plugin repository is accessible
3. Required system dependencies are installed

```yaml
# Example with proper dependencies
asdf_install_dependencies: true
```

### curl-minimal Conflicts (RedHat)

The role automatically handles this:

```bash
# Automatically done by the role:
# 1. dnf clean all
# 2. Replace curl-minimal with curl (allowerasing=true)
# 3. Install system dependencies
```

### Plugin Installation Fails

```bash
# Check asdf version
asdf --version

# List available plugins
asdf plugin list all

# Install plugin manually
asdf plugin add <plugin-name>
asdf install <plugin-name> <version>
```

### Global Version Not Set

The role uses `asdf set <plugin> <version>` (asdf v0.16.0+):

```bash
# Check current version
asdf current <plugin>

# Set manually if needed
asdf set <plugin> <version>
```

## 📚 Additional Resources

- [asdf Official Documentation](https://asdf-vm.com/)
- [asdf GitHub Repository](https://github.com/asdf-vm/asdf)
- [Available Plugins](https://github.com/asdf-vm/asdf-plugins)

## 📝 Example Playbooks Directory

See complete examples in `playbooks/asdf/`:

- `install-asdf.yml` - Basic installation
- `install-asdf-basic.yml` - Lightweight plugins (recommended for testing)
- `install-asdf-full.yml` - Heavy plugins (nodejs, python)
- `setup-nodejs-python.yml` - Development environment
- `setup-multi-user.yml` - Multiple users configuration
- `setup-multi-shell.yml` - Multiple shells (bash, zsh, fish)
## 🔐 Security Considerations

- Role requires root/sudo privileges
- Downloads from official asdf GitHub releases
- Verifies binary versions before installation
- No secrets in variables (use Ansible Vault for sensitive data)

## 📄 License

MIT

## ✍️ Author Information

This role was created by the **Kode3Tech DevOps Team**.

- GitHub: [kode3tech](https://github.com/kode3tech)
- Email: suporte@kode3.tech
- Website: [kode3.tech](https://kode3.tech)

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](../../CONTRIBUTING.md) for details.

## 📋 Changelog

See [CHANGELOG.md](../../CHANGELOG.md) for version history.
