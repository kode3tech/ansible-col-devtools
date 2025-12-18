# 👨‍💻 Development Documentation

Documentation for contributors and developers working on the code3tech.devtools collection.

## 📋 Documentation Structure

### [Role Structure](ROLE_STRUCTURE.md)
Understanding how roles are organized in this collection.
- Standard role structure
- File organization
- Naming conventions
- Best practices

### [Testing Guide](TESTING.md)
Comprehensive testing guide for the collection.
- Testing framework (Molecule)
- Running tests (Make + Molecule)
- Test structure and platforms
- What gets tested (and what doesn't)
- CI/CD integration
- Troubleshooting
- Docker-in-Docker (DinD) considerations

---

## 🎯 For New Contributors

1. **Read** [Role Structure Guide](ROLE_STRUCTURE.md)
2. **Review** [Testing Guide](TESTING.md)
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

See [Testing Guide](TESTING.md) for complete documentation.

---

## 📚 Related Documentation

- [Contributing Guide](../../CONTRIBUTING.md) - How to contribute
- [Code of Conduct](../../CODE_OF_CONDUCT.md) - Community guidelines
- [Security Policy](../../SECURITY.md) - Reporting vulnerabilities

---

[← Back to Documentation Index](../README.md)
