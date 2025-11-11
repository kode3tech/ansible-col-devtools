.PHONY: help install lint test clean build install-collection

# Variables
VENV_DIR = .venv
PYTHON = $(VENV_DIR)/bin/python
PIP = $(VENV_DIR)/bin/pip
ANSIBLE = $(VENV_DIR)/bin/ansible
ANSIBLE_GALAXY = $(VENV_DIR)/bin/ansible-galaxy
ANSIBLE_LINT = $(VENV_DIR)/bin/ansible-lint
YAMLLINT = $(VENV_DIR)/bin/yamllint
MOLECULE = $(VENV_DIR)/bin/molecule

COLLECTION_NAMESPACE = kode3tech
COLLECTION_NAME = devtools
COLLECTION_VERSION = $(shell grep '^version:' galaxy.yml | awk '{print $$2}')
COLLECTION_FILE = $(COLLECTION_NAMESPACE)-$(COLLECTION_NAME)-$(COLLECTION_VERSION).tar.gz

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
	@$(PYTHON) --version
	@$(ANSIBLE) --version | head -n 1
	@$(ANSIBLE_LINT) --version
	@$(MOLECULE) --version
	@$(YAMLLINT) --version
	@echo ""
	@echo "Collection: $(COLLECTION_NAMESPACE).$(COLLECTION_NAME) v$(COLLECTION_VERSION)"

lint: ## Run linters (yamllint and ansible-lint)
	@echo "🔍 Running yamllint..."
	@$(YAMLLINT) .
	@echo ""
	@echo "🔍 Running ansible-lint..."
	@$(ANSIBLE_LINT)

lint-yaml: ## Run yamllint only
	@$(YAMLLINT) .

lint-ansible: ## Run ansible-lint only
	@$(ANSIBLE_LINT)

test-docker: ## Test Docker role
	@echo "🧪 Testing Docker role..."
	@cd roles/docker && $(MOLECULE) test

test-podman: ## Test Podman role
	@echo "🧪 Testing Podman role..."
	@cd roles/podman && $(MOLECULE) test

test-all: ## Test all roles
	@echo "🧪 Testing all roles..."
	@cd roles/docker && $(MOLECULE) test
	@cd roles/podman && $(MOLECULE) test

build: ## Build collection tarball
	@echo "📦 Building collection..."
	@$(ANSIBLE_GALAXY) collection build --force
	@echo "✅ Collection built: $(COLLECTION_FILE)"

install-collection: build ## Install collection locally
	@echo "📥 Installing collection locally..."
	@$(ANSIBLE_GALAXY) collection install $(COLLECTION_FILE) --force
	@echo "✅ Collection installed!"

publish: build ## Build and publish collection to Galaxy (requires GALAXY_API_KEY)
	@echo "🚀 Publishing collection to Ansible Galaxy..."
	@$(ANSIBLE_GALAXY) collection publish $(COLLECTION_FILE) --api-key=$(GALAXY_API_KEY)
	@echo "✅ Collection published!"

clean: ## Clean build artifacts
	@echo "🧹 Cleaning build artifacts..."
	@rm -rf $(COLLECTION_NAMESPACE)-$(COLLECTION_NAME)-*.tar.gz
	@rm -rf roles/*/molecule/*/.cache
	@rm -rf roles/*/molecule/*/.molecule
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@echo "✅ Clean complete!"

clean-all: clean ## Clean all (including venv)
	@echo "🧹 Cleaning virtual environment..."
	@rm -rf $(VENV_DIR)
	@echo "✅ Full clean complete!"

docs: ## Generate documentation
	@echo "� Generating documentation..."
	@echo "Documentation available in README.md and roles/*/README.md"

example-setup: ## Run example playbook (setup-dev-environment)
	@$(ANSIBLE) playbooks/setup-dev-environment.yml -i inventory.example

example-docker: ## Run example playbook (install-docker)
	@$(ANSIBLE) playbooks/install-docker.yml -i inventory.example

example-podman: ## Run example playbook (install-podman)
	@$(ANSIBLE) playbooks/install-podman.yml -i inventory.example
