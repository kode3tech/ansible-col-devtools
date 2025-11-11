# Molecule Tests Update - Insecure Registries

## 📋 Overview

Updated Molecule test scenarios for both `docker` and `podman` roles to include comprehensive testing of insecure registry configurations.

**Date**: 2024  
**Roles Updated**: docker, podman  
**Purpose**: Validate insecure registries feature implementation

---

## 🎯 Test Coverage Added

### Docker Role Tests

#### 1. Converge Scenario (`roles/docker/molecule/default/converge.yml`)

**Added Variables**:
```yaml
docker_insecure_registries:
  - "localhost:5000"
  - "registry.test.local:5000"
  - "192.168.100.100:5000"
```

**Purpose**: Test role configuration with multiple insecure registries

#### 2. Verification Tasks (`roles/docker/molecule/default/verify.yml`)

**New Verification Checks**:

1. **daemon.json File Existence**
   - Verifies `/etc/docker/daemon.json` exists
   - Uses `stat` and `assert` modules

2. **daemon.json Content Validation**
   - Reads and parses JSON content
   - Validates `insecure-registries` key exists
   - Checks array has items

3. **Specific Registries Present**
   - Validates each test registry is in configuration
   - Registries: `localhost:5000`, `registry.test.local:5000`, `192.168.100.100:5000`

4. **Debug Output**
   - Displays configured insecure registries for troubleshooting

#### 3. Pytest Tests (`roles/docker/molecule/default/test_default.py`)

**New Test Functions**:

1. **`test_docker_daemon_json_contains_insecure_registries()`**
   - Parses daemon.json using Python's json module
   - Validates insecure-registries is a list
   - Checks all expected registries are present
   - Individual assertions for each registry

2. **`test_docker_daemon_json_valid_format()`**
   - Validates JSON syntax
   - Catches JSONDecodeError exceptions
   - Ensures configuration won't break Docker daemon

---

### Podman Role Tests

#### 1. Converge Scenario (`roles/podman/molecule/default/converge.yml`)

**Added Variables**:
```yaml
podman_insecure_registries:
  - "localhost:5000"
  - "registry.test.local:5000"
  - "192.168.100.100:5000"
```

**Purpose**: Test role configuration with insecure registries

#### 2. Verification Tasks (`roles/podman/molecule/default/verify.yml`)

**New Verification Checks**:

1. **registries.conf Content Reading**
   - Uses `slurp` module to read configuration
   - Debug output for troubleshooting

2. **Count Insecure Registries**
   - Shell script to count `insecure = true` entries
   - Validates at least 3 entries exist

3. **Specific Registry Validation**
   - Checks each registry has `location = "registry"` line
   - Uses `lineinfile` in check mode

4. **Insecure Flag Verification**
   - AWK script to verify `insecure = true` for each registry
   - Ensures proper TOML structure

#### 3. Pytest Tests (`roles/podman/molecule/default/test_default.py`)

**Fixed Issues**:
- Added missing `testinfra_hosts` configuration
- Added proper imports: `os`, `testinfra.utils.ansible_runner`

**New Test Functions**:

1. **`test_registries_conf_contains_insecure_registries()`**
   - Checks for `[[registry]]` TOML sections
   - Validates presence of `insecure = true`
   - Counts insecure registry entries (minimum 3)

2. **`test_specific_insecure_registries_configured()`**
   - Validates each expected registry has location directive
   - Checks TOML format: `location = "registry"`

3. **`test_insecure_flag_for_each_registry()`**
   - Uses regex to validate TOML block structure
   - Ensures each registry has `insecure = true` flag
   - Pattern: `[[registry]]` → `location` → `insecure = true`

4. **`test_registries_conf_valid_toml_syntax()`**
   - Basic TOML validation
   - Counts registry blocks vs location directives
   - Ensures configuration structure is valid

---

## 🧪 Test Execution

### Running Tests

**Docker Role**:
```bash
cd roles/docker
molecule test
```

**Podman Role**:
```bash
cd roles/podman
molecule test
```

**Both Roles**:
```bash
make test-all
```

### Expected Results

#### Docker Role Tests
- ✅ daemon.json exists and is valid JSON
- ✅ insecure-registries array contains 3 registries
- ✅ All expected registries present
- ✅ Docker service restarts successfully

#### Podman Role Tests
- ✅ registries.conf exists
- ✅ Contains at least 3 `[[registry]]` blocks
- ✅ Each registry has `insecure = true` flag
- ✅ TOML syntax is valid

---

## 📊 Test Matrix

### Platforms Tested

| Platform | OS Family | Docker Tests | Podman Tests |
|----------|-----------|--------------|--------------|
| Ubuntu 22.04 | Debian | ✅ | ✅ |
| Debian 12 | Debian | ✅ | ✅ |
| Rocky Linux 9 | RedHat | ✅ | ✅ |

### Test Types

| Test Type | Docker | Podman | Description |
|-----------|--------|--------|-------------|
| File Existence | ✅ | ✅ | Config file exists |
| Syntax Validation | ✅ | ✅ | JSON/TOML valid |
| Content Verification | ✅ | ✅ | Registries present |
| Structure Check | ✅ | ✅ | Proper format |
| Count Validation | ✅ | ✅ | Minimum entries |

---

## 🔍 Verification Methods

### Docker Role Verification

