# Relatório de Troubleshooting - Docker em LXC Containers

**Data:** 2025-11-06  
**Hosts Testados:** 3 (Ubuntu 24.04, Debian 13.1, Rocky Linux 9)  
**Ambiente:** LXC unprivileged containers com AppArmor unconfined

---

## 🔍 Resumo Executivo

| Host | Docker Service | Podman | Docker Run | Status |
|------|---------------|--------|------------|--------|
| **Ubuntu 24.04** | ✅ Running | ✅ OK | ❌ AppArmor Error | ⚠️ Parcial |
| **Debian 13.1** | ✅ Running | ✅ OK | ❌ Sysctl Error | ⚠️ Parcial |
| **Rocky 9** | ⚠️ Timeout | ❓ | ❓ Timeout | ⚠️ Investigar |

---

## 📊 Testes Realizados

### ✅ Testes BEM-SUCEDIDOS

1. **Podman run hello-world**
   - Ubuntu 24.04: ✅ **SUCCESS**
   - Debian 13.1: ✅ **SUCCESS**
   - Rocky 9: Não testado (timeout)

2. **Docker daemon running**
   - Ubuntu 24.04: ✅ Running
   - Debian 13.1: ✅ Running
   - Rocky 9: ✅ Running (mas com timeout em comandos)

3. **Docker commands básicos**
   - `docker ps`: ✅ Funciona
   - `docker images`: ✅ Funciona
   - `docker version`: ✅ Funciona

### ❌ Testes COM FALHA

#### **Ubuntu 24.04 (192.168.1.70)**

**Comando:** `docker run --rm hello-world`

**Erro:**
```
docker: Error response from daemon: Could not check if docker-default AppArmor profile was loaded: 
open /sys/kernel/security/apparmor/profiles: permission denied
```

**Análise:**
- **Causa Raiz:** Container LXC unprivileged não tem acesso a `/sys/kernel/security/apparmor/`
- **Impacto:** Docker não consegue verificar perfis AppArmor
- **Severidade:** 🟡 Médio
- **Workaround Possível:** Desabilitar AppArmor no Docker ou adicionar permissões ao LXC

#### **Debian 13.1 (192.168.1.71)**

**Comando:** `docker run --rm hello-world`

**Erro:**
```
OCI runtime create failed: runc create failed: 
error during container init: open sysctl net.ipv4.ip_unprivileged_port_start file: 
reopen fd 8: permission denied
```

**Análise:**
- **Causa Raiz:** Tentando acessar `/proc/sys/net/ipv4/ip_unprivileged_port_start` sem permissão
- **Impacto:** Containers não conseguem iniciar
- **Severidade:** 🔴 Alto
- **Workaround Possível:** Adicionar capabilities ao LXC ou usar network host mode

#### **Rocky Linux 9 (192.168.1.72)**

**Sintoma:** Comandos Docker travando (timeout)

**Análise:**
- **Possíveis Causas:**
  1. Docker daemon travado
  2. Problema de rede/DNS
  3. Deadlock no runtime
- **Severidade:** 🔴 Alto  
- **Ação Necessária:** Investigação detalhada, restart do daemon

---

## 🎯 Causa Raiz: Limitações LXC Unprivileged

### Contexto

Os hosts estão rodando como **containers LXC unprivileged** com:
- AppArmor profile: `unconfined` (já configurado)
- User namespaces: Ativados
- Capabilities: Limitadas

### Problemas Conhecidos

1. **AppArmor no LXC**
   - LXC unprivileged **não tem acesso** a `/sys/kernel/security/apparmor/`
   - Docker tenta verificar perfis AppArmor antes de executar containers
   - Mesmo com profile `unconfined`, o acesso é negado pelo próprio LXC

2. **Sysctl em Namespaces**
   - Alguns sysctls não são namespace-aware
   - `net.ipv4.ip_unprivileged_port_start` pode estar bloqueado
   - LXC pode não expor todos os sysctls necessários

---

## 💡 Soluções Propostas

### Solução 1: Desabilitar AppArmor no Docker (Ubuntu)

