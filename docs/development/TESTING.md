# 🧪 Testing Guide

Comprehensive testing documentation for the **code3tech.devtools** collection.

## 📋 Table of Contents

- [Overview](#-overview)
- [Testing Framework](#-testing-framework)
- [Running Tests](#-running-tests)
- [Test Structure](#-test-structure)
- [Test Environments](#-test-environments)
- [What Gets Tested](#-what-gets-tested)
- [Limitations](#%EF%B8%8F-test-environment-limitations)
- [CI/CD Integration](#-cicd-integration)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Overview

The collection uses a **multi-layered testing approach** to ensure quality:

1. **Syntax validation** - Yamllint + Ansible-lint
2. **Molecule tests** - Installation and configuration validation
3. **CI/CD automation** - GitHub Actions on every commit

### Testing Philosophy

- ✅ **Validate configuration correctness** (primary goal)
- ✅ **Test on multiple distributions** (Ubuntu, Debian, RHEL)
- ✅ **Ensure idempotency** (run twice, no changes on second run)
- ⚠️ **Not for performance benchmarking** (DinD limitations)

---

## 🔧 Testing Framework

### Molecule

**Molecule** is the primary testing framework for all roles in this collection.

**Why Molecule?**
- Tests roles in isolated Docker containers
- Multi-platform testing (Ubuntu, Debian, Rocky Linux)
- Supports full lifecycle: create → converge → verify → destroy
- Integrates with CI/CD pipelines

**Architecture:**
```
molecule/default/
├── molecule.yml          # Test configuration
├── converge.yml          # Apply role
├── verify.yml            # Ansible verification
├── test_default.py       # Pytest tests
└── prepare.yml           # Pre-test setup (optional)
```

### Linters

#### Ansible-lint
Validates Ansible best practices:
- FQCN usage (Fully Qualified Collection Names)
- Task naming conventions
- Security checks
- Deprecated module usage

#### Yamllint
Validates YAML syntax and style:
- Indentation (2 spaces)
- Line length (160 chars)
- Trailing spaces
- Document start markers

---

## 🚀 Running Tests

### All Tests (Recommended)

```bash
# Run linters + all role tests
make test
```

### Linting Only

```bash
# Run both linters
make lint

# Individual linters
make lint-yaml      # Yamllint only
make lint-ansible   # Ansible-lint only
```

### Molecule Tests

#### Test All Roles
```bash
# From collection root
for role in roles/*/; do
  cd "$role"
  molecule test
  cd ../..
done
```

#### Test Specific Role
```bash
cd roles/docker
molecule test
```

#### Molecule Workflow Steps

```bash
# Full workflow
molecule test               # Complete: create → test → destroy

# Individual steps
molecule create             # Create test containers
molecule converge           # Apply role
molecule verify             # Run verification tests
molecule destroy            # Clean up containers

# Debugging
molecule converge           # Apply and keep running
molecule login              # SSH into container
molecule verify             # Run tests manually
```

---

## 📁 Test Structure

### Standard Molecule Structure

Every role follows this pattern:

```
roles/<role>/
├── molecule/
│   └── default/
│       ├── molecule.yml          # Platforms and config
│       ├── prepare.yml           # Pre-test setup
│       ├── converge.yml          # Apply role
│       ├── verify.yml            # Ansible verification
│       └── test_default.py       # Pytest/testinfra tests
├── pytest.ini                    # Pytest configuration
└── README.md                     # Role documentation
```

### Test Platforms Matrix

All roles test on:

| Platform | Image | Purpose |
|----------|-------|---------|
| **Ubuntu 22.04** | geerlingguy/docker-ubuntu2204-ansible | Debian-family (LTS) |
| **Debian 12** | geerlingguy/docker-debian12-ansible | Debian-family (current) |
| **Rocky Linux 9** | geerlingguy/docker-rockylinux9-ansible | RHEL-family |

---

## 🧪 What Gets Tested

### ✅ Configuration Validation

Molecule tests focus on **validating that configurations are correct**:

#### Installation
- ✅ Packages installed
- ✅ Correct versions
- ✅ Dependencies resolved
- ✅ Repository configuration

#### Configuration Files
- ✅ Files created in correct locations
- ✅ Valid syntax (JSON, TOML, YAML, etc.)
- ✅ Proper permissions and ownership
- ✅ Security settings applied

#### Services
- ✅ Services enabled
- ✅ Services running
- ✅ Service state verification
- ✅ Service configuration valid

#### Users & Groups
- ✅ Users created
- ✅ Groups assigned
- ✅ Permissions correct
- ✅ Home directories exist

#### Idempotency
- ✅ Running role twice produces no changes
- ✅ State remains consistent
- ✅ No unexpected modifications

### ❌ What is NOT Tested

Performance benchmarking is **NOT** the goal because:

- ⚠️ **Docker-in-Docker overhead** - Containers inside containers add latency
- ⚠️ **Storage driver differences** - DinD uses `vfs` instead of `overlay2`
- ⚠️ **Resource constraints** - Shared resources affect performance
- ⚠️ **Network overhead** - Bridge networking adds overhead
- ⚠️ **Kernel limitations** - Host kernel restricts nested capabilities

**For performance validation**, use the collection in a **real production environment** with the example playbooks.

---

## 🐳 Test Environment Limitations

### Docker-in-Docker (DinD)

Molecule runs containers **inside privileged Docker containers** (DinD).

**Advantages:**
- ✅ Fast and isolated
- ✅ No host impact
- ✅ Parallel execution
- ✅ CI/CD friendly
- ✅ Consistent environments

**Limitations:**
- ⚠️ Storage drivers limited (usually `vfs`)
- ⚠️ Performance not representative
- ⚠️ Some advanced features unavailable
- ⚠️ Nested virtualization constraints
- ⚠️ Rootless containers behave differently

### Storage Driver Comparison

| Environment | Storage Driver | Performance |
|-------------|---------------|-------------|
| **Production** | overlay2 | 100% (baseline) |
| **Molecule (DinD)** | vfs | 30-40% slower |

**Why?** DinD cannot efficiently layer overlay-over-overlay.

### Testing Strategy

**Molecule validates:** Configuration correctness ✅  
**Production validates:** Performance & real-world scenarios ✅

---

## 🎯 Test Coverage by Role

### Current Roles

| Role | Molecule Tests | Special Considerations |
|------|----------------|------------------------|
| **docker** | ✅ Yes | DinD storage driver auto-detect |
| **podman** | ✅ Yes | Rootless mode in privileged containers |
| **asdf** | ✅ Yes | Multi-user, plugin management |
| **azure_devops_agents** | ✅ Yes | Multi-agent, service verification |
| **github_actions_runners** | ✅ Yes | Multi-runner, API-based management |
| **gitlab_ci_runners** | ✅ Yes | Multi-runner, API creation workflow |

### Test Scenarios

Each role tests:
1. **Basic installation** - Packages and dependencies
2. **Multi-instance setup** - Multiple agents/runners/plugins
3. **Configuration management** - Files and settings
4. **Service management** - Systemd units
5. **Removal workflow** - Clean uninstall (`state: absent`)

---

## 🔄 CI/CD Integration

### GitHub Actions Workflows

#### `.github/workflows/ci.yml`
Runs on **every push and pull request**:
- Yamllint validation
- Ansible-lint validation
- Molecule tests (all roles, all platforms)

#### `.github/workflows/sanity.yml`
Runs **ansible-test sanity**:
- Python syntax checks
- Import validation
- Documentation checks
- Collection structure validation

#### `.github/workflows/release.yml`
Runs on **version tags**:
- Build collection tarball
- Publish to Ansible Galaxy
- Create GitHub release

### CI Test Matrix

```yaml
strategy:
  matrix:
    distro:
      - ubuntu2204
      - debian12
      - rockylinux9
    role:
      - docker
      - podman
      - asdf
      - azure_devops_agents
      - github_actions_runners
      - gitlab_ci_runners
```

**Total test combinations:** 18 (3 distros × 6 roles)

---

## 🔍 Interpreting Results

### ✅ Test Passed

**Meaning:** Configuration is **correct** and role works as expected.

**Does NOT guarantee:**
- Optimal performance (test in production)
- Real-world edge cases (limited environment)
- Security hardening (basic validation only)

### ❌ Test Failed

May indicate:
1. **Actual problem** - Configuration error, bug in role
2. **DinD incompatibility** - Works in production, fails in DinD
3. **Test environment issue** - Container image problem
4. **Timing issue** - Service startup delay

**Debugging steps:**
```bash
molecule converge           # Apply role
molecule login              # Inspect container
molecule verify             # Run tests manually
journalctl -xe              # Check service logs
```

---

## 🛠️ Troubleshooting

### Common Issues

#### 1. Service Fails to Start in Molecule

**Problem:** Systemd services don't work in containers.

**Solution:** Molecule uses **privileged containers** with systemd support:
```yaml
# molecule.yml
platforms:
  - name: test
    privileged: true
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:rw
    cgroupns_mode: host
```

#### 2. Permission Denied Errors

**Problem:** File ownership issues.

**Solution:** Use `become: true` and proper ownership:
```yaml
- name: Create config file
  ansible.builtin.file:
    path: /etc/service/config
    owner: service-user
    group: service-user
    mode: '0600'
```

#### 3. Tests Fail on Rocky Linux Only

**Problem:** RHEL-family has different package names or paths.

**Solution:** Use OS-specific variables:
```yaml
# vars/Debian.yml
packages: [pkg-debian]

# vars/RedHat.yml
packages: [pkg-redhat]
```

#### 4. Molecule Hangs on Destroy

**Problem:** Containers won't stop.

**Solution:** Force removal:
```bash
molecule destroy --force
docker ps -a | grep molecule | awk '{print $1}' | xargs docker rm -f
```

#### 5. GPG Key Import Fails

**Problem:** Network issues or repository changes.

**Solution:** Import keys with error handling:
```yaml
- name: Import GPG key
  ansible.builtin.rpm_key:
    key: "{{ gpg_key_url }}"
    state: present
  retries: 3
  delay: 5
```

---

## 📊 Test Reporting

### View Test Results

```bash
# Verbose output
molecule test --debug

# Save output
molecule test 2>&1 | tee test-output.log

# JSON format (for parsing)
molecule test --format json
```

### Molecule Summary

After tests complete, check:
- **PLAY RECAP** - Ansible task results
- **pytest output** - Python test results
- **Return code** - 0 = success, non-zero = failure

---

## 🎓 Best Practices

### 1. Run Linters First
```bash
make lint       # Fix issues before Molecule
```

### 2. Test Incrementally
```bash
molecule converge    # Apply role
molecule verify      # Test
# Fix issues, repeat
```

### 3. Keep Tests Fast
- Use `skip_tags` for time-consuming tasks
- Mock external dependencies
- Use fixtures for data

### 4. Write Clear Assertions
```python
def test_service_running(host):
    """Test that service is running."""
    service = host.service('myservice')
    assert service.is_running
    assert service.is_enabled
```

### 5. Clean Up After Tests
```bash
molecule destroy    # Always clean up
```

---

## 📚 Additional Resources

### Official Documentation
- [Molecule Documentation](https://molecule.readthedocs.io/)
- [Ansible Testing](https://docs.ansible.com/ansible/latest/dev_guide/testing.html)
- [Testinfra](https://testinfra.readthedocs.io/)

### Collection-Specific Guides
- [Role Structure](ROLE_STRUCTURE.md) - How roles are organized
- [Contributing Guide](../../CONTRIBUTING.md) - How to contribute
- [CI/CD Workflows](../../.github/workflows/) - GitHub Actions configuration

---

## 🚀 Production Validation

After Molecule tests pass, validate in **real environments** using example playbooks:

```bash
# Test in real environment
ansible-playbook -i inventory.ini playbooks/docker/install-docker.yml

# Verify installation
ansible -i inventory.ini all -m shell -a 'docker --version'

# Check service status
ansible -i inventory.ini all -m systemd -a 'name=docker state=started'
```

**Remember:** Molecule validates configuration. Production validates performance! 🎯

---

[← Back to Development Documentation](README.md)
