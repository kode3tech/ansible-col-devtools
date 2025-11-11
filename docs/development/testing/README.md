# 🧪 Testing Documentation

Comprehensive testing documentation for the kode3tech.devtools collection.

## 📋 Available Guides

### [Testing Strategy](TESTING.md)
Overall testing approach and strategy.
- Test structure
- Test platforms (Ubuntu, Debian, Rocky)
- Test sequence
- Running tests

### [Molecule Testing Guide](MOLECULE_TESTING.md)
Complete Molecule testing framework documentation.
- Molecule overview
- Docker-in-Docker (DinD) environment
- What tests validate
- Performance considerations
- Limitations and workarounds

### [Molecule Quick Reference](MOLECULE_QUICK_REFERENCE.md)
Quick reference for common Molecule commands.
- Essential commands
- Common workflows
- Troubleshooting

### [Test Summary](MOLECULE_TESTS_SUMMARY.md)
Current test coverage and test scenarios.
- Docker role tests
- Podman role tests
- Insecure registry tests
- Verification methods

### [Test Updates](MOLECULE_TESTS_UPDATE.md)
Recent updates to test scenarios.
- Latest changes
- New test coverage
- Breaking changes

### [Test Report](TEST_REPORT.md)
Latest test execution results.
- Test results by platform
- Pass/fail status
- Issues found

---

## 🚀 Quick Start

### Run All Tests
```bash
make test-all
```

### Test Specific Role
```bash
# Docker
cd roles/docker
molecule test

# Podman
cd roles/podman
molecule test
```

### Individual Test Steps
```bash
molecule create    # Create containers
molecule converge  # Apply role
molecule verify    # Run verification
molecule destroy   # Clean up
```

---

## 📊 Test Platforms

Tests run on the following platforms:

- **Ubuntu 22.04** (Jammy)
- **Debian 12** (Bookworm)
- **Rocky Linux 9**

---

## 🎯 What Gets Tested

### Configuration Validation ✅
- Files created correctly
- Valid syntax (JSON, TOML)
- Correct permissions
- Services running
- Users/groups configured

### What's NOT Tested ⚠️
- Performance (DinD overhead)
- Real-world scenarios
- Rootless Podman (partial)

See [Molecule Testing Guide](MOLECULE_TESTING.md) for details.

---

[← Back to Development Documentation](../README.md)
