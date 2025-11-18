# Contributing to kode3tech.devtools

First off, thank you for considering contributing to kode3tech.devtools! It's people like you that make this collection better for everyone.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Pull Requests](#pull-requests)
- [Development Setup](#development-setup)
- [Style Guidelines](#style-guidelines)
  - [Git Commit Messages](#git-commit-messages)
  - [Ansible Code Style](#ansible-code-style)
  - [Python Code Style](#python-code-style)
  - [YAML Style](#yaml-style)
- [Testing](#testing)
  - [Running Tests](#running-tests)
  - [Writing Tests](#writing-tests)
- [Documentation](#documentation)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by respect and professionalism. By participating, you are expected to uphold this standard. Please be respectful and constructive in your interactions.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the [existing issues](https://github.com/kode3tech/ansible-devtools/issues) to avoid duplicates.

When you create a bug report, please include as many details as possible:

**Use the following template:**

```markdown
**Description:**
A clear and concise description of the bug.

**To Reproduce:**
Steps to reproduce the behavior:
1. Run command '...'
2. With these variables '...'
3. See error

**Expected behavior:**
What you expected to happen.

**Environment:**
- OS: [e.g. Ubuntu 22.04]
- Ansible Version: [e.g. 2.15.0]
- Collection Version: [e.g. 1.0.0]
- Python Version: [e.g. 3.11]

**Additional context:**
Add any other context about the problem here (logs, screenshots, etc.).
```

### Suggesting Enhancements

Enhancement suggestions are tracked as [GitHub issues](https://github.com/kode3tech/ansible-devtools/issues).

When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful** to most users
- **List any alternative solutions** you've considered

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our style guidelines
3. **Add tests** for your changes
4. **Ensure all tests pass** (`make test`)
5. **Ensure linting passes** (`make lint`)
6. **Update documentation** if needed
7. **Commit your changes** using conventional commits
8. **Push to your fork** and submit a pull request

**Pull Request Template:**

```markdown
**Description:**
Brief description of what this PR does.

**Related Issue:**
Fixes #(issue number)

**Type of Change:**
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

**Checklist:**
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

**Testing:**
Describe the tests you ran and their results.
```

## Development Setup

### Prerequisites

- Python 3.11+
- Git
- asdf (recommended for version management)

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ansible-devtools.git
cd ansible-devtools

# Add upstream remote
git remote add upstream https://github.com/kode3tech/ansible-devtools.git

# Install dependencies
make install

# Activate virtual environment
source .venv/bin/activate

# Verify installation
make version
```

### Keeping Your Fork Updated

```bash
# Fetch upstream changes
git fetch upstream

# Merge upstream main into your local main
git checkout main
git merge upstream/main

# Push updates to your fork
git push origin main
```

## Style Guidelines

### Git Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/) specification:

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Code style changes (formatting, missing semi-colons, etc)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(docker): add support for Ubuntu 24.04

Added support for Ubuntu 24.04 LTS including repository
configuration and package installation.

Closes #123

fix(podman): correct storage driver detection on Debian

The storage driver was incorrectly detected on Debian systems
due to missing overlay module check.

Fixes #456
```

### Ansible Code Style

We follow Ansible best practices and use `ansible-lint` to enforce standards:

**Key Guidelines:**

1. **Use Fully Qualified Collection Names (FQCN):**
   ```yaml
   # Good
   - ansible.builtin.package:
       name: docker-ce
   
   # Bad
   - package:
       name: docker-ce
   ```

2. **Naming Conventions:**
   - Use descriptive task names
   - Use snake_case for variables
   - Use clear, meaningful names

3. **YAML Formatting:**
   - Use 2 spaces for indentation
   - Quote strings when necessary
   - Keep lines under 160 characters (preferred 120)

4. **Tasks:**
   - Add `changed_when` for command/shell tasks
   - Use `failed_when` instead of `ignore_errors`
   - Add tags for role organization

5. **Variables:**
   - Prefix role variables with role name
   - Document all variables in `defaults/main.yml`
   - Use `vars/` for constants

**Example Task:**
```yaml
- name: Install Docker packages
  ansible.builtin.package:
    name: "{{ docker_packages }}"
    state: present
  tags:
    - docker
    - packages
```

### YAML Linting

We use `yamllint` with the following configuration:

- Indentation: 2 spaces
- Line length: 160 characters max
- No trailing spaces
- Document start optional

Run linting:
```bash
make lint-yaml
```

### Ansible Linting

We use `ansible-lint` with production profile:

```bash
make lint-ansible
```

## Testing

All changes must include tests and all tests must pass before merging.

### Running Tests

```bash
# Test all roles
make test

# Run linting
make lint
```

### Writing Tests

1. **Molecule Tests** - Located in `roles/*/molecule/default/`
   - `molecule.yml` - Test configuration
   - `converge.yml` - Apply the role
   - `verify.yml` - Ansible-based verification
   - `test_default.py` - Pytest/testinfra tests

2. **Test Structure:**
   ```python
   def test_package_installed(host):
       """Verify package is installed."""
       pkg = host.package("docker-ce")
       assert pkg.is_installed
   ```

3. **Test Coverage:**
   - Package installation
   - Service status
   - Configuration files
   - Permissions
   - Functionality tests

### Test Platforms

We test on:
- Ubuntu 22.04 (Jammy)
- Debian 12 (Bookworm)
- Rocky Linux 9

## Documentation

### What to Document

1. **Code Comments:**
   - Complex logic
   - Non-obvious decisions
   - Platform-specific workarounds

2. **README Updates:**
   - New features
   - Changed behavior
   - New variables
   - Usage examples

3. **Role Documentation:**
   - Update `roles/*/README.md`
   - Document all variables
   - Provide usage examples
   - List supported platforms

4. **CHANGELOG:**
   - Add entry for your changes
   - Follow [Keep a Changelog](https://keepachangelog.com/) format
   - Group changes by type (Added, Changed, Fixed, etc.)

### Documentation Style

- Use clear, concise language
- Provide examples
- Use proper Markdown formatting
- Include code blocks with syntax highlighting

**Example:**

````markdown
### New Variable

The `docker_custom_registry` variable allows configuring custom registries:

```yaml
docker_custom_registry:
  - "registry.example.com"
  - "docker.internal.net"
```

Default: `[]` (empty list)
````

## Review Process

1. **Automated Checks:**
   - Linting (ansible-lint, yamllint)
   - Tests (Molecule, pytest)
   - CI/CD pipeline

2. **Code Review:**
   - At least one maintainer approval required
   - Constructive feedback provided
   - Response time: typically 2-3 business days

3. **Merge:**
   - Squash and merge preferred
   - Conventional commit message required
   - Branch deleted after merge

## Questions?

- **Issues:** [GitHub Issues](https://github.com/kode3tech/ansible-devtools/issues)
- **Discussions:** [GitHub Discussions](https://github.com/kode3tech/ansible-devtools/discussions)
- **Email:** suporte@kode3.tech

## Recognition

Contributors will be recognized in:
- README.md acknowledgments section
- Git commit history
- Release notes

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to kode3tech.devtools!** 🚀

**Made with ❤️ by Kode3Tech DevOps Team**
