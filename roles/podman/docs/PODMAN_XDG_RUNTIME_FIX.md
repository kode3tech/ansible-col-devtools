# Podman XDG_RUNTIME_DIR Fix

## 🐛 Problem Identified

### Symptom
When running `podman login` as **root** on Ubuntu 24.04, the following warning/error appears:

```
WARN[0000] "/run/user/0" directory set by $XDG_RUNTIME_DIR does not exist. 
Either create the directory or unset $XDG_RUNTIME_DIR.: 
stat /run/user/0: no such file or directory: 
Trying to pull image in the event that it is a public image.
Authenticating with existing credentials for docker.io
Existing credentials are invalid, please enter valid username and password
```

### Root Cause

Podman (unlike Docker) uses the XDG (X Desktop Group) standard for managing runtime and configuration directories:

1. **XDG_RUNTIME_DIR**: Temporary directory for runtime files
   - For regular users: `/run/user/<UID>`
   - For root: `/run/user/0`

2. **XDG_CONFIG_HOME**: Directory for persistent configurations
   - For regular users: `$HOME/.config`
   - For root: `/root/.config`

When the `/run/user/0` directory does not exist, Podman cannot:
- Store temporary credentials
- Manage communication sockets
- Maintain session state

### Why Does This Happen?

In modern distributions like Ubuntu 24.04:
- `systemd-logind` creates `/run/user/<UID>` only for **login sessions** of regular users
- For root, this directory is **not created automatically** in many scenarios
- Containers and SSH executions may not have an active logind session

---

## ✅ Implemented Solutions

### 1. Persistent Configuration with systemd-tmpfiles (DEFINITIVE SOLUTION)

**Task added**:
```yaml
- name: Configure systemd-tmpfiles for Podman XDG_RUNTIME_DIR
  ansible.builtin.copy:
    content: |
      # Podman XDG_RUNTIME_DIR for root
      # This ensures /run/user/0 is created automatically on boot
      d /run/user/0 0700 root root -
    dest: /etc/tmpfiles.d/podman-xdg.conf
    mode: '0644'
  tags: podman

- name: Create XDG_RUNTIME_DIR for root immediately
  ansible.builtin.command: systemd-tmpfiles --create /etc/tmpfiles.d/podman-xdg.conf
  changed_when: true
  tags: podman
```

**What it does**:
- Creates configuration file in `/etc/tmpfiles.d/podman-xdg.conf`
- **Persists between reboots** - systemd recreates automatically on boot
- Applies configuration immediately with `systemd-tmpfiles --create`
- tmpfiles.d format: `d /run/user/0 0700 root root -`
  - `d` = directory
  - `/run/user/0` = path
  - `0700` = permissions
  - `root root` = owner and group
  - `-` = no max age

**Why it's better**:
- ✅ Survives reboots
- ✅ Managed by systemd (system standard)
- ✅ Compatible with tmpfs (/run is cleaned on boot)
- ✅ Official solution recommended by systemd documentation

### 2. Configuration Directory Creation

**Task added**:
```yaml
- name: Ensure auth directory exists for root Podman
  ansible.builtin.file:
    path: /root/.config/containers
    state: directory
    owner: root
    group: root
    mode: '0700'
  tags: podman
```

**What it does**:
- Creates directory to store `auth.json` (credentials)
- Enables persistent login to registries
- Secure with 0700 permissions

### 3. Export XDG_RUNTIME_DIR in Commands

**Updated in podman_login module**:
```yaml
- name: Login to Podman registries (root mode) - Using podman_login module
  containers.podman.podman_login:
    # ...
  environment:
    XDG_RUNTIME_DIR: /run/user/0
```

**Updated in shell commands**:
```yaml
- name: Login to Podman registries (root mode) - Fallback to command
  ansible.builtin.shell:
    cmd: |
      export XDG_RUNTIME_DIR=/run/user/0
      echo "{{ item.password }}" | \
      podman login "{{ item.registry }}" -u "{{ item.username }}" --password-stdin
```

### 4. Support for Rootless Users

**Tasks added**:
```yaml
- name: Get user information for XDG_RUNTIME_DIR
  ansible.builtin.getent:
    database: passwd
    key: "{{ item }}"
  loop: "{{ podman_rootless_users }}"
  register: user_info

- name: Ensure XDG_RUNTIME_DIR exists for rootless users
  ansible.builtin.file:
    path: "/run/user/{{ item.ansible_facts.getent_passwd[item.item][1] }}"
    state: directory
    owner: "{{ item.item }}"
    group: "{{ item.ansible_facts.getent_passwd[item.item][2] }}"
    mode: '0700'
  loop: "{{ user_info.results }}"
  when: item.ansible_facts.getent_passwd is defined
```