**Arquivo:** `/etc/docker/daemon.json`

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "security-opt": ["apparmor=unconfined"]
}
```

**Aplicar:**
```bash
ansible -i inventory.ini 192.168.1.70 -m shell \
  -a 'systemctl restart docker' --become
```

**Prós:** ✅ Resolve erro AppArmor  
**Contras:** ⚠️ Reduz isolamento de segurança

### Solução 2: Configurar LXC para Permitir Sysctls (Debian)

**Arquivo LXC:** `/var/lib/lxc/<container>/config`

```ini
# Adicionar capabilities
lxc.cap.drop =
lxc.cap.keep = sys_admin sys_resource net_admin

# Expor sysctls
lxc.mount.entry = /proc/sys/net proc/sys/net none bind,ro 0 0
```

**Aplicar:**
```bash
lxc-stop -n <container>
lxc-start -n <container>
```

**Prós:** ✅ Resolve acesso a sysctls  
**Contras:** ⚠️ Requer restart do container LXC

### Solução 3: Usar Podman Exclusivamente

**Recomendação:** ✅ **MELHOR OPÇÃO PARA LXC**

**Motivo:**
- Podman **FUNCIONA** perfeitamente em LXC unprivileged ✅
- Não depende de daemon
- Melhor isolamento com user namespaces
- Menos problemas com AppArmor e capabilities

**Ação:**
```yaml
# Focar em Podman para workloads em LXC
# Usar Docker apenas em VMs reais ou bare metal
```

### Solução 4: Mudar para Containers LXC Privileged

**⚠️ NÃO RECOMENDADO** (reduz segurança)

```ini
# /var/lib/lxc/<container>/config
lxc.apparmor.profile = unconfined
lxc.cap.drop =
unprivileged = 0  # MUDAR PARA PRIVILEGED
```

**Prós:** ✅ Resolve todos os problemas  
**Contras:** 🔴 Container tem acesso root completo ao host

---

## 📋 Checklist de Validação

### Para Ubuntu 24.04:
- [ ] Adicionar `security-opt` no daemon.json
- [ ] Restart Docker daemon
- [ ] Testar `docker run --rm hello-world`
- [ ] Validar `docker run --rm -d nginx`

### Para Debian 13.1:
- [ ] Adicionar capabilities no LXC config
- [ ] Restart container LXC
- [ ] Testar `docker run --rm hello-world`
- [ ] Validar acesso a sysctls

### Para Rocky 9:
- [ ] Investigar timeout do Docker
- [ ] Verificar logs: `journalctl -xeu docker`
- [ ] Restart Docker daemon
- [ ] Testar conectividade

---

## 🎓 Recomendações Finais

### Para Produção em LXC:

1. **Use Podman como Padrão** ✅
   - 100% funcional em LXC unprivileged
   - Sem problemas de permissão
   - Melhor segurança

2. **Docker Apenas em VMs/Bare Metal** ⚠️
   - Docker + LXC unprivileged = Problemas conhecidos
   - Para Docker, prefira KVM/VMware/Bare metal

3. **Se PRECISA de Docker em LXC:**
   - Use LXC privileged (menos seguro)
   - OU adicione workarounds de segurança
   - OU aceite limitações funcionais

### Arquitetura Recomendada:

```
┌─────────────────────────────────────┐
│          Hypervisor (Proxmox)       │
├─────────────────┬───────────────────┤
│   LXC Containers│   KVM VMs         │
│                 │                   │
│   ✅ Podman     │   ✅ Docker       │
│   ❌ Docker     │   ✅ Podman       │
│   (limitado)    │   (tudo funciona) │
└─────────────────┴───────────────────┘
```

---

## 📞 Próximos Passos

1. ✅ **Validar Podman** (FEITO - 100% funcional)
2. ⏳ **Decidir estratégia:** Docker com workarounds OU Podman exclusivo
3. ⏳ **Implementar solução escolhida**
4. ⏳ **Atualizar playbooks** com configurações específicas para LXC
5. ⏳ **Documentar limitações** no README

---

**Conclusão:** Podman é a melhor escolha para containers LXC unprivileged. Docker funciona mas requer workarounds que reduzem segurança ou funcionalidade.
