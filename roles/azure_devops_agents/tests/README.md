# Azure DevOps Agents - Tests

This directory contains basic Ansible tests for the azure_devops_agents role.

## Running Tests

### Using Molecule (Recommended)

```bash
cd roles/azure_devops_agents
molecule test
```

### Using ansible-playbook

```bash
ansible-playbook -i tests/inventory tests/test.yml
```