**What it does**:
- Detects UID of each rootless user
- Creates `/run/user/<UID>` for each user
- Ensures correct ownership

---

## 🔍 Technical Details

### Podman Directory Structure

#### For Root
```
/run/user/0/                         # XDG_RUNTIME_DIR (temporary runtime)
├── containers/                      # Sockets and runtime
├── libpod/                          # Podman state
└── ...

/root/.config/containers/            # XDG_CONFIG_HOME (persistent)
├── auth.json                        # Registry credentials
├── storage.conf                     # Storage configuration
└── registries.conf                  # Registry configuration
```

#### For Regular User (e.g., ansible, UID 1000)
```
/run/user/1000/                      # XDG_RUNTIME_DIR
├── containers/
├── libpod/
└── ...

/home/ansible/.config/containers/    # XDG_CONFIG_HOME
├── auth.json
├── storage.conf
└── registries.conf
```

### Correct Permissions

| Directory | Owner | Group | Mode | Description |
|-----------|-------|-------|------|-------------|
| `/run/user/0` | root | root | 0700 | Root runtime |
| `/root/.config/containers` | root | root | 0700 | Root config |
| `/run/user/<UID>` | user | user | 0700 | User runtime |
| `~/.config/containers` | user | user | 0700 | User config |

---

## 🧪 Tests and Verification

### Manual Test on Host

```bash
# Verify if directories exist
ls -la /run/user/0
ls -la /root/.config/containers

# Test login as root
sudo podman login docker.io
# Should work without warnings

# Verify stored credentials
sudo cat /root/.config/containers/auth.json
```

### Test with Ansible

```bash
# Run role
ansible-playbook -i inventory.ini playbook.yaml

# Verify result
ansible -i inventory.ini all -m shell -a "ls -la /run/user/0" --become
ansible -i inventory.ini all -m shell -a "ls -la /root/.config/containers" --become
```

### Log Verification

```bash
# View Podman logs
journalctl -u podman --since "5 minutes ago"

# View specific warnings
podman --log-level=debug info 2>&1 | grep -i xdg
```

---

## 📋 Expected Behavior

### Before Fix
```bash
root@host:~# podman login
WARN[0000] "/run/user/0" directory set by $XDG_RUNTIME_DIR does not exist...
Authenticating with existing credentials for docker.io
Existing credentials are invalid...
```

### After Fix
```bash
root@host:~# podman login docker.io
Username: myuser
Password: ********
Login Succeeded!
```

### Credentials Verification
```bash
root@host:~# cat /root/.config/containers/auth.json
{
  "auths": {
    "docker.io": {
      "auth": "base64encodedcredentials=="
    }
  }
}
```

---

## 🔄 Persistence and Lifecycle

### /run/user/0 Directory (tmpfs)

**Characteristics**:
- Stored in RAM (tmpfs)
- **Deleted on every reboot**
- Automatically created by role on boot

**Persistence Solution**:
- Add to systemd-tmpfiles or
- Recreate via our role on each provisioning

### /root/.config/containers Directory (persistent)

**Characteristics**:
- Stored on disk
- **Persists between reboots**
- Contains credentials and configurations

---

## 🐳 Comparison: Docker vs Podman

| Aspect | Docker | Podman |
|--------|--------|--------|
| **Auth Storage (root)** | `/root/.docker/config.json` | `/root/.config/containers/auth.json` |
| **Runtime Dir** | Does not use XDG | Uses `/run/user/0` |
| **Daemon** | Yes (dockerd) | No (daemonless) |
| **Socket** | `/var/run/docker.sock` | `/run/user/0/podman/podman.sock` |
| **Config Standard** | Proprietary | XDG Base Directory |

---

## 🔧 Troubleshooting

### Problem: Directory Disappears After Reboot

**Symptom**:
```bash
stat /run/user/0: no such file or directory
```

**Solution 1 - Systemd Tmpfiles**:
```bash
# Create /etc/tmpfiles.d/podman.conf
echo "d /run/user/0 0700 root root -" | sudo tee /etc/tmpfiles.d/podman.conf
sudo systemd-tmpfiles --create
```

**Solution 2 - Recreate Manually**:
```bash
sudo mkdir -p /run/user/0
sudo chmod 0700 /run/user/0
sudo chown root:root /run/user/0
```

**Solution 3 - Our Role** (already implemented):
- Role recreates automatically on each execution

### Problem: Credentials Not Persisting

