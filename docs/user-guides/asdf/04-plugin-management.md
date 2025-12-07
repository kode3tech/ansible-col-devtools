# Plugin Management

Complete guide to managing asdf plugins - from lightweight binaries to compiled runtimes.

---

## 📋 Table of Contents

- [Plugin Categories](#plugin-categories)
- [Lightweight Plugins](#lightweight-plugins)
- [Heavy Plugins (Compiled)](#heavy-plugins-compiled)
- [Plugin Configuration](#plugin-configuration)
- [Installation Time Reference](#installation-time-reference)
- [Finding Plugins](#finding-plugins)
- [Version Management](#version-management)

---

## Plugin Categories

asdf plugins fall into two categories based on installation time:

| Category | Installation Time | Method | Examples |
|----------|------------------|--------|----------|
| **Lightweight** | 5-30 seconds | Download pre-built binary | direnv, jq, kubectl, terraform |
| **Heavy** | 2-30 minutes | Compile from source | nodejs, python, ruby, rust |

Understanding this distinction is crucial for planning deployments and setting appropriate timeouts.

---

## Lightweight Plugins

Lightweight plugins download pre-compiled binaries. They're fast and ideal for CI/CD and quick deployments.

### Popular Lightweight Plugins

| Plugin | Description | Installation Time | Use Case |
|--------|-------------|------------------|----------|
| **direnv** | Directory-based environment manager | ~5s | Per-project env vars |
| **jq** | JSON processor | ~5s | JSON manipulation in scripts |
| **yq** | YAML processor | ~5s | YAML manipulation in scripts |
| **kubectl** | Kubernetes CLI | ~10s | K8s cluster management |
| **helm** | Kubernetes package manager | ~10s | K8s deployments |
| **terraform** | Infrastructure as Code | ~15s | Cloud provisioning |
| **awscli** | AWS Command Line Interface | ~15s | AWS management |
| **gcloud** | Google Cloud SDK | ~30s | GCP management |
| **azure-cli** | Azure CLI | ~20s | Azure management |
| **k9s** | Kubernetes TUI | ~10s | K8s visual management |
| **lazygit** | Git TUI | ~5s | Visual Git operations |

### Lightweight Plugins Configuration

```yaml
asdf_plugins:
  # Environment management
  - name: "direnv"
    versions: ["2.35.0"]
    global: "2.35.0"
  
  # Data processing
  - name: "jq"
    versions: ["1.7.1"]
    global: "1.7.1"
  
  - name: "yq"
    versions: ["4.44.0"]
    global: "4.44.0"
  
  # Kubernetes tools
  - name: "kubectl"
    versions: ["1.31.0", "1.30.0"]
    global: "1.31.0"
  
  - name: "helm"
    versions: ["3.15.0"]
    global: "3.15.0"
  
  # Infrastructure
  - name: "terraform"
    versions: ["1.9.0", "1.8.0"]
    global: "1.9.0"
```

**Total installation time:** ~30-60 seconds

### DevOps Toolchain Example

Complete DevOps toolchain with lightweight plugins:

```yaml
---
- name: DevOps Toolchain with asdf
  hosts: all
  become: true
  
  vars:
    asdf_users:
      - devops
      - sre
    
    asdf_plugins:
      # Version control
      - name: "lazygit"
        versions: ["0.43.0"]
        global: "0.43.0"
      
      # Container tools
      - name: "kubectl"
        versions: ["1.31.0"]
        global: "1.31.0"
      
      - name: "helm"
        versions: ["3.15.0"]
        global: "3.15.0"
      
      - name: "k9s"
        versions: ["0.32.0"]
        global: "0.32.0"
      
      # Infrastructure
      - name: "terraform"
        versions: ["1.9.0"]
        global: "1.9.0"
      
      # Cloud CLIs
      - name: "awscli"
        versions: ["2.17.0"]
        global: "2.17.0"
  
  roles:
    - code3tech.devtools.asdf
```

---

## Heavy Plugins (Compiled)

Heavy plugins compile runtimes from source. They require build tools and take significantly longer.

### Popular Heavy Plugins

| Plugin | Description | Installation Time | Dependencies |
|--------|-------------|------------------|--------------|
| **nodejs** | JavaScript runtime | 3-8 min | gcc, make, python |
| **python** | Python interpreter | 2-7 min | gcc, libssl-dev, libffi-dev |
| **ruby** | Ruby interpreter | 5-15 min | gcc, make, libssl-dev |
| **golang** | Go compiler | 2-5 min | gcc (minimal) |
| **rust** | Rust toolchain | 10-30 min | gcc, make, curl |
| **erlang** | Erlang/OTP runtime | 10-20 min | gcc, libncurses, libssl |
| **elixir** | Elixir language | 2-5 min | erlang installed first |
| **java** | OpenJDK | 1-3 min | wget (downloads binary) |

### Heavy Plugins Configuration

```yaml
asdf_plugins:
  # JavaScript development
  - name: "nodejs"
    versions:
      - "22.11.0"    # Latest LTS
      - "20.18.0"    # Previous LTS
    global: "22.11.0"
  
  # Python development
  - name: "python"
    versions:
      - "3.13.0"     # Latest
      - "3.12.7"     # Stable
      - "3.11.10"    # LTS
    global: "3.13.0"
  
  # Ruby development
  - name: "ruby"
    versions:
      - "3.3.0"
      - "3.2.3"
    global: "3.3.0"
  
  # Go development
  - name: "golang"
    versions:
      - "1.23.0"
      - "1.22.0"
    global: "1.23.0"
```

**Total installation time:** ~15-40 minutes (depending on hardware)

### Development Stack Example

Full development stack with heavy plugins:

```yaml
---
- name: Full Development Stack
  hosts: all
  become: true
  
  vars:
    asdf_users:
      - developer
    
    asdf_install_dependencies: true  # Ensure build tools installed
    
    asdf_plugins:
      # Web development
      - name: "nodejs"
        versions: ["22.11.0", "20.18.0"]
        global: "22.11.0"
      
      # Backend/scripting
      - name: "python"
        versions: ["3.13.0", "3.12.7"]
        global: "3.13.0"
      
      # Infrastructure tools
      - name: "golang"
        versions: ["1.23.0"]
        global: "1.23.0"
      
      # Lightweight tools
      - name: "direnv"
        versions: ["2.35.0"]
        global: "2.35.0"
  
  roles:
    - code3tech.devtools.asdf
```

---

## Plugin Configuration

### Plugin Structure

Each plugin entry has this structure:

```yaml
asdf_plugins:
  - name: "plugin-name"      # Required: Plugin name
    versions:                 # Required: List of versions to install
      - "1.2.3"
      - "1.1.0"
    global: "1.2.3"          # Optional: Default version for all users
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | String | Yes | Plugin name (from `asdf plugin list all`) |
| `versions` | List | Yes | Versions to install |
| `global` | String | No | Global default version |

### Version Specification

```yaml
asdf_plugins:
  # Exact version
  - name: "nodejs"
    versions: ["22.11.0"]
    global: "22.11.0"
  
  # Multiple versions (for testing/compatibility)
  - name: "python"
    versions:
      - "3.13.0"   # Latest
      - "3.12.7"   # Stable
      - "3.11.10"  # LTS
    global: "3.13.0"
  
  # Pre-release versions (if plugin supports)
  - name: "rust"
    versions:
      - "stable"
      - "nightly"
    global: "stable"
```

### Without Global Version

If you don't set `global`, users must explicitly set versions:

```yaml
asdf_plugins:
  - name: "nodejs"
    versions: ["22.11.0", "20.18.0"]
    # No global - users must use `asdf local` or `.tool-versions`
```

Users then set versions per-project:

```bash
cd my-project
asdf local nodejs 20.18.0
# Creates .tool-versions file
```

---

## Installation Time Reference

### By Plugin Category

| Scenario | Time | Plugins |
|----------|------|---------|
| **asdf only** | ~10-20s | None |
| **Lightweight tools** | ~15-30s | direnv, jq, yq |
| **DevOps tools** | ~30-60s | kubectl, helm, terraform |
| **Node.js (1 version)** | ~3-8 min | nodejs |
| **Python (1 version)** | ~2-7 min | python |
| **Full dev stack** | ~15-30 min | nodejs, python, golang |
| **Complete toolchain** | ~25-45 min | nodejs, python, ruby, golang |

### Factors Affecting Time

| Factor | Impact |
|--------|--------|
| **CPU cores** | More cores = faster compilation |
| **RAM** | 4GB+ recommended for heavy plugins |
| **Storage speed** | SSD significantly faster than HDD |
| **Network speed** | Affects download phase |
| **Existing dependencies** | Pre-installed build tools save time |

### Optimization Tips

```yaml
# 1. Pre-install dependencies (done automatically if asdf_install_dependencies: true)
asdf_install_dependencies: true

# 2. Use SSD for asdf data directory
asdf_data_dir: "/ssd/asdf"

# 3. Install fewer versions
asdf_plugins:
  - name: "nodejs"
    versions: ["22.11.0"]  # Just 1 version = faster
    global: "22.11.0"

# 4. Use Java (binary download) instead of heavy compilation
asdf_plugins:
  - name: "java"
    versions: ["openjdk-21"]  # Downloads binary, no compilation
    global: "openjdk-21"
```

---

## Finding Plugins

### List All Available Plugins

```bash
# Show all 300+ available plugins
asdf plugin list all

# Search for specific plugin
asdf plugin list all | grep python
asdf plugin list all | grep node

# Count available plugins
asdf plugin list all | wc -l
```

### Plugin Repository

The official plugin repository: https://github.com/asdf-vm/asdf-plugins

Each plugin has its own repository with:
- Installation instructions
- Supported versions
- Required dependencies
- Configuration options

### Common Plugin Names

| Language/Tool | Plugin Name |
|--------------|-------------|
| Node.js | `nodejs` |
| Python | `python` |
| Ruby | `ruby` |
| Go | `golang` |
| Rust | `rust` |
| Java | `java` |
| Terraform | `terraform` |
| Kubernetes CLI | `kubectl` |
| Helm | `helm` |
| AWS CLI | `awscli` |
| PostgreSQL | `postgres` |
| Redis | `redis` |
| MongoDB | `mongodb` |

### Verify Plugin Availability

```bash
# Check if plugin exists
asdf plugin list all | grep -w "nodejs"

# Get plugin repository URL
asdf plugin list all | grep nodejs
# Output: nodejs  https://github.com/asdf-vm/asdf-nodejs.git
```

---

## Version Management

### Listing Versions

```bash
# List all available versions for a plugin
asdf list all nodejs

# List installed versions
asdf list nodejs

# Show current version
asdf current nodejs
asdf current  # All plugins
```

### Setting Versions

```bash
# Set global version (all users)
asdf global nodejs 22.11.0

# Set local version (per directory)
cd my-project
asdf local nodejs 20.18.0

# Set shell version (current session only)
asdf shell nodejs 18.20.0
```

### .tool-versions File

Projects can specify exact versions:

```bash
# .tool-versions (in project root)
nodejs 20.18.0
python 3.12.7
terraform 1.9.0
```

This file:
- Is automatically detected by asdf
- Overrides global versions in this directory
- Should be committed to version control
- Ensures reproducible environments

### Version Priority

asdf resolves versions in this order:

1. **Shell version** (`asdf shell`)
2. **Local version** (`.tool-versions` in current directory)
3. **Parent directories** (`.tool-versions` in parent directories)
4. **Global version** (`asdf global`)
5. **System version** (if plugin has `system` option)

---

## Best Practices

### 1. Start Lightweight

Begin with essential lightweight plugins:

```yaml
asdf_plugins:
  - name: "direnv"
    versions: ["2.35.0"]
    global: "2.35.0"
```

### 2. Pin Versions

Always specify exact versions:

```yaml
# ✅ Good - explicit version
versions: ["22.11.0"]

# ❌ Avoid - can cause inconsistency
versions: ["latest"]
```

### 3. Use Global Versions

Set global versions to avoid user confusion:

```yaml
asdf_plugins:
  - name: "nodejs"
    versions: ["22.11.0"]
    global: "22.11.0"  # ✅ Users get this by default
```

### 4. Document Plugin Versions

Maintain a `.tool-versions` template for projects:

```bash
# template/.tool-versions
nodejs 22.11.0
python 3.13.0
terraform 1.9.0
```

---

## Next Steps

- **[Multi-User Configuration](05-multi-user-config.md)** - Configure asdf for multiple users
- **[Production Deployment](06-production-deployment.md)** - Complete production playbooks
- **[Performance & Security](07-performance-security.md)** - Optimization and best practices

---

[← Back to asdf Documentation](README.md) | [Previous: Basic Installation](03-basic-installation.md) | [Next: Multi-User Configuration →](05-multi-user-config.md)
