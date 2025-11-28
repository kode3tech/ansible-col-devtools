# Molecule Testing Guide

## 📋 Overview

This document explains how Molecule tests work and what are the limitations of the Docker-in-Docker (DinD) environment.

## 🐳 Test Environment

### Tested Platforms
- **Ubuntu 22.04** (geerlingguy/docker-ubuntu2204-ansible)
- **Debian 12** (geerlingguy/docker-debian12-ansible)
- **Rocky Linux 9** (geerlingguy/docker-rockylinux9-ansible)

### Docker-in-Docker (DinD)

Molecule tests run **Docker/Podman INSIDE privileged Docker containers**. This has some implications:

**Advantages:**
- ✅ Fast and isolated tests
- ✅ Doesn't affect the host
- ✅ Multiple distros in parallel
- ✅ CI/CD friendly

**Limitations:**
- ⚠️ Limited storage drivers (usually `vfs` instead of `overlay2`)
- ⚠️ Performance doesn't represent real environment
- ⚠️ Some advanced features may not work
- ⚠️ Rootless Podman behaves differently

## 🎯 What the Tests Validate

### ✅ Configuration Validation
Molecule tests focus on **validating that configurations are correct**:

- Configuration files created correctly
- Valid syntax (JSON, TOML, etc.)
- Appropriate permissions
- Services enabled and running
- Users and groups configured
- Repositories and GPG keys installed

### ❌ What is NOT Tested
The tests **DO NOT measure real performance** because:

- DinD adds significant overhead
- Storage drivers are different (vfs vs overlay2)
- Host kernel limitations
- Resources shared with sibling containers

## 📊 Performance: Molecule vs. Production

### Docker Storage Driver

| Environment | Storage Driver | Performance |
|-------------|---------------|-------------|
| **Production** | overlay2 | 100% (baseline) |
| **Molecule (DinD)** | vfs | 30-40% (slow, but compatible) |

**Why?**
- DinD cannot reliably use overlay2
- The host kernel is already using overlay2 for the Molecule container
- Cannot efficiently do overlay-over-overlay

### Molecule-Specific Configurations

#### Docker (`roles/docker/molecule/default/converge.yml`)
```yaml
# Override default storage-driver to let Docker auto-detect
docker_daemon_config:
  log-driver: "json-file"
  log-opts:
    max-size: "10m"
    max-file: "3"
  # storage-driver: removed for DinD compatibility
```

**In production** (`defaults/main.yml`):
```yaml
docker_daemon_config:
  log-driver: "json-file"
  log-opts:
    max-size: "10m"
    max-file: "3"
  storage-driver: "overlay2"  # ✅ Explicit for performance
```

#### Podman
Podman in Molecule runs in rootless mode inside privileged containers, which is a unique scenario. In production, rootless Podman has direct access to XDG_RUNTIME_DIR and subuid/subgid on the host.

## 🧪 Running the Tests

### Prerequisites
```bash
# Activate virtual environment
source activate.sh

# Install dependencies (if needed)
pip install -r requirements.txt
```

### Docker Role
```bash
cd roles/docker
molecule test
```

### Podman Role
```bash
cd roles/podman
molecule test
```

### Converge Only (without destroy)
```bash
molecule converge
```

### Verify Only (with existing containers)
```bash
molecule verify
```

## 📝 Test Structure

### Installation Tests
- Packages installed
- Services running and enabled
- Correct versions

### Configuration Tests
- Configuration files exist
- Valid syntax (JSON, TOML)
- Correct permissions
- Security settings

### Performance Tests (Config Validation)
- ✅ `daemon.json` has `storage-driver` configured (if applicable)
- ✅ `storage.conf` has correct optimizations
- ✅ crun installed (optional)
- ✅ Appropriate logging settings
- ❌ **We DON'T measure real performance** (DinD is not representative)

### Security Tests
- Insecure registries configured
- GPG keys installed correctly
- Repositories authenticated

## 🔍 Interpreting Results

### ✅ Test Passed
Means that the **configuration is correct**, not that performance is optimal.

### ❌ Test Failed
May indicate:
1. Incorrect configuration (real problem)
2. DinD incompatibility (may work in production)
3. Test environment limitation

## 🚀 Production Validation

To validate real performance, use the example playbooks:

```bash
# Test in real environment
ansible-playbook -i inventory.ini playbooks/docker/install-docker.yml

# Validate configurations
ansible -i inventory.ini all -m shell \
  -a 'docker info | grep "Storage Driver"'

ansible -i inventory.ini all -m shell \
  -a 'cat /etc/containers/storage.conf | grep "driver ="'
```

## 📈 Expected Performance Gains

### In Production (NOT in Molecule!)

| Optimization | Expected Gain | Where to Test |
|--------------|---------------|---------------|
| Docker overlay2 | +15-30% I/O | Real hosts |
| Docker crun | +20-30% startup | Real hosts |
| Podman overlay+metacopy | +30-50% I/O | Real hosts |
| Podman crun | +20-30% startup | Real hosts |
| Podman parallel copies | +200-300% pull | Real hosts |

**⚠️ IMPORTANT:** These gains **are NOT measurable in Molecule** due to DinD limitations!

## 🎓 Lessons Learned

### 1. Molecule is for CI/CD, not benchmarks
Use Molecule to ensure the role **works**, not to measure **how fast** it works.

### 2. DinD has known limitations
Storage drivers, networking, and performance are different from the real world.

### 3. Conditional tests are important
```python
# Example: don't force overlay2 in Molecule
if "storage-driver" in daemon_config:
    assert daemon_config["storage-driver"] == "overlay2"
# If not configured, Docker auto-detected (vfs in DinD)
```

### 4. Always validate in real environment
Molecule is the first line of defense, not the last.

## 🔗 References

- [Molecule Documentation](https://molecule.readthedocs.io/)
- [Docker Storage Drivers](https://docs.docker.com/storage/storagedriver/)
- [Podman Storage Configuration](https://docs.podman.io/en/latest/markdown/podman-storage.conf.5.html)
- [Rootless Podman](https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md)

---

[← Back to Testing Documentation](README.md)

**Summary:** Use Molecule to validate configurations, not to measure performance. Test performance on real hosts! 🚀
