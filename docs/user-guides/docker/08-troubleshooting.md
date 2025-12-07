# Troubleshooting

Complete troubleshooting guide for Docker role with common errors, diagnostics, and solutions.

---

## 📋 Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Installation Issues](#installation-issues)
- [Service Issues](#service-issues)
- [Permission Issues](#permission-issues)
- [Registry Authentication](#registry-authentication)
- [Storage Issues](#storage-issues)
- [Network Issues](#network-issues)
- [Container Issues](#container-issues)
- [Variable Reference](#variable-reference)

---

## Quick Diagnostics

### Essential Commands

```bash
# Docker service status
sudo systemctl status docker

# Docker info
docker info

# Docker version
docker version

# Check daemon logs
sudo journalctl -u docker -n 50

# Test functionality
docker run --rm hello-world

# Check daemon config
cat /etc/docker/daemon.json | jq
```

### Health Check Script

```bash
#!/bin/bash
echo "=== Docker Health Check ==="

echo -e "\n1. Service Status:"
systemctl is-active docker && echo "✅ Running" || echo "❌ Not running"

echo -e "\n2. Docker Version:"
docker version --format '{{.Server.Version}}' 2>/dev/null || echo "❌ Cannot connect"

echo -e "\n3. Storage Driver:"
docker info --format '{{.Driver}}' 2>/dev/null || echo "❌ Unknown"

echo -e "\n4. Disk Usage:"
docker system df 2>/dev/null || echo "❌ Cannot check"

echo -e "\n5. Test Container:"
docker run --rm alpine echo "✅ Containers work" 2>/dev/null || echo "❌ Container failed"
```

---

## Installation Issues

### Repository Not Found

```
E: The repository 'https://download.docker.com/linux/ubuntu focal Release' does not have a Release file
```

**Causes:**
- Unsupported distribution version
- Network issues
- Repository key issues

**Solutions:**

1. Check distribution support:
   ```bash
   lsb_release -cs  # Should match supported versions
   ```

2. Re-add repository:
   ```bash
   sudo rm /etc/apt/sources.list.d/docker.list
   # Re-run playbook
   ```

3. Check network:
   ```bash
   curl -I https://download.docker.com/linux/ubuntu/
   ```

### GPG Key Error

```
The following signatures couldn't be verified because the public key is not available
```

**Solution:**
```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
```

### Package Conflicts

```
docker-ce conflicts with docker.io
```

**Solution:**
```bash
sudo apt remove docker docker.io containerd runc
sudo apt autoremove
# Re-run playbook
```

---

## Service Issues

### Docker Won't Start

```
Job for docker.service failed because the control process exited with error code
```

**Diagnostics:**
```bash
sudo journalctl -xeu docker
sudo dockerd --debug
```

**Common causes:**

1. **Invalid daemon.json:**
   ```bash
   # Validate JSON
   cat /etc/docker/daemon.json | jq
   
   # Fix and restart
   sudo systemctl restart docker
   ```

2. **Storage driver issue:**
   ```bash
   # Check kernel support
   modprobe overlay
   lsmod | grep overlay
   ```

3. **Port conflict:**
   ```bash
   sudo netstat -tulpn | grep 2375
   ```

### Docker Service Stops Unexpectedly

**Diagnostics:**
```bash
sudo journalctl -u docker --since "1 hour ago"
dmesg | grep -i docker
```

**Common causes:**
- OOM killer (out of memory)
- Disk full
- Corrupted storage

**Solutions:**
```bash
# Check memory
free -h

# Check disk
df -h /var/lib/docker

# Clean up
docker system prune -af
```

---

## Permission Issues

### Permission Denied to Docker Socket

```
Got permission denied while trying to connect to the Docker daemon socket
```

**Cause:** User not in docker group.

**Solution:**
```yaml
# In playbook
docker_users:
  - myuser
```

Or manually:
```bash
sudo usermod -aG docker $USER
newgrp docker  # Or logout/login
```

### Config File Permission Denied

```
error getting credentials - err: exit status 1, out: ``
```

**Cause:** `~/.docker/config.json` owned by root.

**Solution:** Role handles this automatically. Manual fix:
```bash
sudo chown -R $USER:$USER ~/.docker
chmod 700 ~/.docker
chmod 600 ~/.docker/config.json
```

### Cannot Write to Data Directory

```
error initializing graphdriver: mkdir /data/docker: permission denied
```

**Solution:**
```bash
sudo mkdir -p /data/docker
sudo chmod 711 /data/docker
sudo chown root:root /data/docker
```

---

## Registry Authentication

### Unauthorized Error

```
Error response from daemon: unauthorized: authentication required
```

**Causes & Solutions:**

1. **Wrong registry URL for Docker Hub:**
   ```yaml
   # ❌ Wrong
   registry: "docker.io"
   
   # ✅ Correct
   registry: "https://index.docker.io/v1/"
   ```

2. **Expired token:**
   - Generate new token at registry provider
   - Update Ansible Vault

3. **Wrong credentials:**
   ```bash
   # Test manually
   docker login registry.example.com
   ```

### Certificate Error

```
x509: certificate signed by unknown authority
```

**Solutions:**

1. Add to insecure registries:
   ```yaml
   docker_insecure_registries:
     - "registry.example.com:5000"
   ```

2. Install CA certificate:
   ```bash
   sudo cp ca.crt /usr/local/share/ca-certificates/
   sudo update-ca-certificates
   sudo systemctl restart docker
   ```

### Registry Not Reachable

```
dial tcp: lookup registry.example.com: no such host
```

**Diagnostics:**
```bash
# DNS
nslookup registry.example.com

# Network
curl -I https://registry.example.com/v2/

# Firewall
telnet registry.example.com 443
```

---

## Storage Issues

### No Space Left on Device

```
no space left on device
```

**Diagnostics:**
```bash
df -h /var/lib/docker
docker system df
```

**Solutions:**

1. Clean unused resources:
   ```bash
   docker system prune -af --volumes
   ```

2. Remove old images:
   ```bash
   docker image prune -a --filter "until=168h"
   ```

3. Move data directory:
   ```yaml
   docker_daemon_config:
     data-root: "/data/docker"  # Larger disk
   ```

### Storage Driver Mismatch

```
error initializing graphdriver: driver not supported
```

**Solution:**
```bash
# Check current driver
docker info | grep "Storage Driver"

# Ensure kernel support
modprobe overlay
cat /proc/filesystems | grep overlay
```

### Corrupted Storage

```
error mounting layer: invalid argument
```

**Nuclear option (data loss!):**
```bash
sudo systemctl stop docker
sudo rm -rf /var/lib/docker
sudo systemctl start docker
```

**Better approach:**
```bash
# Backup running containers first
docker export container_name > backup.tar

# Then clean
sudo systemctl stop docker
sudo rm -rf /var/lib/docker/overlay2/*
sudo systemctl start docker
```

---

## Network Issues

### DNS Resolution Failed

```
Temporary failure in name resolution
```

**Solutions:**

1. Configure DNS in daemon:
   ```yaml
   docker_daemon_config:
     dns:
       - "8.8.8.8"
       - "8.8.4.4"
   ```

2. Check host DNS:
   ```bash
   cat /etc/resolv.conf
   nslookup google.com
   ```

### Port Already in Use

```
Error starting userland proxy: listen tcp 0.0.0.0:80: bind: address already in use
```

**Diagnostics:**
```bash
sudo netstat -tulpn | grep :80
sudo lsof -i :80
```

**Solutions:**
- Stop conflicting service
- Use different port mapping

### Container Cannot Reach Internet

**Diagnostics:**
```bash
docker run --rm alpine ping -c 3 8.8.8.8
docker run --rm alpine ping -c 3 google.com
```

**Solutions:**

1. Check IP forwarding:
   ```bash
   sysctl net.ipv4.ip_forward
   # Should be 1
   ```

2. Check iptables:
   ```bash
   sudo iptables -L -n | grep DOCKER
   ```

3. Restart Docker networking:
   ```bash
   docker network prune
   sudo systemctl restart docker
   ```

---

## Container Issues

### Container Exits Immediately

**Diagnostics:**
```bash
docker logs container_name
docker inspect container_name | jq '.[0].State'
```

**Common causes:**
- Command not found
- Missing dependencies
- Permission issues inside container

### Out of Memory

```
container killed due to OOM
```

**Diagnostics:**
```bash
docker stats container_name
dmesg | grep -i oom
```

**Solutions:**
- Increase memory limit
- Optimize application
- Add swap

### High CPU Usage

**Diagnostics:**
```bash
docker stats
docker top container_name
```

**Solutions:**
- Set CPU limits
- Investigate application
- Check for infinite loops

---

## Variable Reference

### Complete Role Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `docker_edition` | string | `"ce"` | Docker edition (ce/ee) |
| `docker_packages` | list | See defaults | Packages to install |
| `docker_users` | list | `[]` | Users for docker group |
| `docker_daemon_config` | dict | See below | Daemon configuration |
| `docker_buildkit_enabled` | bool | `true` | Enable BuildKit |
| `docker_service_enabled` | bool | `true` | Enable service |
| `docker_service_state` | string | `started` | Service state |
| `docker_configure_repo` | bool | `true` | Configure Docker repo |
| `docker_insecure_registries` | list | `[]` | HTTP/self-signed registries |
| `docker_registries_auth` | list | `[]` | Registry authentication |

### Default Packages

```yaml
docker_packages:
  - docker-{{ docker_edition }}
  - docker-{{ docker_edition }}-cli
  - containerd.io
  - docker-buildx-plugin
  - docker-compose-plugin
```

### Default Daemon Configuration

```yaml
docker_daemon_config:
  log-driver: "json-file"
  log-opts:
    max-size: "10m"
    max-file: "3"
  storage-driver: "overlay2"
```

### Registry Authentication Format

```yaml
docker_registries_auth:
  - registry: "https://index.docker.io/v1/"  # Docker Hub
    username: "user"
    password: "{{ vault_token }}"
  - registry: "ghcr.io"  # GitHub
    username: "user"
    password: "{{ vault_github_token }}"
```

---

## FAQ

### Why does Docker Hub need a full URL?

Docker Hub uses a legacy API endpoint. The `community.docker.docker_login` module requires the full URL `https://index.docker.io/v1/` for proper authentication.

### Why is my login task showing "changed" every run?

The `docker_login` module doesn't have proper idempotency detection. As long as login succeeds, this is expected behavior.

### How do I use Docker in an LXC container?

Enable nesting in LXC configuration:
```
features: nesting=1
lxc.apparmor.profile: unconfined
```

### Should I use Docker or Podman?

| Use Case | Recommendation |
|----------|----------------|
| Production workloads | Docker (more mature) |
| Developer workstations | Podman (rootless) |
| CI/CD | Docker (better tooling) |
| Security-sensitive | Podman (no daemon) |

### How do I migrate from Docker to Podman?

Most commands are compatible:
```bash
alias docker=podman
```

For Compose:
```bash
podman-compose up -d
# or
podman compose up -d
```

---

## Getting Help

### Log Locations

| Log | Location |
|-----|----------|
| Docker daemon | `journalctl -u docker` |
| Container logs | `docker logs <container>` |
| System logs | `/var/log/syslog` or `/var/log/messages` |

### Useful Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Forum](https://forums.docker.com/)
- [Docker GitHub Issues](https://github.com/moby/moby/issues)

### Support

- **Bug Reports:** [GitHub Issues](https://github.com/kode3tech/ansible-col-devtools/issues)
- **Email:** suporte@code3.tech

---

[← Back to Docker Documentation](README.md) | [Previous: Performance & Security](07-performance-security.md)
