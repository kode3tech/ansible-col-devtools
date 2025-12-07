# Docker Role - Example Playbooks

Production-ready example playbooks demonstrating Docker role usage with performance optimizations.

## 📋 Available Examples

### [install-docker.yml](install-docker.yml)
**Purpose:** Production Docker installation with full performance optimization.

**What it does:**
- Installs Docker Engine with all plugins
- Configures custom data directory (`/opt/docker-data`)
- Optimized daemon configuration:
  - overlay2 storage driver
  - High concurrency downloads (25 parallel)
  - Non-blocking logging with compression
  - Live restore for zero-downtime updates
  - Prometheus metrics endpoint
- DNS optimization with Cloudflare/Google
- Time synchronization (critical for GPG keys)
- BuildKit enabled for faster builds
- Full validation and performance testing

**Usage:**
```bash
# Basic installation
ansible-playbook playbooks/docker/install-docker.yml -i inventory

# With vault for registry authentication
ansible-playbook playbooks/docker/install-docker.yml -i inventory --ask-vault-pass
```

**Customization:**
Edit the playbook to configure:
```yaml
# Add users to docker group
docker_users:
  - deploy
  - jenkins

# Configure insecure registries (development only!)
docker_insecure_registries:
  - "localhost:5000"
  - "registry.internal:5000"

# Configure registry authentication (use Ansible Vault!)
docker_registries_auth:
  - registry: "https://index.docker.io/v1/"
    username: "myuser"
    password: "{{ vault_dockerhub_token }}"
  - registry: "ghcr.io"
    username: "github-user"
    password: "{{ vault_github_token }}"
```

**Performance Features Included:**
| Feature | Value | Benefit |
|---------|-------|---------|
| `data-root` | `/opt/docker-data` | SSD optimization |
| `max-concurrent-downloads` | 25 | 200-300% faster pulls |
| `userland-proxy` | false | +20-30% network performance |
| `live-restore` | true | Zero-downtime updates |
| `mode` | non-blocking | Application doesn't block on logs |
| `metrics-addr` | 127.0.0.1:9323 | Prometheus monitoring |

---

## 🎯 Quick Start

1. **Review the playbook** and customize variables as needed
2. **Create vault file** (if using registry authentication):
   ```bash
   ansible-vault create vars/registry_secrets.yml
   ```
3. **Run the playbook:**
   ```bash
   ansible-playbook playbooks/docker/install-docker.yml -i inventory
   ```

## 📚 Related Documentation

- [Docker Complete Guide](../../docs/user-guides/docker/) - 8-part modular documentation
- [Docker Role README](../../roles/docker/README.md) - Role reference
- [Variables Reference](../../docs/reference/VARIABLES.md) - All variables

---

[← Back to Playbooks](../README.md)

