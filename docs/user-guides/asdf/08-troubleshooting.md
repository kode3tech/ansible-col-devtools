# Troubleshooting

Common issues, diagnostic commands, and solutions for asdf deployments.

---

## 📋 Table of Contents

- [Diagnostic Commands](#diagnostic-commands)
- [Common Errors](#common-errors)
- [Shell Configuration Issues](#shell-configuration-issues)
- [Plugin Issues](#plugin-issues)
- [Permission Issues](#permission-issues)
- [Build Failures](#build-failures)
- [Complete Variable Reference](#complete-variable-reference)
- [FAQ](#faq)

---

## Diagnostic Commands

### Quick Health Check

```bash
# Check asdf installation
asdf --version

# Verify PATH configuration
echo $PATH | tr ':' '\n' | grep asdf

# Check environment variables
env | grep ASDF

# List installed plugins
asdf plugin list

# Show all installed versions
asdf list

# Check current versions
asdf current
```

### Detailed Diagnostics

```bash
# Check asdf directory structure
ls -la /opt/asdf/

# Verify group membership
getent group asdf

# Check user groups
groups $(whoami)

# Verify file permissions
ls -la /opt/asdf/bin/
ls -la /opt/asdf/shims/

# Check shell configuration
grep -r "ASDF" ~/.bashrc ~/.zshrc 2>/dev/null
```

### Plugin Diagnostics

```bash
# Show plugin location
asdf where nodejs

# Check plugin source
asdf plugin list --urls

# List available versions
asdf list all nodejs | tail -20

# Reshim to fix shim issues
asdf reshim
```

---

## Common Errors

### Error: Command Not Found

```
bash: node: command not found
```

**Cause:** Shell not configured or PATH not updated.

**Solutions:**

1. **Reload shell configuration:**
   ```bash
   source ~/.bashrc   # or ~/.zshrc
   ```

2. **Verify PATH includes asdf:**
   ```bash
   echo $PATH | grep asdf
   # Should show: /opt/asdf/shims:/opt/asdf/bin
   ```

3. **Manual PATH fix:**
   ```bash
   export PATH="/opt/asdf/shims:/opt/asdf/bin:$PATH"
   ```

4. **Re-run role with shell configuration:**
   ```yaml
   asdf_configure_shell: true
   asdf_shell_profile: "bashrc"
   ```

---

### Error: Permission Denied

```
Permission denied: /opt/asdf/plugins/nodejs
```

**Cause:** User not in asdf group.

**Solutions:**

1. **Add user to asdf group:**
   ```bash
   sudo usermod -aG asdf $(whoami)
   ```

2. **Apply group immediately:**
   ```bash
   newgrp asdf
   ```

3. **Or log out and back in**

4. **Verify group membership:**
   ```bash
   groups
   # Should show: ... asdf ...
   ```

5. **Fix via role:**
   ```yaml
   asdf_users:
     - myuser
   ```

---

### Error: Plugin Not Found

```
No such plugin: my-plugin
asdf plugin add failed
```

**Cause:** Plugin name incorrect or not in registry.

**Solutions:**

1. **Search for correct plugin name:**
   ```bash
   asdf plugin list all | grep -i python
   asdf plugin list all | grep -i node
   ```

2. **Check exact name:**
   ```bash
   # Some common names that differ:
   # nodejs (not node)
   # golang (not go)
   # python (not python3)
   ```

3. **Manually add from URL:**
   ```bash
   asdf plugin add custom-plugin https://github.com/user/asdf-custom-plugin.git
   ```

---

### Error: Version Not Found

```
version 99.99.99 is not installed for nodejs
```

**Cause:** Requested version doesn't exist or isn't installed.

**Solutions:**

1. **List available versions:**
   ```bash
   asdf list all nodejs
   ```

2. **Install the version:**
   ```bash
   asdf install nodejs 22.11.0
   ```

3. **Check installed versions:**
   ```bash
   asdf list nodejs
   ```

4. **Use valid version in configuration:**
   ```yaml
   asdf_plugins:
     - name: "nodejs"
       versions: ["22.11.0"]  # Use version from `asdf list all nodejs`
       global: "22.11.0"
   ```

---

### Error: Build Failed

```
BUILD FAILED: missing dependency
configure: error: C compiler cannot create executables
```

**Cause:** Missing system build dependencies.

**Solutions:**

1. **Enable dependency installation:**
   ```yaml
   asdf_install_dependencies: true
   ```

2. **Manually install dependencies:**

   **Debian/Ubuntu:**
   ```bash
   sudo apt update
   sudo apt install -y build-essential libssl-dev libffi-dev \
     zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev \
     libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev liblzma-dev
   ```

   **RHEL/Rocky:**
   ```bash
   sudo dnf groupinstall -y "Development Tools"
   sudo dnf install -y openssl-devel bzip2-devel libffi-devel \
     zlib-devel readline-devel sqlite-devel xz-devel
   ```

3. **Check specific plugin requirements:**
   ```bash
   # Visit plugin repository for requirements
   # Example: https://github.com/asdf-vm/asdf-nodejs
   ```

---

### Error: Shim Not Working

```
node: command not found (but asdf shows it installed)
```

**Cause:** Shims not regenerated after installation.

**Solutions:**

1. **Reshim specific plugin:**
   ```bash
   asdf reshim nodejs
   ```

2. **Reshim all plugins:**
   ```bash
   asdf reshim
   ```

3. **Verify shim exists:**
   ```bash
   ls -la /opt/asdf/shims/node
   ```

4. **Check shim content:**
   ```bash
   cat /opt/asdf/shims/node
   # Should be a script that delegates to asdf
   ```

---

### Error: Old asdf Syntax

```
asdf: command 'global' is not known
```

**Cause:** Using old command syntax with new asdf version (v0.16.0+).

**Solutions:**

1. **Update command syntax:**
   ```bash
   # Old syntax (pre v0.16.0)
   asdf global nodejs 22.11.0
   
   # New syntax (v0.16.0+)
   asdf set -g nodejs 22.11.0
   
   # Both still work, but 'set' is preferred
   ```

2. **Check asdf version:**
   ```bash
   asdf --version
   ```

3. **Update asdf:**
   ```bash
   asdf update
   ```

---

## Shell Configuration Issues

### Shell Configuration Not Applied

**Symptoms:**
- asdf commands work with full path but not directly
- PATH doesn't include asdf directories

**Diagnosis:**
```bash
# Check if configuration exists
grep "ASDF" ~/.bashrc

# Check what's in profile
cat ~/.bashrc | grep -A5 "asdf configuration"
```

**Solutions:**

1. **Verify shell profile setting:**
   ```yaml
   asdf_shell_profile: "bashrc"   # For bash
   asdf_shell_profile: "zshrc"    # For zsh
   ```

2. **Manually add configuration:**
   ```bash
   # Add to ~/.bashrc or ~/.zshrc
   export ASDF_DIR="/opt/asdf"
   export ASDF_DATA_DIR="/opt/asdf"
   export PATH="$ASDF_DIR/bin:$ASDF_DIR/shims:$PATH"
   ```

3. **For fish shell:**
   ```fish
   # Add to ~/.config/fish/config.fish
   set -gx ASDF_DIR "/opt/asdf"
   set -gx ASDF_DATA_DIR "/opt/asdf"
   set -gx PATH "$ASDF_DIR/bin" "$ASDF_DIR/shims" $PATH
   ```

### Non-Interactive Shells (CI/CD)

**Symptoms:**
- asdf works in interactive shell but not in CI/CD
- Scripts can't find asdf commands

**Solutions:**

1. **Source profile in scripts:**
   ```bash
   #!/bin/bash
   source ~/.bashrc
   node --version
   ```

2. **Set environment explicitly:**
   ```bash
   export ASDF_DIR="/opt/asdf"
   export ASDF_DATA_DIR="/opt/asdf"
   export PATH="$ASDF_DIR/bin:$ASDF_DIR/shims:$PATH"
   ```

3. **For Jenkins:**
   ```groovy
   environment {
       ASDF_DIR = '/opt/asdf'
       ASDF_DATA_DIR = '/opt/asdf'
       PATH = "${ASDF_DIR}/bin:${ASDF_DIR}/shims:${PATH}"
   }
   ```

---

## Plugin Issues

### Plugin Installation Stuck

**Symptoms:**
- Plugin installation hangs
- No output during installation

**Solutions:**

1. **Check internet connectivity:**
   ```bash
   curl -I https://github.com
   curl -I https://nodejs.org
   ```

2. **Check DNS resolution:**
   ```bash
   nslookup github.com
   ```

3. **Try with verbose output:**
   ```bash
   asdf plugin add nodejs 2>&1 | tee plugin-install.log
   ```

### Plugin Update Failed

**Solutions:**

1. **Update specific plugin:**
   ```bash
   asdf plugin update nodejs
   ```

2. **Remove and re-add plugin:**
   ```bash
   asdf plugin remove nodejs
   asdf plugin add nodejs
   asdf install nodejs 22.11.0
   ```

---

## Permission Issues

### Fix Directory Permissions

```bash
# Reset ownership
sudo chown -R root:asdf /opt/asdf

# Reset permissions
sudo chmod -R 0775 /opt/asdf

# Ensure group write on specific dirs
sudo chmod -R g+w /opt/asdf/plugins
sudo chmod -R g+w /opt/asdf/installs
sudo chmod -R g+w /opt/asdf/shims
```

### Check File Permissions

```bash
# Correct permissions should look like:
ls -la /opt/asdf/
# drwxrwxr-x root asdf ...

ls -la /opt/asdf/shims/
# -rwxrwxr-x root asdf ... node
```

---

## Build Failures

### Node.js Build Failure

```bash
# Ensure nodejs plugin dependencies
sudo apt install -y python3 g++ make

# Or on RHEL
sudo dnf install -y python3 gcc-c++ make
```

### Python Build Failure

```bash
# Full Python build dependencies (Debian/Ubuntu)
sudo apt install -y \
    build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev curl \
    libncursesw5-dev xz-utils tk-dev libxml2-dev \
    libxmlsec1-dev libffi-dev liblzma-dev

# RHEL/Rocky
sudo dnf install -y \
    gcc make openssl-devel bzip2-devel libffi-devel \
    zlib-devel readline-devel sqlite-devel xz-devel
```

### Ruby Build Failure

```bash
# Ruby build dependencies (Debian/Ubuntu)
sudo apt install -y \
    autoconf bison build-essential libssl-dev \
    libyaml-dev libreadline-dev zlib1g-dev \
    libncurses5-dev libffi-dev libgdbm-dev
```

---

## Complete Variable Reference

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `asdf_version` | String | `"latest"` | asdf version to install |
| `asdf_install_dir` | String | `"/opt/asdf"` | Installation directory |
| `asdf_data_dir` | String | `""` | Custom data directory |
| `asdf_install_dependencies` | Boolean | `true` | Install build tools |
| `asdf_configure_shell` | Boolean | `true` | Configure user shells |
| `asdf_shell_profile` | String | `"bashrc"` | Shell profile to configure |
| `asdf_users` | List | `[]` | Users to add to asdf group |
| `asdf_plugins` | List | `[]` | Plugins to install |

### Plugin Structure

```yaml
asdf_plugins:
  - name: "plugin-name"      # Required
    versions:                 # Required
      - "1.2.3"
    global: "1.2.3"          # Optional
```

### Shell Profile Values

| Value | File | Shell |
|-------|------|-------|
| `bashrc` | `~/.bashrc` | Bash |
| `zshrc` | `~/.zshrc` | Zsh |
| `config/fish/config.fish` | `~/.config/fish/config.fish` | Fish |

---

## FAQ

### Q: How do I update asdf?

```bash
asdf update
```

### Q: How do I update all plugins?

```bash
asdf plugin update --all
```

### Q: How do I list all available plugins?

```bash
asdf plugin list all
```

### Q: How do I see available versions for a plugin?

```bash
asdf list all nodejs
asdf list all python
```

### Q: How do I switch between versions?

```bash
# Global (all users)
asdf global nodejs 20.18.0

# Local (current directory)
asdf local nodejs 20.18.0

# Shell (current session)
asdf shell nodejs 20.18.0
```

### Q: How do I uninstall a version?

```bash
asdf uninstall nodejs 18.0.0
```

### Q: How do I remove a plugin?

```bash
asdf plugin remove nodejs
```

### Q: Where are versions installed?

```bash
/opt/asdf/installs/<plugin>/<version>/
# Example: /opt/asdf/installs/nodejs/22.11.0/
```

### Q: How do I check disk usage?

```bash
du -sh /opt/asdf/
du -sh /opt/asdf/installs/*
```

### Q: Why is installation slow?

Heavy plugins (nodejs, python, ruby) compile from source. Use lightweight plugins for faster installation or consider pre-built binaries when available.

### Q: Can multiple users share installations?

Yes! The role uses group-based architecture. All users in the `asdf` group share the same plugins and versions.

---

## Getting Help

### Resources

- [asdf Official Documentation](https://asdf-vm.com/)
- [asdf GitHub Issues](https://github.com/asdf-vm/asdf/issues)
- [Plugin-specific Documentation](https://github.com/asdf-vm/asdf-plugins)

### Useful Commands

```bash
# Show asdf help
asdf help

# Show plugin help
asdf help nodejs

# Check asdf info
asdf info
```

### Collecting Debug Information

When reporting issues, include:

```bash
# System info
uname -a
cat /etc/os-release

# asdf info
asdf --version
asdf info
asdf plugin list --urls

# Environment
echo $PATH
echo $ASDF_DIR
echo $ASDF_DATA_DIR

# Permissions
ls -la /opt/asdf/
groups $(whoami)
```

---

## See Also

- **[Introduction](01-introduction.md)** - asdf overview
- **[Plugin Management](04-plugin-management.md)** - Plugin configuration
- **[Performance & Security](07-performance-security.md)** - Optimization

---

[← Back to asdf Documentation](README.md) | [Previous: Performance & Security](07-performance-security.md)
