.PHONY: help install version doctor lint lint-yaml lint-ansible test clean build install-collection publish

# Variables
VENV_DIR = .venv
PYTHON = $(VENV_DIR)/bin/python
PIP = $(VENV_DIR)/bin/pip
ANSIBLE = $(VENV_DIR)/bin/ansible
ANSIBLE_PLAYBOOK = $(VENV_DIR)/bin/ansible-playbook
ANSIBLE_GALAXY = $(VENV_DIR)/bin/ansible-galaxy
ANSIBLE_LINT = $(VENV_DIR)/bin/ansible-lint
YAMLLINT = $(VENV_DIR)/bin/yamllint
MOLECULE = $(VENV_DIR)/bin/molecule

# Get absolute paths
PROJECT_DIR = $(shell pwd)
MOLECULE_ABS = $(PROJECT_DIR)/$(VENV_DIR)/bin/molecule

COLLECTION_NAMESPACE = code3tech
COLLECTION_NAME = devtools
COLLECTION_VERSION = $(shell grep '^version:' galaxy.yml | awk '{print $$2}')
COLLECTION_FILE = $(COLLECTION_NAMESPACE)-$(COLLECTION_NAME)-$(COLLECTION_VERSION).tar.gz

# Directories to lint
LINT_DIRS = roles
YAMLLINT_DIRS = roles
YAMLLINT_FILES = *.yml *.yaml

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install project dependencies
	@echo "🔧 Creating virtual environment..."
	@python3 -m venv $(VENV_DIR)
	@echo "📦 Installing dependencies..."
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements.txt
	@echo "✅ Installation complete!"
	@echo ""
	@echo "Run 'source .venv/bin/activate' to activate the virtual environment"

version: ## Show installed tools versions
	@echo "📋 Installed versions:"
	@echo ""
	@$(PYTHON) --version || echo "⚠️  Python not found in venv"
	@$(ANSIBLE) --version | head -n 1 || echo "⚠️  Ansible not found in venv"
	@$(ANSIBLE_LINT) --version || echo "⚠️  Ansible-lint not found in venv"
	@$(MOLECULE) --version || echo "⚠️  Molecule not found in venv"
	@$(YAMLLINT) --version || echo "⚠️  Yamllint not found in venv"
	@echo ""
	@echo "Collection: $(COLLECTION_NAMESPACE).$(COLLECTION_NAME) v$(COLLECTION_VERSION)"

lint: ## Run linters (yamllint and ansible-lint)
	@echo "🔍 Running yamllint..."
	@$(YAMLLINT) .
	@echo ""
	@echo "🔍 Running ansible-lint..."
	@$(ANSIBLE_LINT) --profile production .

lint-yaml: ## Run yamllint only
	@$(YAMLLINT) .

lint-ansible: ## Run ansible-lint only
	@$(ANSIBLE_LINT) --profile production .

doctor: ## Diagnose common local environment issues (collections paths, duplicates)
	@echo "🩺 Environment diagnostics"
	@echo ""
	@echo "📌 Project: $(COLLECTION_NAMESPACE).$(COLLECTION_NAME) v$(COLLECTION_VERSION)"
	@echo "📌 PWD: $(PROJECT_DIR)"
	@echo ""
	@echo "🐍 Python:"
	@$(PYTHON) --version || true
	@echo ""
	@echo "🧰 Tooling:"
	@$(ANSIBLE) --version | head -n 1 || true
	@$(ANSIBLE_LINT) --version || true
	@$(YAMLLINT) --version || true
	@$(MOLECULE) --version || true
	@echo ""
	@echo "📦 Installed collections (showing potential duplicates):"
	@$(VENV_DIR)/bin/ansible-galaxy collection list 2>/dev/null | grep -E 'code3tech\\.devtools|community\\.docker|containers\\.podman' || true
	@echo ""
	@echo "💡 If you see multiple versions above, clean local installs and reinstall into a single path:";
	@echo "   - Remove: ~/.ansible/collections/ansible_collections/code3tech/devtools (and other duplicates)";
	@echo "   - Then run: make clean && make install-collection";

test: ## Test all roles with Molecule
	@echo "🧪 Testing all roles..."
	@for role_dir in roles/*/; do \
		role_name=$$(basename "$$role_dir"); \
		if [ -d "$$role_dir/molecule" ]; then \
			echo "Testing $$role_name..."; \
			(cd "$$role_dir" && $(MOLECULE_ABS) test) || exit 1; \
		fi \
	done
	@echo "✅ All tests passed!"

build: ## Build collection tarball
	@echo "📦 Building collection..."
	@$(ANSIBLE_GALAXY) collection build --force
	@echo "✅ Collection built: $(COLLECTION_FILE)"

install-collection: ## Install collection locally
	@if [ ! -f "$(COLLECTION_FILE)" ]; then \
		echo "📦 Collection not found, building..."; \
		$(MAKE) build; \
	fi
	@echo "📥 Installing collection locally..."
	@$(ANSIBLE_GALAXY) collection install $(COLLECTION_FILE) --force
	@echo "✅ Collection installed!"

publish: ## Build and publish collection to Galaxy (requires GALAXY_API_KEY)
	@if [ ! -f "$(COLLECTION_FILE)" ]; then \
		echo "📦 Collection not found, building..."; \
		$(MAKE) build; \
	fi
	@echo "🚀 Publishing collection to Ansible Galaxy..."
	@$(ANSIBLE_GALAXY) collection publish $(COLLECTION_FILE) --api-key=$(GALAXY_API_KEY)
	@echo "✅ Collection published!"

clean: ## Clean build artifacts
	@echo "🧹 Cleaning build artifacts..."
	@rm -rf $(COLLECTION_NAMESPACE)-$(COLLECTION_NAME)-*.tar.gz
	@rm -rf collections/
	@rm -rf .ansible/
	@rm -rf roles/*/molecule/*/.cache
	@rm -rf roles/*/molecule/*/.molecule
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@echo "✅ Clean complete!"
