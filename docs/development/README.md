# 👨‍💻 Development Documentation

Documentation for contributors and developers working on the kode3tech.devtools collection.

## 📋 Documentation Structure

### [Role Structure](ROLE_STRUCTURE.md)
Understanding how roles are organized in this collection.
- Standard role structure
- File organization
- Naming conventions
- Best practices

### [Testing](testing/)
Complete testing documentation.
- [Testing Strategy](testing/TESTING.md) - Overall testing approach
- [Molecule Testing](testing/MOLECULE_TESTING.md) - Molecule test framework
- [Quick Reference](testing/MOLECULE_QUICK_REFERENCE.md) - Molecule commands
- [Test Summary](testing/MOLECULE_TESTS_SUMMARY.md) - Current test coverage
- [Test Updates](testing/MOLECULE_TESTS_UPDATE.md) - Recent test changes
- [Test Reports](testing/TEST_REPORT.md) - Latest test results

---

## 🎯 For New Contributors

1. **Read** [Contributing Guide](../../CONTRIBUTING.md)
2. **Understand** [Role Structure](ROLE_STRUCTURE.md)
3. **Learn** [Testing Strategy](testing/TESTING.md)
4. **Run** tests with Molecule

---

## 🧪 Running Tests

```bash
# Test all roles
make test-all

# Test specific role
make test-docker
make test-podman

# Using Molecule directly
cd roles/docker
molecule test
```

See [Testing Documentation](testing/) for details.

---

## 📚 Related Documentation

- [Contributing Guide](../../CONTRIBUTING.md) - How to contribute
- [Code of Conduct](../../CODE_OF_CONDUCT.md) - Community guidelines
- [Security Policy](../../SECURITY.md) - Reporting vulnerabilities

---

[← Back to Documentation Index](../README.md)
