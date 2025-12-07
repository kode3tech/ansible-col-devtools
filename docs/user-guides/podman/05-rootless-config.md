# Rootless Configuration

Complete guide to configuring Podman rootless mode for secure, per-user container execution.

---

## 📋 Table of Contents

- [Overview](#overview)
- [How Rootless Works](#how-rootless-works)
- [Configuration](#configuration)
- [Subuid/Subgid Mapping](#subuidsubgid-mapping)
- [XDG_RUNTIME_DIR](#xdg_runtime_dir)
- [Storage Locations](#storage-locations)
- [Port Binding](#port-binding)
- [Troubleshooting](#troubleshooting)

---

## Overview

Rootless Podman allows running containers **without root privileges**, providing enhanced security and user isolation.

### Key Benefits

- ✅ **Security**: No root daemon, smaller attack surface
- ✅ **Isolation**: Each user has separate containers
- ✅ **Multi-tenant**: Multiple users can run containers safely
- ✅ **No Sudo**: Users don't need administrative access

### How It Differs from Root Mode

| Aspect | Root Mode | Rootless Mode |
|--------|-----------|---------------|
| Execution | `sudo podman run` | `podman run` |
| Storage | `/var/lib/containers/storage` | `~/.local/share/containers/storage` |
| Network | iptables (full) | slirp4netns (user-space) |
| Ports | All (< 1024 included) | > 1024 only (by default) |
| Isolation | Shared | Per-user |

---

## How Rootless Works

### User Namespaces

Podman uses Linux user namespaces to map container UIDs to host UIDs:

```
┌──────────────────────────────────────────────────────────────┐
│                    USER NAMESPACE MAPPING                     │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│   CONTAINER              HOST                                 │
│   ┌─────────┐           ┌─────────────────┐                  │
│   │ UID 0   │ ───────▶  │ UID 100000      │                  │
│   │ (root)  │           │ (developer's    │                  │
│   │         │           │  subuid range)  │                  │
│   └─────────┘           └─────────────────┘                  │
│                                                               │
│   ┌─────────┐           ┌─────────────────┐                  │
│   │ UID 1000│ ───────▶  │ UID 101000      │                  │
│   │ (app)   │           │                 │                  │
│   └─────────┘           └─────────────────┘                  │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### Subuid/Subgid Files

The mapping is defined in:
- `/etc/subuid` - User ID ranges
- `/etc/subgid` - Group ID ranges

---

## Configuration

### Enable Rootless Mode

```yaml
podman_enable_rootless: true
```

### Configure Users

```yaml
podman_rootless_users:
  - developer      # Developer workstation
  - jenkins        # CI/CD service
  - deployer       # Deployment user
  - testuser       # QA/testing
```

### Complete Example

```yaml
---
- name: Configure Podman Rootless
  hosts: all
  become: true
  
  vars:
    podman_enable_rootless: true
    
    podman_rootless_users:
      - developer
      - jenkins
    
    # Optional: Custom subuid range
    podman_subuid_start: 100000
    podman_subuid_count: 65536
  
  pre_tasks:
    # Users must exist before role runs
    - name: Create Podman users
      ansible.builtin.user:
        name: "{{ item }}"
        shell: /bin/bash
        create_home: true
      loop:
        - developer
        - jenkins
  
  roles:
    - code3tech.devtools.podman
```

---

## Subuid/Subgid Mapping

### Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `podman_subuid_start` | `100000` | Starting UID for ranges |
| `podman_subuid_count` | `65536` | UIDs per user |
| `podman_subgid_start` | `100000` | Starting GID for ranges |
| `podman_subgid_count` | `65536` | GIDs per user |

### How Ranges Are Assigned

```yaml
podman_rootless_users:
  - developer   # Gets 100000-165535
  - jenkins     # Gets 165536-231071
  - deployer    # Gets 231072-296607
```

### Resulting Files

`/etc/subuid`:
```
developer:100000:65536
jenkins:165536:65536
deployer:231072:65536
```

`/etc/subgid`:
```
developer:100000:65536
jenkins:165536:65536
deployer:231072:65536
```

### Custom Ranges

```yaml
# More UIDs per user (for complex containers)
podman_subuid_count: 131072  # 128K UIDs per user

# Different starting point
podman_subuid_start: 200000
```

### Verify Mappings

```bash
# Check user's subuid
grep developer /etc/subuid

# Check user's subgid
grep developer /etc/subgid

# Verify from Podman
podman unshare cat /proc/self/uid_map
```

---

## XDG_RUNTIME_DIR

### What It Is

`XDG_RUNTIME_DIR` is a per-user directory for runtime files:
- Socket files
- Temporary authentication
- Container metadata

### Default Path

```
/run/user/<UID>
```

For user with UID 1000: `/run/user/1000`

### Role Configuration

The role ensures XDG_RUNTIME_DIR exists for each rootless user:

```yaml
- name: Ensure XDG_RUNTIME_DIR exists
  ansible.builtin.file:
    path: "/run/user/{{ user_uid }}"
    state: directory
    owner: "{{ user }}"
    group: "{{ user }}"
    mode: '0700'
```

### Environment Variable

For manual use, ensure it's set:

```bash
export XDG_RUNTIME_DIR="/run/user/$(id -u)"
```

Add to `~/.bashrc` or `~/.zshrc`:
```bash
echo 'export XDG_RUNTIME_DIR="/run/user/$(id -u)"' >> ~/.bashrc
```

### Systemd User Session

If using systemd, enable lingering for the user:

```bash
sudo loginctl enable-linger username
```

This keeps XDG_RUNTIME_DIR alive after logout.

---

## Storage Locations

### Per-User Storage

Each rootless user has isolated storage:

| Location | Purpose |
|----------|---------|
| `~/.local/share/containers/storage` | Images, containers |
| `~/.config/containers` | Configuration files |
| `$XDG_RUNTIME_DIR/containers` | Runtime data |

### Custom Storage Path

```yaml
podman_storage_conf:
  storage:
    driver: "overlay"
    graphroot: "/data/podman/${USER}/storage"
    runroot: "/run/user/${UID}/containers"
```

### Storage Initialization

First run initializes user storage:

```bash
podman info  # Initializes storage
```

---

## Port Binding

### Limitation

Rootless Podman cannot bind to ports < 1024 by default.

### Solutions

#### 1. Use High Ports

```bash
# Instead of port 80
podman run -d -p 8080:80 nginx
```

#### 2. Port Forwarding (iptables)

```bash
# Redirect 80 to 8080
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080
```

#### 3. sysctl (System-Wide)

```bash
# Allow non-root to bind to lower ports
sudo sysctl -w net.ipv4.ip_unprivileged_port_start=80
```

Persist in `/etc/sysctl.conf`:
```
net.ipv4.ip_unprivileged_port_start=80
```

#### 4. Using Ansible

```yaml
pre_tasks:
  - name: Allow unprivileged port binding
    ansible.posix.sysctl:
      name: net.ipv4.ip_unprivileged_port_start
      value: "80"
      sysctl_file: /etc/sysctl.d/99-podman.conf
      reload: true
```

---

## Network Configuration

### slirp4netns

Rootless Podman uses slirp4netns for user-space networking:

```
┌───────────────────────────────────────────────────────┐
│              ROOTLESS NETWORKING                       │
├───────────────────────────────────────────────────────┤
│                                                        │
│   Container                User Space                  │
│   ┌─────────────┐         ┌─────────────────┐         │
│   │   nginx     │         │   slirp4netns   │         │
│   │   :80       │◀───────▶│   (TAP device)  │         │
│   └─────────────┘         └────────┬────────┘         │
│                                    │                   │
│                                    ▼                   │
│                           ┌─────────────────┐         │
│                           │   Host Network  │         │
│                           │   :8080 (mapped)│         │
│                           └─────────────────┘         │
│                                                        │
└───────────────────────────────────────────────────────┘
```

### Performance Note

slirp4netns is slightly slower than root mode networking but provides isolation.

---

## Validation

### Check Rootless Status

```bash
# As rootless user (no sudo)
podman info | grep rootless
# Expected: rootless: true
```

### Test Container Run

```bash
# As regular user
podman run --rm alpine echo "Rootless works!"
```

### Verify User Isolation

```bash
# User 1
su - developer
podman pull alpine
podman images  # Shows alpine

# User 2 (different session)
su - jenkins
podman images  # Empty - isolated storage
```

### Check Storage Location

```bash
podman info --format '{{.Store.GraphRoot}}'
# Expected: /home/developer/.local/share/containers/storage
```

---

## Troubleshooting

### XDG_RUNTIME_DIR Not Set

```
Error: XDG_RUNTIME_DIR is not set
```

**Solution:**
```bash
export XDG_RUNTIME_DIR="/run/user/$(id -u)"
```

### XDG_RUNTIME_DIR Wrong Owner

```
Error: XDG_RUNTIME_DIR directory "/run/user/0" is not owned by the current user
```

**Cause:** Running as user but directory points to root's.

**Solution:**
```bash
# Get correct UID
id -u

# Set correct directory
export XDG_RUNTIME_DIR="/run/user/$(id -u)"
```

### Subuid Not Configured

```
Error: cannot find UID/GID for user
```

**Solution:** Ensure user is in `podman_rootless_users`:
```yaml
podman_rootless_users:
  - myuser
```

Verify manually:
```bash
cat /etc/subuid | grep myuser
```

### Permission Denied on Storage

```
Error: creating overlay mount: permission denied
```

**Solutions:**

1. Check directory ownership:
   ```bash
   ls -la ~/.local/share/containers/
   ```

2. Reset storage:
   ```bash
   podman system reset
   ```

3. Check SELinux (RHEL):
   ```bash
   restorecon -Rv ~/.local/share/containers
   ```

### User Not Created

```
Error: user does not exist
```

**Solution:** Create user in pre_tasks:
```yaml
pre_tasks:
  - name: Create user
    ansible.builtin.user:
      name: developer
      create_home: true
```

---

## Best Practices

### 1. Create Dedicated Users

Don't use system accounts for containers:
```yaml
podman_rootless_users:
  - podman-developer  # Dedicated
  - podman-ci         # Dedicated
```

### 2. Enable Lingering

Keep user sessions alive:
```bash
sudo loginctl enable-linger username
```

### 3. Use Systemd Units

Create user services:
```bash
podman generate systemd --user mycontainer > ~/.config/systemd/user/mycontainer.service
systemctl --user enable mycontainer
```

### 4. Monitor Storage

User storage can grow quickly:
```bash
podman system df
```

---

## Complete Rootless Setup Example

```yaml
---
- name: Complete Rootless Podman Setup
  hosts: all
  become: true
  
  vars:
    podman_enable_rootless: true
    podman_rootless_users:
      - developer
      - jenkins
    
    podman_registries_auth:
      - registry: "docker.io"
        username: "myuser"
        password: "{{ vault_dockerhub_token }}"
  
  pre_tasks:
    - name: Create rootless users
      ansible.builtin.user:
        name: "{{ item }}"
        shell: /bin/bash
        create_home: true
      loop: "{{ podman_rootless_users }}"
    
    - name: Enable user lingering
      ansible.builtin.command: loginctl enable-linger {{ item }}
      loop: "{{ podman_rootless_users }}"
      changed_when: false
  
  roles:
    - code3tech.devtools.podman
  
  post_tasks:
    - name: Verify rootless for each user
      ansible.builtin.command: podman info --format '{{ "{{" }}.Host.Security.Rootless{{ "}}" }}'
      become: true
      become_user: "{{ item }}"
      environment:
        XDG_RUNTIME_DIR: "/run/user/{{ lookup('pipe', 'id -u ' + item) }}"
      loop: "{{ podman_rootless_users }}"
      register: rootless_check
      changed_when: false
    
    - name: Display rootless status
      ansible.builtin.debug:
        msg: "{{ item.item }}: rootless={{ item.stdout }}"
      loop: "{{ rootless_check.results }}"
```

---

## Next Steps

- **[Production Deployment](06-production-deployment.md)** - Complete playbooks
- **[Performance & Security](07-performance-security.md)** - Optimization

---

[← Back to Podman Documentation](README.md) | [Previous: Registry Auth](04-registry-auth.md) | [Next: Production Deployment →](06-production-deployment.md)
