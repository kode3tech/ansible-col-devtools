# Molecule Testing Guide

## 📋 Overview

This document explains how Molecule tests work and what are the limitations of the Docker-in-Docker (DinD) environment.

## 🐳 Test Environment

### Tested Platforms
- **Ubuntu 22.04** (geerlingguy/docker-ubuntu2204-ansible)
- **Debian 12** (geerlingguy/docker-debian12-ansible)
- **Rocky Linux 9** (geerlingguy/docker-rockylinux9-ansible)

### Docker-in-Docker (DinD)

Molecule tests run **Docker/Podman INSIDE privileged Docker containers**. This has some implications:

**Advantages:**
- ✅ Fast and isolated tests
- ✅ Doesn't affect the host
- ✅ Multiple distros in parallel
- ✅ CI/CD friendly

**Limitations:**
- ⚠️ Limited storage drivers (usually `vfs` instead of `overlay2`)
- ⚠️ Performance doesn't represent real environment
- ⚠️ Some advanced features may not work
- ⚠️ Rootless Podman behaves differently

## 🎯 What the Tests Validate

### ✅ Configuration Validation
Molecule tests focus on **validating that configurations are correct**:

- Configuration files created correctly
- Valid syntax (JSON, TOML, etc.)
- Appropriate permissions
- Services enabled and running
- Users and groups configured
- Repositories and GPG keys installed

### ❌ What is NOT Tested
The tests **DO NOT measure real performance** because:

- DinD adds significant overhead
- Storage drivers are different (vfs vs overlay2)
- Host kernel limitations
- Resources shared with sibling containers

## 📊 Performance: Molecule vs. Production

### Docker Storage Driver

| Environment | Storage Driver | Performance |
|-------------|---------------|-------------|
| **Production** | overlay2 | 100% (baseline) |
| **Molecule (DinD)** | vfs | 30-40% (slow, but compatible) |

**Why?**
- DinD cannot reliably use overlay2
- The host kernel is already using overlay2 for the Molecule container
- Cannot efficiently do overlay-over-overlay

### Molecule-Specific Configurations

#### Docker (`roles/docker/molecule/default/converge.yml`)
```yaml
# Override default storage-driver to let Docker auto-detect
docker_daemon_config:
  log-driver: "json-file"
  log-opts:
    max-size: "10m"
    max-file: "3"
  # storage-driver: removed for DinD compatibility
```

**In production** (`defaults/main.yml`):
```yaml
docker_daemon_config:
  log-driver: "json-file"
  log-opts:
    max-size: "10m"
    max-file: "3"
  storage-driver: "overlay2"  # ✅ Explicit for performance
```

#### Podman
Podman in Molecule runs in rootless mode inside privileged containers, which is a unique scenario. In production, rootless Podman has direct access to XDG_RUNTIME_DIR and subuid/subgid on the host.

## 🧪 Running the Tests

### Prerequisites
```bash
# Activate virtual environment
source activate.sh

# Install dependencies (if needed)
pip install -r requirements.txt
```

### Docker Role
```bash
cd roles/docker
molecule test
```

### Podman Role
```bash
cd roles/podman
molecule test
```

### Converge Only (without destroy)
```bash
molecule converge
```

### Verify Only (with existing containers)
```bash
molecule verify
```

## 📝 Test Structure

### Installation Tests
- Packages installed
- Services running and enabled
- Correct versions

### Configuration Tests
- Configuration files exist
- Valid syntax (JSON, TOML)
- Correct permissions
- Security settings

### Performance Tests (Config Validation)
- ✅ `daemon.json` has `storage-driver` configured (if applicable)
- ✅ `storage.conf` has correct optimizations
- ✅ crun installed (optional)
- ✅ Appropriate logging settings
- ❌ **We DON'T measure real performance** (DinD is not representative)

### Security Tests
- Insecure registries configured
- GPG keys installed correctly
- Repositories authenticated

## 🔍 Interpreting Results

### ✅ Test Passed
Means that the **configuration is correct**, not that performance is optimal.

### ❌ Test Failed
May indicate:
1. Incorrect configuration (real problem)
2. DinD incompatibility (may work in production)
3. Test environment limitation

## 🚀 Production Validation

To validate real performance, use the example playbooks:

