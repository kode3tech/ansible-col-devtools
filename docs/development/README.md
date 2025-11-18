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
- [Molecule Testing](testing/MOLECULE_TESTING.md) - Molecule test framework
- [Molecule Quick Reference](testing/MOLECULE_QUICK_REFERENCE.md) - Molecule commands

---

## 🎯 For New Contributors

1. **Read** [Role Structure Guide](ROLE_STRUCTURE.md)
2. **Review** [Molecule Testing](testing/MOLECULE_TESTING.md)
3. **Run** tests with `make test`

---

## 🧪 Running Tests

```bash
# Test all roles
make test

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
