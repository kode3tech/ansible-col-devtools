# Your First Playbook

Learn by doing! Create and run your first playbook with the **code3tech.devtools** collection.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Example 1: Install Docker](#example-1-install-docker)
- [Example 2: Install Podman](#example-2-install-podman)
- [Example 3: Deploy CI/CD Runner](#example-3-deploy-cicd-runner)
- [Understanding What Happened](#understanding-what-happened)
- [Next Steps](#next-steps)

---

## Prerequisites

Before starting, ensure you have:

- ✅ Collection installed: [Installation Guide](01-installation.md)
- ✅ Target host accessible via SSH
- ✅ SSH key configured (passwordless access)
- ✅ Sudo privileges on target host

**Quick connectivity test:**
```bash
# Test SSH connection
ssh user@your-server.com

# Test with Ansible
ansible all -i "your-server.com," -m ping -u user
```

---

## Example 1: Install Docker

### Step 1: Create Inventory File

Create `inventory`:

```ini
[docker_hosts]
server1.example.com ansible_user=ubuntu
```

**Or use IP address:**
```ini
[docker_hosts]
192.168.1.100 ansible_user=ubuntu
```

### Step 2: Create Playbook

Create `install-docker.yml`:

```yaml
---
- name: Install Docker on servers
  hosts: docker_hosts
  become: true
  
  roles:
    - code3tech.devtools.docker
```

### Step 3: Run Playbook

```bash
ansible-playbook -i inventory install-docker.yml
```

**Expected output:**
```
PLAY [Install Docker on servers] ***************

TASK [Gathering Facts] *************************
ok: [server1.example.com]

TASK [code3tech.devtools.docker : Install Docker] ***
changed: [server1.example.com]

PLAY RECAP ************************************
server1.example.com    : ok=12   changed=5
```

### Step 4: Verify Installation

SSH into your server and verify:

```bash
ssh ubuntu@server1.example.com

# Check Docker version
docker --version
# Output: Docker version 24.0.7, build afdd53b

# Check Docker service
systemctl status docker
# Output: ● docker.service - Docker Application Container Engine
#         Active: active (running)
```

🎉 **Congratulations!** You just deployed Docker with Ansible!

---

## Example 2: Install Podman

### Simple Podman Installation

Create `install-podman.yml`:

```yaml
---
- name: Install Podman with rootless support
  hosts: podman_hosts
  become: true
  
  roles:
    - code3tech.devtools.podman
```

Update `inventory`:
```ini
[podman_hosts]
server2.example.com ansible_user=ubuntu
```

Run:
```bash
ansible-playbook -i inventory install-podman.yml
```

### With Custom Configuration

```yaml
---
- name: Install Podman with registry authentication
  hosts: podman_hosts
  become: true
  
  vars:
    podman_users:
      - deploy
      - jenkins
    
    podman_registries_auth:
      - registry: "ghcr.io"
        username: "myuser"
        password: "{{ vault_github_token }}"
  
  roles:
    - code3tech.devtools.podman
```

**Note**: Store secrets in Ansible Vault:
```bash
ansible-vault create secrets.yml
# Add: vault_github_token: "your_token_here"
```

Run with vault:
```bash
ansible-playbook -i inventory install-podman.yml --ask-vault-pass
```

---

## Example 3: Deploy CI/CD Runner

### GitHub Actions Runner

Create `deploy-github-runner.yml`:

```yaml
---
- name: Deploy GitHub Actions self-hosted runner
  hosts: ci_servers
  become: true
  
  vars:
    github_actions_runners_org: "your-organization"
    github_actions_runners_pat: "{{ vault_github_pat }}"
    
    github_actions_runners_list:
      - name: "runner-01"
        labels:
          - "linux"
          - "docker"
          - "production"
  
  roles:
    - code3tech.devtools.docker
    - code3tech.devtools.github_actions_runners
```

**Key points:**
- Installs Docker first (dependency)
- Creates runner with custom labels
- Runner automatically registers with GitHub

Update `inventory`:
```ini
[ci_servers]
ci-server-01.example.com ansible_user=ubuntu
```

Run:
```bash
ansible-playbook -i inventory deploy-github-runner.yml --ask-vault-pass
```

**Verify in GitHub:**
- Go to: `https://github.com/organizations/YOUR_ORG/settings/actions/runners`
- You should see `runner-01` listed as **Online** ✅

---

## Understanding What Happened

### Playbook Anatomy

```yaml
---
- name: Install Docker on servers          # 1. Play name (description)
  hosts: docker_hosts                      # 2. Target hosts from inventory
  become: true                             # 3. Use sudo (run as root)
  
  vars:                                    # 4. Variables (optional)
    docker_users:
      - myuser
  
  roles:                                   # 5. Roles to apply
    - code3tech.devtools.docker
```

**What each line does:**

1. **`name:`** - Human-readable description of what this play does
2. **`hosts:`** - Which servers to target (from inventory file)
3. **`become: true`** - Escalate privileges to root (required for package installation)
4. **`vars:`** - Variables to customize role behavior (optional)
5. **`roles:`** - List of roles to apply in order

### Execution Flow

```
1. Ansible reads inventory file
   └─> Identifies target hosts

2. Connects via SSH to each host
   └─> Gathers system information (OS, version, etc.)

3. Applies role tasks in sequence
   ├─> Installs packages
   ├─> Configures services
   ├─> Creates users/groups
   └─> Starts services

4. Reports results
   └─> Shows what changed
```

### Idempotency

Run the same playbook twice:

```bash
# First run
ansible-playbook -i inventory install-docker.yml
# Output: changed=5

# Second run (immediately after)
ansible-playbook -i inventory install-docker.yml
# Output: changed=0  ← Nothing changed!
```

**Why?** Ansible is **idempotent** - it only makes changes when needed.

---

## Common Customizations

### Add Users to Docker Group

```yaml
vars:
  docker_users:
    - alice
    - bob
    - jenkins
```

**Result**: Users can run `docker` commands without sudo.

### Configure Multiple Servers

```yaml
hosts: all  # Apply to ALL hosts in inventory
```

Or create groups:
```ini
[production]
prod-server-01.example.com
prod-server-02.example.com

[staging]
staging-server-01.example.com
```

### Use Different Variables per Group

```yaml
- name: Install Docker
  hosts: production
  become: true
  vars:
    docker_daemon_config:
      log-driver: "json-file"
      log-opts:
        max-size: "10m"
  roles:
    - code3tech.devtools.docker

- name: Install Docker (staging)
  hosts: staging
  become: true
  vars:
    docker_daemon_config:
      log-driver: "local"
  roles:
    - code3tech.devtools.docker
```

---

## Troubleshooting First Playbook

### "Host key verification failed"

**Solution**: Add host to known_hosts
```bash
ssh-keyscan -H server1.example.com >> ~/.ssh/known_hosts
```

Or disable checking (not recommended for production):
```ini
# ansible.cfg
[defaults]
host_key_checking = False
```

### "Permission denied (publickey)"

**Solutions:**

1. **Use password authentication temporarily:**
   ```bash
   ansible-playbook -i inventory install-docker.yml --ask-pass
   ```

2. **Specify SSH key:**
   ```ini
   [docker_hosts]
   server1.example.com ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/id_rsa
   ```

3. **Copy SSH key to server:**
   ```bash
   ssh-copy-id ubuntu@server1.example.com
   ```

### "Become password is missing"

**Solution**: Add `--ask-become-pass` if sudo requires password
```bash
ansible-playbook -i inventory install-docker.yml --ask-become-pass
```

### "Connection timeout"

**Solutions:**

1. **Test connectivity:**
   ```bash
   ansible -i inventory docker_hosts -m ping
   ```

2. **Increase timeout:**
   ```ini
   # ansible.cfg
   [defaults]
   timeout = 30
   ```

3. **Check firewall:**
   ```bash
   # On control node
   telnet server1.example.com 22
   ```

---

## Next Steps

✅ **You ran your first playbook!** Now explore:

1. **[Inventory Basics](03-inventory-basics.md)** - Organize hosts into groups
2. **[Using Roles](04-using-roles.md)** - Learn about all 6 available roles
3. **[Common Patterns](05-common-patterns.md)** - Multi-environment setups, vault, tags

---

## Quick Reference

**Basic playbook structure:**
```yaml
---
- name: Description
  hosts: target_group
  become: true
  vars:
    variable_name: value
  roles:
    - collection_name.role_name
```

**Run commands:**
```bash
# Run playbook
ansible-playbook -i inventory playbook.yml

# Dry run (check mode)
ansible-playbook -i inventory playbook.yml --check

# Verbose output
ansible-playbook -i inventory playbook.yml -v
# More verbose: -vv, -vvv, -vvvv

# Limit to specific hosts
ansible-playbook -i inventory playbook.yml --limit server1.example.com
```

---

[← Back: Installation](01-installation.md) | [Next: Inventory Basics →](03-inventory-basics.md)