```bash
# Test in real environment
ansible-playbook -i inventory.ini playbooks/docker/install-docker.yml

# Validate configurations
ansible -i inventory.ini all -m shell \
  -a 'docker info | grep "Storage Driver"'

ansible -i inventory.ini all -m shell \
  -a 'cat /etc/containers/storage.conf | grep "driver ="'
```

## 📈 Expected Performance Gains

### In Production (NOT in Molecule!)

| Optimization | Expected Gain | Where to Test |
|--------------|---------------|---------------|
| Docker overlay2 | +15-30% I/O | Real hosts |
| Docker crun | +20-30% startup | Real hosts |
| Podman overlay+metacopy | +30-50% I/O | Real hosts |
| Podman crun | +20-30% startup | Real hosts |
| Podman parallel copies | +200-300% pull | Real hosts |

**⚠️ IMPORTANT:** These gains **are NOT measurable in Molecule** due to DinD limitations!

## 🎓 Lessons Learned

### 1. Molecule is for CI/CD, not benchmarks
Use Molecule to ensure the role **works**, not to measure **how fast** it works.

### 2. DinD has known limitations
Storage drivers, networking, and performance are different from the real world.

### 3. Conditional tests are important
```python
# Example: don't force overlay2 in Molecule
if "storage-driver" in daemon_config:
    assert daemon_config["storage-driver"] == "overlay2"
# If not configured, Docker auto-detected (vfs in DinD)
```

### 4. Always validate in real environment
Molecule is the first line of defense, not the last.

## 🔗 References

