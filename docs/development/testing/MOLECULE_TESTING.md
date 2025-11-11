# Molecule Testing Guide

## 📋 Overview

Este documento explica como os testes do Molecule funcionam e quais são as limitações do ambiente Docker-in-Docker (DinD).

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
ansible-playbook -i inventory.ini playbooks/install-docker.yml

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
