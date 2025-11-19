````markdown
# Quick Start Guide

## 🚀 Initial Setup

### 1. Prerequisites

Ensure you have installed:
- asdf (version manager)
- Python plugin for asdf
- Git

### 2. Clone the Repository

```bash
git clone https://github.com/kode3tech/ansible-col-devtools.git
cd ansible-col-devtools
```

### 3. Configure Python

The project is already configured with Python 3.11.2 via asdf:

```bash
# Install Python version from .tool-versions
asdf install

# Verify
python3 --version  # Should show: Python 3.11.2
```

### 4. Install Dependencies

**Option A: Using the script (Recommended)**

```bash
source activate.sh
```

**Option B: Using make**

```bash
make install
source .venv/bin/activate
```

**Option C: Manual**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Verify Installation

```bash
# Using make
make version

# Or manually
ansible --version
ansible-lint --version
molecule --version
```

## 🛠️ Useful Commands

### Environment Activation

```bash
# Every time you open a new terminal
source .venv/bin/activate

# Or use the script
source activate.sh
```

### Linting

```bash
# Run all linters
make lint

# YAML only
make lint-yaml

# Ansible only
make lint-ansible
```

### Testing

```bash
# Tests with Molecule
make test

# Tests with pytest
make test-pytest
```

### Cleanup

```bash
# Clean temporary files
make clean
```

## 📚 File Structure

```text
.
├── .tool-versions       # Python version (asdf)
├── .python-version      # Alternative Python version
├── requirements.txt     # Dependencies
├── ansible.cfg          # Ansible configuration
├── .ansible-lint        # ansible-lint configuration
├── .yamllint            # yamllint configuration
├── Makefile             # Useful commands
├── activate.sh          # Activation script
├── inventory.example    # Inventory example
└── docs/                # Documentation
```

## 🔧 Next Steps

1. **Configure Inventory**: Copy and edit `inventory.example`
   ```bash
   cp inventory.example inventory
   # Edit with your hosts
   ```

2. **Create a Role**: Use molecule to initialize
   ```bash
   molecule init role role-name
   ```

3. **Develop**: Create your tasks, handlers, templates, etc.

4. **Test**: Run the tests
   ```bash
   make lint
   make test
   ```

## 🆘 Troubleshooting

### Virtual environment won't activate

```bash
# Remove and recreate
rm -rf .venv
make install
```

### Incorrect Python version

```bash
# Check asdf
asdf current python

# Reinstall
asdf install python 3.11.2
asdf global python 3.11.2
```

### Dependencies won't install

```bash
# Update pip first
pip install --upgrade pip

# Then install requirements
pip install -r requirements.txt
```

## 📞 Support

For questions or issues, contact the Code3Tech team.

---

[← Back to Getting Started](README.md)

**Happy Coding! 🚀**

````