- [Molecule Documentation](https://molecule.readthedocs.io/)
- [Docker Storage Drivers](https://docs.docker.com/storage/storagedriver/)
- [Podman Storage Configuration](https://docs.podman.io/en/latest/markdown/podman-storage.conf.5.html)
- [Rootless Podman](https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md)

---

[← Back to Testing Documentation](README.md)

**Summary:** Use Molecule to validate configurations, not to measure performance. Test performance on real hosts! 🚀

## 🐳 Ambiente de Teste

### Plataformas Testadas
- **Ubuntu 22.04** (geerlingguy/docker-ubuntu2204-ansible)
- **Debian 12** (geerlingguy/docker-debian12-ansible)
- **Rocky Linux 9** (geerlingguy/docker-rockylinux9-ansible)

### Docker-in-Docker (DinD)

Os testes do Molecule rodam **Docker/Podman DENTRO de containers Docker** privilegiados. Isso tem algumas implicações:

**Vantagens:**
- ✅ Testes rápidos e isolados
- ✅ Não afeta o host
- ✅ Múltiplas distros em paralelo
- ✅ CI/CD friendly

**Limitações:**
- ⚠️ Storage drivers limitados (geralmente `vfs` ao invés de `overlay2`)
- ⚠️ Performance não representa ambiente real
- ⚠️ Algumas features avançadas podem não funcionar
- ⚠️ Rootless Podman tem comportamento diferente

## 🎯 O Que os Testes Validam

### ✅ Validação de Configuração
Os testes do Molecule focam em **validar que as configurações estão corretas**:

- Arquivos de configuração criados corretamente
- Sintaxe válida (JSON, TOML, etc.)
- Permissões adequadas
- Serviços habilitados e rodando
- Usuários e grupos configurados
- Repositórios e GPG keys instalados

### ❌ O Que NÃO É Testado
Os testes **NÃO medem performance real** porque:

- DinD adiciona overhead significativo
- Storage drivers são diferentes (vfs vs overlay2)
- Limitações do kernel do host
- Recursos compartilhados com containers irmãos

## 📊 Performance: Molecule vs. Produção

### Docker Storage Driver

| Ambiente | Storage Driver | Performance |
|----------|---------------|-------------|
| **Produção** | overlay2 | 100% (baseline) |
| **Molecule (DinD)** | vfs | 30-40% (lento, mas compatível) |

**Por quê?**
- DinD não consegue usar overlay2 de forma confiável
- O kernel do host já está usando overlay2 para o container Molecule
- Não é possível fazer overlay-sobre-overlay de forma eficiente

### Configurações Específicas do Molecule

#### Docker (`roles/docker/molecule/default/converge.yml`)
```yaml
# Override default storage-driver to let Docker auto-detect
docker_daemon_config:
  log-driver: "json-file"
  log-opts:
    max-size: "10m"
    max-file: "3"
  # storage-driver: removed for DinD compatibility
```

**Em produção** (`defaults/main.yml`):
```yaml
docker_daemon_config:
  log-driver: "json-file"
  log-opts:
    max-size: "10m"
    max-file: "3"
  storage-driver: "overlay2"  # ✅ Explicit for performance
```

#### Podman
Podman no Molecule roda em modo rootless dentro de containers privilegiados, que é um cenário único. Em produção, rootless Podman tem acesso direto ao XDG_RUNTIME_DIR e subuid/subgid do host.

## 🧪 Executando os Testes

### Pré-requisitos
```bash
# Ativar ambiente virtual
source activate.sh

# Instalar dependências (se necessário)
pip install -r requirements.txt
```

### Docker Role
```bash
cd roles/docker
molecule test
```

### Podman Role
```bash
cd roles/podman
molecule test
```

### Apenas Convergência (sem destroy)
```bash
molecule converge
```

### Apenas Testes (com containers existentes)
```bash
molecule verify
```

## 📝 Estrutura dos Testes

### Testes de Instalação
- Pacotes instalados
- Serviços rodando e habilitados
- Versões corretas

### Testes de Configuração
- Arquivos de configuração existem
- Sintaxe válida (JSON, TOML)
- Permissões corretas
- Configurações de segurança

### Testes de Performance (Validação de Config)
- ✅ `daemon.json` tem `storage-driver` configurado (se aplicável)
- ✅ `storage.conf` tem otimizações corretas
- ✅ crun instalado (opcional)
- ✅ Configurações de logging adequadas
- ❌ **NÃO medimos performance real** (DinD não é representativo)

### Testes de Segurança
- Insecure registries configurados
- GPG keys instalados corretamente
- Repositórios autenticados

## 🔍 Interpretando Resultados

### ✅ Teste Passou
Significa que a **configuração está correta**, não que a performance é ótima.

### ❌ Teste Falhou
Pode indicar:
1. Configuração incorreta (problema real)
2. Incompatibilidade DinD (pode funcionar em produção)
3. Limitação do ambiente de teste

## 🚀 Validação em Produção

Para validar performance real, use os playbooks de exemplo:

```bash
# Testar em ambiente real
ansible-playbook -i inventory.ini playbooks/docker/install-docker.yml

# Validar configurações
ansible -i inventory.ini all -m shell \
  -a 'docker info | grep "Storage Driver"'

ansible -i inventory.ini all -m shell \
  -a 'cat /etc/containers/storage.conf | grep "driver ="'
```

## 📈 Ganhos de Performance Esperados

### Em Produção (NÃO no Molecule!)

| Otimização | Ganho Esperado | Onde Testar |
|-----------|----------------|-------------|
| Docker overlay2 | +15-30% I/O | Hosts reais |
| Docker crun | +20-30% startup | Hosts reais |
| Podman overlay+metacopy | +30-50% I/O | Hosts reais |
| Podman crun | +20-30% startup | Hosts reais |
| Podman parallel copies | +200-300% pull | Hosts reais |

**⚠️ IMPORTANTE:** Estes ganhos **NÃO são mensuráveis no Molecule** devido às limitações do DinD!

## 🎓 Lições Aprendidas

### 1. Molecule é para CI/CD, não benchmarks
Use Molecule para garantir que a role **funciona**, não para medir **quão rápido** funciona.

### 2. DinD tem limitações conhecidas
Storage drivers, networking e performance são diferentes do mundo real.

### 3. Testes condicionais são importantes
```python
# Exemplo: não forçar overlay2 no Molecule
if "storage-driver" in daemon_config:
    assert daemon_config["storage-driver"] == "overlay2"
# Se não está configurado, Docker auto-detectou (vfs no DinD)
```

### 4. Sempre valide em ambiente real
Molecule é a primeira linha de defesa, não a última.

## 🔗 Referências

- [Molecule Documentation](https://molecule.readthedocs.io/)
- [Docker Storage Drivers](https://docs.docker.com/storage/storagedriver/)
- [Podman Storage Configuration](https://docs.podman.io/en/latest/markdown/podman-storage.conf.5.html)
- [Rootless Podman](https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md)

---

**Resumo:** Use Molecule para validar configurações, não para medir performance. Teste performance em hosts reais! 🚀