**Ansible Tasks**:
```yaml
# Check file exists
- ansible.builtin.stat: path=/etc/docker/daemon.json

# Read and parse JSON
- ansible.builtin.slurp: src=/etc/docker/daemon.json
- ansible.builtin.set_fact: daemon_config="{{ content | b64decode | from_json }}"

# Validate content
- ansible.builtin.assert:
    that:
      - "'insecure-registries' in daemon_config"
      - "daemon_config['insecure-registries'] | length > 0"
```

**Pytest Tests**:
```python
import json

def test_docker_daemon_json_contains_insecure_registries(host):
    daemon_config_file = host.file("/etc/docker/daemon.json")
    daemon_config = json.loads(daemon_config_file.content_string)
    
    assert "insecure-registries" in daemon_config
    assert isinstance(daemon_config["insecure-registries"], list)
    
    for registry in expected_registries:
        assert registry in daemon_config["insecure-registries"]
```

### Podman Role Verification

**Ansible Tasks**:
```yaml
# Count insecure entries
- ansible.builtin.shell: |
    grep -A2 '^\[\[registry\]\]' /etc/containers/registries.conf | \
    grep -c 'insecure = true' || echo "0"

# Verify specific registry
- ansible.builtin.lineinfile:
    path: /etc/containers/registries.conf
    line: 'location = "{{ item }}"'
    state: present
  check_mode: true
  failed_when: registry_check.changed
```

**Pytest Tests**:
```python
import re

def test_insecure_flag_for_each_registry(host):
    config_file = host.file("/etc/containers/registries.conf")
    content = config_file.content_string
    
    for registry in expected_registries:
        pattern = rf'\[\[registry\]\].*?location = "{re.escape(registry)}".*?insecure = true'
        assert re.search(pattern, content, re.DOTALL)
```

---

## 🐛 Known Issues & Solutions

### Issue 1: Testinfra Host Configuration
**Problem**: Podman tests missing `testinfra_hosts` configuration  
**Solution**: Added standard testinfra setup:
```python
import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')
```

### Issue 2: TOML Parsing Complexity
**Problem**: TOML format harder to validate than JSON  
**Solution**: Used multiple verification methods:
- String matching for basic checks
- Regex for structure validation
- AWK scripts for context-aware checks

### Issue 3: Multi-line TOML Blocks
**Problem**: Registry blocks span multiple lines  
**Solution**: Used `re.DOTALL` flag in regex patterns to match across lines

---

## 📝 Best Practices Applied

### 1. **Multiple Verification Layers**
- Ansible assertions
- Pytest unit tests
- Manual verification tasks

### 2. **Descriptive Test Names**
- Clear function names indicate purpose
- Docstrings explain what each test validates

### 3. **Comprehensive Coverage**
- File existence
- Syntax validation
- Content verification
- Structure checks

### 4. **Error Messages**
- Informative failure messages
- Include context (counts, missing items)
- Help debugging with debug tasks

### 5. **Platform Independence**
- Tests work on all supported platforms
- OS-specific logic handled by role
- Tests validate outcomes, not methods

---

## 🚀 Continuous Integration

### GitHub Actions Integration

Tests can be integrated into CI/CD:

```yaml
- name: Test Docker Role
  run: |
    cd roles/docker
    molecule test

- name: Test Podman Role
  run: |
    cd roles/podman
    molecule test
```

### Local Development Workflow

```bash
# 1. Make changes to role
vim roles/docker/tasks/main.yml

# 2. Run tests
cd roles/docker
molecule converge  # Apply changes

# 3. Verify manually if needed
molecule login

# 4. Run full test suite
molecule test

# 5. Cleanup
molecule destroy
```

---

## 📚 Related Documentation

- [TESTING.md](TESTING.md) - General testing guide
- [ROLE_STRUCTURE.md](../ROLE_STRUCTURE.md) - Role structure standards
- [Docker Role README](../../../roles/docker/README.md) - Docker role documentation
- [Podman Role README](../../../roles/podman/README.md) - Podman role documentation
- [CHANGELOG.md](../../../CHANGELOG.md) - Version history

---

## ✅ Verification Checklist

Before committing changes:

- [x] Docker converge.yml updated with test variables
- [x] Docker verify.yml has insecure registry checks
- [x] Docker test_default.py has pytest tests
- [x] Podman converge.yml updated with test variables
- [x] Podman verify.yml has insecure registry checks
- [x] Podman test_default.py has pytest tests
- [x] All tests use FQCN (Fully Qualified Collection Names)
- [x] Test names are descriptive
- [x] Error messages are informative
- [x] Documentation updated

---

## 🎓 Key Learnings

1. **JSON vs TOML Validation**: Different approaches needed for different formats
2. **Multi-Layer Testing**: Ansible + Pytest provides comprehensive coverage
3. **Regex for TOML**: Essential for validating multi-line TOML structures
4. **Check Mode Usage**: Efficient way to verify without changes
5. **Testinfra Integration**: Proper setup required for pytest-testinfra

---

## 📞 Support

For questions about these tests:
- Review [TESTING.md](TESTING.md) for general testing guidance
- Check Molecule documentation: https://molecule.readthedocs.io/
- Open GitHub issue for bugs or improvements

---

**Last Updated**: 2024  
**Maintainer**: Kode3Tech DevOps Team
