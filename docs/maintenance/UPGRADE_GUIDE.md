# Guia de Atualização - v1.0.0 para v1.1.0

## ⚠️ AVISO IMPORTANTE - MUDANÇAS INCOMPATÍVEIS

### Podman: Separação de Arquivos de Configuração

A partir da **v1.1.0**, as configurações do Podman foram reorganizadas para seguir as melhores práticas oficiais:

#### O Que Mudou?

**Antes (v1.0.x):**
- Todas as configurações em `/etc/containers/storage.conf`
- Seções `[storage]` e `[engine]` no mesmo arquivo ❌

**Agora (v1.1.0+):**
- `/etc/containers/storage.conf`: Apenas `[storage]` e `[storage.options]` ✅
- `/etc/containers/containers.conf`: Apenas `[engine]` ✅

#### Por Quê Mudou?

A documentação oficial do Podman especifica:
- **`storage.conf`**: Configurações de armazenamento (driver, graphroot, mountopt)
- **`containers.conf`**: Configurações de runtime (crun, cgroup, parallel copies)

Misturar essas configurações causava:
- ⚠️ Warnings: `Failed to decode the keys ["engine" ...] from storage.conf`
- ❌ Erros: `database graph driver mismatch`

### 🔧 Como Atualizar

#### Opção 1: Atualização Automática (Recomendado)

```bash
# Install collection
ansible-galaxy collection install code3tech.devtools

# Run playbook
ansible-playbook -i inventory.ini playbooks/podman/install-podman.yml

# 2. Resetar storage do Podman (REMOVE containers/imagens!)
ansible -i inventory.ini all -m shell \
  -a 'rm -rf /var/lib/containers/storage/* /run/containers/storage/*' \
  --become

# 3. Verificar funcionamento
ansible -i inventory.ini all -m shell \
  -a 'podman info | grep -A3 "store:"' \
  --become
```

#### Opção 2: Atualização Manual

1. **Remover configurações `[engine]` de `storage.conf`:**
```bash
# Editar /etc/containers/storage.conf
# Remover seção [engine] completa
```

2. **Criar `/etc/containers/containers.conf`:**
```toml
[engine]
runtime = "crun"
events_logger = "file"
cgroup_manager = "systemd"
num_locks = 2048
image_parallel_copies = 10
```

3. **Resetar storage:**
```bash
rm -rf /var/lib/containers/storage/*
rm -rf /run/containers/storage/*
```

4. **Verificar:**
```bash
podman info
podman version
```

### 🚨 Impacto da Atualização

**⚠️ ATENÇÃO:** O reset do storage Podman **REMOVE**:
- ✗ Todos os containers
- ✗ Todas as imagens
- ✗ Todos os volumes
- ✗ Todas as redes personalizadas

**✅ NÃO afeta:**
- ✓ Configurações de registries
- ✓ Credenciais de login
- ✓ Usuários rootless configurados
- ✓ Configurações do Docker

### 📋 Checklist Pós-Atualização

```bash
# 1. Verificar versão do Podman
podman version

# 2. Verificar storage driver
podman info --format '{{.Store.GraphDriverName}}'
# Deve retornar: overlay

# 3. Verificar runtime
podman info --format '{{.Host.OCIRuntime.Name}}'
# Deve retornar: crun

# 4. Testar pull de imagem
podman pull alpine:latest

# 5. Testar execução de container
podman run --rm alpine echo "Podman funcionando!"

# 6. Verificar configurações
cat /etc/containers/storage.conf
cat /etc/containers/containers.conf
```

### 🐛 Problemas Conhecidos e Soluções

#### Erro: `database graph driver mismatch`

**Causa:** Storage antigo incompatível com novo driver

**Solução:**
```bash
# Resetar storage
rm -rf /var/lib/containers/storage/*
rm -rf /run/containers/storage/*

# Testar
podman info
```

#### Warning: `Failed to decode the keys ["engine" ...]`

**Causa:** Seção `[engine]` ainda está em `storage.conf`

**Solução:**
```bash
# Remover seção [engine] de storage.conf
sed -i '/^\[engine\]/,/^$/d' /etc/containers/storage.conf

# Executar playbook para criar containers.conf correto
ansible-playbook -i inventory.ini playbooks/install-podman.yml
```

#### Erro: `overlay is not supported`

**Causa:** Kernel muito antigo ou sem suporte a overlay em namespaces

**Solução:**
```yaml
# Usar vfs driver (mais lento mas compatível)
podman_storage_conf:
  storage:
    driver: "vfs"  # Trocar overlay por vfs
```

### 📈 Melhorias de Performance (v1.1.0)

Após a atualização, você terá:

| Recurso | Antes | Agora | Melhoria |
|---------|-------|-------|----------|
| **Storage Driver** | vfs/undefined | overlay + metacopy | +30-50% I/O |
| **Runtime** | runc | crun | +20-30% startup |
| **Image Pull** | serial | parallel (10 layers) | +200-300% |
| **Configurações** | Misturadas | Separadas | ✅ Sem warnings |

### 🔄 Rollback (Se Necessário)

Se encontrar problemas, você pode voltar para v1.0.x:

```bash
# 1. Checkout versão anterior
git checkout tags/v1.0.0

# 2. Executar playbook
ansible-playbook -i inventory.ini playbooks/podman/install-podman.ymlman.yml

# 3. Resetar storage (novamente)
ansible -i inventory.ini all -m shell \
  -a 'rm -rf /var/lib/containers/storage/*' \
  --become
```

### 📞 Suporte

Se encontrar problemas durante a atualização:

1. Verifique os logs: `journalctl -xeu podman`
2. Abra uma issue: https://github.com/kode3tech/ansible-col-devtools/issues
3. Email: suporte@kode3.tech

---

**Última atualização:** 2025-11-06  
**Versão alvo:** v1.1.0  
**Impacto:** ⚠️ ALTO (requer reset de storage)