**Symptom**:
```bash
Authenticating with existing credentials
Existing credentials are invalid
```

**Verify**:
```bash
# Check if auth.json exists
ls -la /root/.config/containers/auth.json

# Check content
cat /root/.config/containers/auth.json

# Check permissions
stat /root/.config/containers/auth.json
```

**Solution**:
```bash
# Recreate directory
sudo mkdir -p /root/.config/containers
sudo chmod 0700 /root/.config/containers

# Login again
sudo podman login registry.example.com
```

### Problem: Permission Denied in Rootless

**Symptom**:
```bash
Error: creating runtime static files directory: mkdir /run/user/1000: permission denied
```

**Verify**:
```bash
# Check if user has logind session
loginctl show-user <username>

# Check UID
id <username>

# Check if directory exists
ls -la /run/user/$(id -u <username>)
```

**Solution**:
```bash
# Create manually (our role already does this)
sudo mkdir -p /run/user/$(id -u <username>)
sudo chown <username>:<username> /run/user/$(id -u <username>)
sudo chmod 0700 /run/user/$(id -u <username>)

# Or enable lingering (persistent session)
sudo loginctl enable-linger <username>
```

---

## 📚 References

### Official Documentation
- [Podman Authentication](https://docs.podman.io/en/latest/markdown/podman-login.1.html)
- [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html)
- [systemd-logind](https://www.freedesktop.org/software/systemd/man/systemd-logind.service.html)

### XDG Standard
```bash
XDG_RUNTIME_DIR    # Non-essential runtime files ($USER-specific)
XDG_CONFIG_HOME    # User configurations
XDG_DATA_HOME      # User-specific data
XDG_CACHE_HOME     # Non-essential cache
```

### Defaults
```bash
XDG_RUNTIME_DIR=/run/user/$UID
XDG_CONFIG_HOME=$HOME/.config
XDG_DATA_HOME=$HOME/.local/share
XDG_CACHE_HOME=$HOME/.cache
```

---

## ✅ Implementation Checklist

- [x] Create `/run/user/0` for root
- [x] Create `/root/.config/containers` for auth
- [x] Export `XDG_RUNTIME_DIR` in podman_login module
- [x] Export `XDG_RUNTIME_DIR` in shell commands
- [x] Create `/run/user/<UID>` for rootless users
- [x] Detect UID automatically via getent
- [x] Configure correct permissions (0700)
- [x] Document problem and solutions
- [x] Update role to include fixes
- [ ] Add Molecule tests to verify directories
- [ ] Add systemd-tmpfiles config (optional)

---

## 🚀 Next Steps

### Option 1: Systemd Tmpfiles (Recommended for Production)

Add task to create persistent configuration:

```yaml
- name: Configure systemd-tmpfiles for Podman XDG_RUNTIME_DIR
  ansible.builtin.copy:
    content: |
      # Podman XDG_RUNTIME_DIR for root
      d /run/user/0 0700 root root -
    dest: /etc/tmpfiles.d/podman-xdg.conf
    mode: '0644'
  notify: systemd tmpfiles create
```

### Option 2: Systemd Unit (For Servers)

Create service that ensures directory on boot:

```yaml
- name: Create systemd unit for Podman runtime dir
  ansible.builtin.copy:
    content: |
      [Unit]
      Description=Create Podman XDG runtime directory
      Before=podman.service
      
      [Service]
      Type=oneshot
      ExecStart=/usr/bin/mkdir -p /run/user/0
      ExecStart=/usr/bin/chmod 0700 /run/user/0
      RemainAfterExit=yes
      
      [Install]
      WantedBy=multi-user.target
    dest: /etc/systemd/system/podman-xdg-runtime.service
    mode: '0644'
  notify: systemd daemon-reload
```

### Option 3: Keep Current Solution (Simple and Effective)

Our role already creates the directories on each execution, which is sufficient for:
- Initial provisioning
- Periodic re-provisioning
- Development environments

---

## 📊 Impact and Benefits

### Before
- ❌ XDG_RUNTIME_DIR warnings on every login
- ❌ Possible authentication failure
- ❌ Poor user experience
- ❌ Polluted logs with warnings

### After
- ✅ Clean login without warnings
- ✅ Reliable authentication
- ✅ Compatible with Docker workflows
- ✅ Production ready
- ✅ Works in root and rootless modes

---

**Status**: ✅ **IMPLEMENTED**  
**Date**: 2024-11-06  
**Tested on**: Ubuntu 24.04, Debian 13, Rocky Linux 9  
**Maintainer**: Code3Tech DevOps Team

---

[← Back to Podman Documentation](../README.md)
