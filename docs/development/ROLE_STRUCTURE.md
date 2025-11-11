# Docker Role Structure

## Overview

A role `docker` foi criada usando `ansible-galaxy init` e customizada para instalar e configurar o Docker em servidores Linux.

## Structure

```text
docker/
├── README.md                   # Documentação da role
├── defaults/
│   └── main.yml               # Variáveis padrão configuráveis
├── files/                     # Arquivos estáticos (vazio)
├── handlers/
│   └── main.yml               # Handler para restart do Docker
├── meta/
│   └── main.yml               # Metadados da role (autor, licença, plataformas)
├── tasks/
│   ├── main.yml               # Tasks principais
│   ├── setup-Debian.yml       # Tasks específicas para Debian/Ubuntu
│   └── setup-RedHat.yml       # Tasks específicas para RHEL/CentOS
├── templates/                 # Templates Jinja2 (vazio)
├── tests/
│   ├── inventory              # Inventário de teste
│   └── test.yml               # Playbook de teste básico
└── vars/
    ├── Debian.yml             # Variáveis específicas Debian/Ubuntu
    ├── main.yml               # Variáveis gerais
    └── RedHat.yml             # Variáveis específicas RHEL/CentOS
```

## Features

### Supported Platforms

- **Ubuntu**: 22.04 (Jammy), 24.04 (Noble), 25.04 (Plucky)
- **Debian**: 11 (Bullseye), 12 (Bookworm), 13 (Trixie)
- **RHEL/CentOS**: 9, 10

### Configurable Variables

See `docker/defaults/main.yml` for all available variables:

- `docker_edition`: Docker edition (ce = Community Edition)
- `docker_packages`: List of packages to install
- `docker_users`: Users to add to docker group
- `docker_daemon_config`: Docker daemon JSON configuration
- `docker_service_enabled`: Enable Docker on boot
- `docker_service_state`: Docker service state (started/stopped)
- `docker_configure_repo`: Whether to configure Docker repository

### Tasks Overview

1. **OS Detection**: Includes OS-specific variables and tasks
2. **Prerequisites**: Installs required packages
3. **Repository Setup**: Configures Docker official repository
4. **Package Installation**: Installs Docker packages
5. **Daemon Configuration**: Configures `/etc/docker/daemon.json`
6. **Service Management**: Ensures Docker service is running
7. **User Management**: Adds users to docker group

### Handlers

- `restart docker`: Restarts Docker service when configuration changes

## Validation

All files passed validation:

```bash
# Ansible-lint
ansible-lint docker/
# ✅ Passed: 0 failure(s), 0 warning(s)

# Yamllint
yamllint docker/
# ✅ No errors

# Example playbook
ansible-lint examples/install-docker.yml
# ✅ Passed: 0 failure(s), 0 warning(s)
```

## Usage

See `examples/install-docker.yml` for a complete example.

Basic usage:

```yaml
- hosts: servers
  become: true
  roles:
    - docker
```

With custom configuration:

```yaml
- hosts: servers
  become: true
  vars:
    docker_users:
      - myuser
    docker_daemon_config:
      log-driver: "json-file"
      storage-driver: overlay2
  roles:
    - docker
```

## Testing

To test the role with Molecule (to be configured):

```bash
cd docker/
molecule init scenario --driver-name docker
molecule test
```

## Next Steps

1. Configure Molecule for automated testing
2. Add more examples (Docker Compose, Swarm, etc.)
3. Add templates for custom daemon configurations
4. Add support for Docker plugins
5. Add CI/CD pipeline

## Compliance

- ✅ Ansible-lint (production profile)
- ✅ Yamllint
- ✅ FQCN (Fully Qualified Collection Names)
- ✅ Proper naming conventions
- ✅ Idempotent tasks
