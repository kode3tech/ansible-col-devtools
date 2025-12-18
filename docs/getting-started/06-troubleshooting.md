# Troubleshooting

Solutions to common issues when deploying with **code3tech.devtools** collection.

## 📋 Table of Contents

- [Connection Issues](#connection-issues)
- [Permission Problems](#permission-problems)
- [Docker Issues](#docker-issues)
- [Podman Issues](#podman-issues)
- [CI/CD Runner Issues](#cicd-runner-issues)
- [Performance Issues](#performance-issues)
- [Debugging Tips](#debugging-tips)

---

## Connection Issues

### SSH Connection Failed

**Problem:**
```
fatal: [server1]: UNREACHABLE! => {"msg": "Failed to connect to the host via ssh"}
```

**Solutions:**

1. **Check SSH connectivity:**
```bash
# Test manual SSH connection
ssh user@server1

# Test with verbose output
ssh -vvv user@server1
```

2. **Verify inventory:**
```yaml
# Correct inventory format
all:
  hosts:
    server1:
      ansible_host: 192.168.1.100
      ansible_user: deploy           # SSH user
      ansible_ssh_private_key_file: ~/.ssh/id_rsa
```

3. **Check SSH key permissions:**
```bash
# Private key should be 600
chmod 600 ~/.ssh/id_rsa

# Verify SSH agent
eval $(ssh-agent)
ssh-add ~/.ssh/id_rsa
```

4. **Add host key to known_hosts:**
```bash
# Option 1: Accept manually
ssh-keyscan server1 >> ~/.ssh/known_hosts

# Option 2: Disable check (NOT recommended for production)
# In ansible.cfg:
[defaults]
host_key_checking = False
```

### Host Key Verification Failed

**Problem:**
```
fatal: [server1]: FAILED! => {"msg": "Host key verification failed"}
```

**Solutions:**

1. **Remove old key:**
```bash
ssh-keygen -R server1
# Or remove from IP
ssh-keygen -R 192.168.1.100
```

2. **Accept new key:**
```bash
ssh-keyscan server1 >> ~/.ssh/known_hosts
```

### Timeout Errors

**Problem:**
```
fatal: [server1]: FAILED! => {"msg": "Timeout (30s) waiting for connection"}
```

**Solutions:**

1. **Increase timeout** (`ansible.cfg`):
```ini
[defaults]
timeout = 60                        # Default is 10
```

2. **Check firewall:**
```bash
# On target server, allow SSH
sudo ufw allow 22/tcp
sudo ufw status
```

3. **Verify SSH service:**
```bash
# On target server
sudo systemctl status sshd
```

---

## Permission Problems

### Permission Denied (sudo)

**Problem:**
```
fatal: [server1]: FAILED! => {"msg": "Missing sudo password"}
```

**Solutions:**

1. **Use `--ask-become-pass`:**
```bash
ansible-playbook site.yml --ask-become-pass
```

2. **Configure passwordless sudo** (recommended):
```bash
# On target server
sudo visudo

# Add line (replace 'deploy' with your user):
deploy ALL=(ALL) NOPASSWD: ALL
```

3. **Specify sudo password in inventory** (NOT recommended):
```yaml
all:
  hosts:
    server1:
      ansible_become_password: "{{ vault_sudo_password }}"
```

### Docker Permission Denied

**Problem:**
```
FAILED! => {"msg": "permission denied while trying to connect to the Docker daemon socket"}
```

**Solutions:**

1. **Verify user is in docker group:**
```bash
# On target server
groups deploy

# Should show: deploy : deploy docker
```

2. **Add user to docker group:**
```bash
# On target server
sudo usermod -aG docker deploy

# Log out and back in, or
newgrp docker
```

3. **Verify Docker socket permissions:**
```bash
# Should be srw-rw----
ls -l /var/run/docker.sock

# If wrong, fix:
sudo chmod 666 /var/run/docker.sock  # Temporary fix
sudo systemctl restart docker         # Permanent fix
```

### File Ownership Issues

**Problem:**
```
FAILED! => {"msg": "chown failed: failed to look up user deploy"}
```

**Solutions:**

1. **Verify user exists:**
```bash
# On target server
id deploy

# If not, create:
sudo useradd -m -s /bin/bash deploy
```

2. **Check home directory permissions:**
```bash
# Should be owned by user
ls -ld /home/deploy

# Fix if needed:
sudo chown -R deploy:deploy /home/deploy
```

---

## Docker Issues

### Docker Installation Failed

**Problem:**
```
FAILED! => {"msg": "No package matching 'docker-ce' found available"}
```

**Solutions:**

1. **Verify OS compatibility:**
```bash
# Check distribution
lsb_release -a

# Supported: Ubuntu 22+, Debian 11+, RHEL 9+
```

2. **Check repository configuration:**
```yaml
# Ensure repo is enabled
docker_configure_repo: true
```

3. **Manual repository setup:**
```bash
# Ubuntu/Debian
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# RHEL/Rocky
sudo dnf config-manager --add-repo https://download.docker.com/linux/rhel/docker-ce.repo
```

### Docker Service Won't Start

**Problem:**
```
FAILED! => {"msg": "Unable to start service docker: Job for docker.service failed"}
```

**Solutions:**

1. **Check Docker logs:**
```bash
sudo journalctl -u docker -n 50 --no-pager
```

2. **Verify daemon.json syntax:**
```bash
# Check JSON syntax
sudo cat /etc/docker/daemon.json | python3 -m json.tool

# If syntax error, fix or remove:
sudo rm /etc/docker/daemon.json
sudo systemctl restart docker
```

3. **Check for port conflicts:**
```bash
# Check if another service is using Docker's ports
sudo netstat -tulpn | grep -E ':(2375|2376)'
```

4. **SELinux issues (RHEL/CentOS):**
```bash
# Check SELinux status
getenforce

# If enforcing, check denials:
sudo ausearch -m avc -ts recent

# Fix context:
sudo restorecon -R /var/lib/docker
```

### Registry Authentication Failed

**Problem:**
```
FAILED! => {"msg": "Error logging in to registry: unauthorized"}
```

**Solutions:**

1. **Verify credentials:**
```yaml
# Use correct registry URL
docker_registries_auth:
  - registry: "ghcr.io"              # NOT https://ghcr.io
    username: "myuser"
    password: "{{ vault_token }}"
```

2. **Check token permissions:**
```bash
# GitHub: Token needs 'read:packages' scope
# Test manually:
echo "TOKEN" | docker login ghcr.io -u USERNAME --password-stdin
```

3. **Verify user home directory:**
```bash
# Check ownership of ~/.docker/
ls -la /home/deploy/.docker/

# Fix if needed:
sudo chown -R deploy:deploy /home/deploy/.docker/
```

---

## Podman Issues

### Rootless Podman Setup Failed

**Problem:**
```
FAILED! => {"msg": "Error setting up rootless: XDG_RUNTIME_DIR not set"}
```

**Solutions:**

1. **Verify user login:**
```bash
# User must be logged in
loginctl user-status deploy

# If not, log in:
sudo machinectl shell deploy@
```

2. **Check XDG_RUNTIME_DIR:**
```bash
# Should be set automatically
echo $XDG_RUNTIME_DIR

# If empty, set manually:
export XDG_RUNTIME_DIR=/run/user/$(id -u)
```

3. **Enable lingering:**
```bash
# Allow user processes to run after logout
sudo loginctl enable-linger deploy
```

### Podman Socket Not Found

**Problem:**
```
FAILED! => {"msg": "Cannot connect to Podman socket"}
```

**Solutions:**

1. **Start user socket:**
```bash
# As the rootless user
systemctl --user start podman.socket
systemctl --user enable podman.socket
```

2. **Verify socket location:**
```bash
# Check socket exists
ls -l /run/user/$(id -u)/podman/podman.sock
```

### Subuid/Subgid Issues

**Problem:**
```
FAILED! => {"msg": "User has no subordinate UIDs/GIDs"}
```

**Solutions:**

1. **Check subuid/subgid:**
```bash
grep deploy /etc/subuid /etc/subgid
```

2. **Add entries if missing:**
```bash
# Add subordinate UIDs/GIDs
echo "deploy:100000:65536" | sudo tee -a /etc/subuid
echo "deploy:100000:65536" | sudo tee -a /etc/subgid

# Restart user session
sudo loginctl terminate-user deploy
```

---

## CI/CD Runner Issues

### GitHub Runner Registration Failed

**Problem:**
```
FAILED! => {"msg": "Runner registration failed: HTTP 401 Unauthorized"}
```

**Solutions:**

1. **Verify PAT permissions:**
```yaml
# Required scopes for organization runners:
# - admin:org (full control)
# - repo (if repository-scoped)

# Test PAT:
curl -H "Authorization: token YOUR_PAT" https://api.github.com/user
```

2. **Check runner scope:**
```yaml
# Organization runner
github_actions_runners_scope: "organization"
github_actions_runners_org: "your-org"

# Repository runner
github_actions_runners_scope: "repository"
github_actions_runners_owner: "your-org"
github_actions_runners_repo: "your-repo"
```

3. **Verify organization permissions:**
```bash
# User must have admin access to organization
# Check at: https://github.com/orgs/YOUR_ORG/settings/actions/runners
```

### Azure DevOps Agent Offline

**Problem:**
```
Agent is registered but shows offline in Azure DevOps
```

**Solutions:**

1. **Check agent service:**
```bash
# List agent services
sudo systemctl list-units | grep vsts.agent

# Check specific agent
sudo systemctl status vsts.agent.YOUR_ORG.POOL.AGENT_NAME
```

2. **Check agent logs:**
```bash
# Navigate to agent directory
cd /opt/azure-devops-agents/agent-01/_diag/

# View recent logs
tail -f Agent*.log
```

3. **Verify network connectivity:**
```bash
# Test Azure DevOps connectivity
curl -I https://dev.azure.com/YOUR_ORG

# Check PAT validity
curl -u :YOUR_PAT https://dev.azure.com/YOUR_ORG/_apis/projects
```

### GitLab Runner Not Picking Jobs

**Problem:**
```
Runner registered but not picking up jobs
```

**Solutions:**

1. **Check runner tags:**
```yaml
# Jobs require matching tags
gitlab_ci_runners_runners_list:
  - name: "runner-01"
    tags:
      - "linux"
      - "docker"
```

**In `.gitlab-ci.yml`:**
```yaml
build:
  tags:
    - linux                          # Must match runner tags
```

2. **Check run_untagged setting:**
```yaml
# Allow runner to pick untagged jobs
gitlab_ci_runners_runners_list:
  - name: "runner-01"
    run_untagged: true               # Default is false
```

3. **Verify runner is not paused:**
```bash
# In GitLab UI:
# Settings > CI/CD > Runners
# Check if runner has "paused" badge
```

4. **Check access level:**
```yaml
# For protected branches
gitlab_ci_runners_runners_list:
  - name: "prod-runner"
    access_level: "ref_protected"    # Matches protected branches
```

---

## Performance Issues

### Slow Playbook Execution

**Solutions:**

1. **Enable fact caching** (`ansible.cfg`):
```ini
[defaults]
gathering = smart
fact_caching = jsonfile
fact_caching_connection = /tmp/ansible_facts
fact_caching_timeout = 86400
```

2. **Increase parallelism:**
```ini
[defaults]
forks = 20                          # Default is 5
```

3. **Use free strategy:**
```yaml
---
- name: Fast deployment
  hosts: all
  strategy: free                    # Don't wait for slowest host
```

4. **Enable pipelining** (`ansible.cfg`):
```ini
[ssh_connection]
pipelining = True
```

5. **Skip fact gathering when not needed:**
```yaml
---
- name: Quick deployment
  hosts: all
  gather_facts: false
```

### Large Image Pull Timeout

**Problem:**
```
FAILED! => {"msg": "Timeout pulling image nginx:latest"}
```

**Solutions:**

1. **Increase timeout:**
```yaml
- name: Pull image with longer timeout
  community.docker.docker_image:
    name: nginx:latest
    source: pull
    timeout: 600                    # 10 minutes
```

2. **Configure Docker for faster downloads:**
```yaml
docker_daemon_config:
  max-concurrent-downloads: 20      # Default is 3
```

3. **Use retry logic:**
```yaml
- name: Pull image with retries
  community.docker.docker_image:
    name: nginx:latest
    source: pull
  register: pull_result
  retries: 3
  delay: 10
  until: pull_result is succeeded
```

---

## Debugging Tips

### Increase Verbosity

**Levels:**
```bash
ansible-playbook site.yml -v       # Basic output
ansible-playbook site.yml -vv      # More detailed
ansible-playbook site.yml -vvv     # Includes connection details
ansible-playbook site.yml -vvvv    # Full debugging (includes SSH commands)
```

### Check Mode (Dry Run)

```bash
# Test without making changes
ansible-playbook site.yml --check

# Show what would change
ansible-playbook site.yml --check --diff
```

### Step-Through Mode

```bash
# Execute one task at a time (prompt before each)
ansible-playbook site.yml --step
```

### Limit to Specific Hosts

```bash
# Test on single host first
ansible-playbook site.yml --limit server1

# Test on subset
ansible-playbook site.yml --limit "staging:&docker_hosts"
```

### Start at Specific Task

```bash
# Start from specific task
ansible-playbook site.yml --start-at-task="Install Docker"

# Use with tags
ansible-playbook site.yml --tags docker --start-at-task="Configure daemon"
```

### Syntax Check

```bash
# Verify playbook syntax
ansible-playbook site.yml --syntax-check

# Verify inventory
ansible-inventory -i inventory.yml --list
```

### Test Connectivity

```bash
# Ping all hosts
ansible all -m ping -i inventory.yml

# Test with specific user
ansible all -m ping -i inventory.yml -u deploy --ask-pass

# Test sudo access
ansible all -m shell -a "whoami" -i inventory.yml --become --ask-become-pass
```

### Debug Module

**Insert debug tasks:**
```yaml
- name: Debug variable
  ansible.builtin.debug:
    var: docker_daemon_config

- name: Debug message
  ansible.builtin.debug:
    msg: "Environment: {{ environment }}, Production: {{ is_production }}"

- name: Debug all variables for host
  ansible.builtin.debug:
    var: hostvars[inventory_hostname]
```

### View Effective Variables

```bash
# View all variables for a host
ansible -m debug -a "var=hostvars[inventory_hostname]" server1 -i inventory.yml

# View specific variable
ansible -m debug -a "var=docker_users" server1 -i inventory.yml
```

### Test Ansible Installation

```bash
# Verify Ansible installation
ansible --version

# Verify collection installation
ansible-galaxy collection list code3tech.devtools

# Verify role documentation
ansible-doc -t role code3tech.devtools.docker
```

### Validate Inventory

```bash
# List all hosts
ansible-inventory -i inventory.yml --list

# Show inventory graph
ansible-inventory -i inventory.yml --graph

# Verify host variables
ansible-inventory -i inventory.yml --host server1
```

---

## Common Error Messages

| Error | Likely Cause | Solution |
|-------|--------------|----------|
| `Collection not found` | Not installed | `ansible-galaxy collection install code3tech.devtools` |
| `Module not found: community.docker` | Dependency missing | `ansible-galaxy collection install community.docker` |
| `UNREACHABLE!` | SSH connection failed | Check SSH keys, firewall, inventory |
| `Permission denied` | Sudo/permissions issue | Use `--ask-become-pass` or configure passwordless sudo |
| `timeout` | Network/firewall issue | Check connectivity, increase timeout |
| `No package matching 'docker-ce'` | Repository not configured | Ensure `docker_configure_repo: true` |
| `unauthorized` | Wrong credentials | Verify PAT/token, check vault variables |
| `HTTP 404` | Wrong URL/scope | Verify org/repo name, check scope setting |

---

## Getting Help

### Check Role Documentation

```bash
# View role documentation
ansible-doc -t role code3tech.devtools.docker
ansible-doc -t role code3tech.devtools.github_actions_runners

# View module documentation
ansible-doc community.docker.docker_container
```

### Collection Resources

- **GitHub Issues**: [ansible-col-devtools/issues](https://github.com/kode3tech/ansible-col-devtools/issues)
- **Role READMEs**: `roles/{role}/README.md`
- **User Guides**: `docs/user-guides/{role}/`
- **FAQ**: [docs/FAQ.md](../FAQ.md)

### Enable Debug Logging

**For roles** (`ansible.cfg`):
```ini
[defaults]
stdout_callback = yaml
bin_ansible_callbacks = True
```

**For Docker:**
```json
{
  "debug": true,
  "log-level": "debug"
}
```

**For systemd services:**
```bash
# View service logs
sudo journalctl -u docker -f

# View runner logs
sudo journalctl -u actions.runner.* -f
```

### Report Issues

When reporting issues, include:

1. **Ansible version:** `ansible --version`
2. **Collection version:** `ansible-galaxy collection list code3tech.devtools`
3. **Target OS:** `lsb_release -a` or `cat /etc/os-release`
4. **Playbook excerpt:** Relevant part of your playbook (sanitized)
5. **Error output:** Full error message with `-vvv`
6. **Inventory:** Sample inventory configuration (sanitized)

---

## Troubleshooting Checklist

**Before running playbook:**
- [ ] Ansible >= 2.15 installed
- [ ] Collection installed: `ansible-galaxy collection list code3tech.devtools`
- [ ] Dependencies installed: `community.docker`, `containers.podman`
- [ ] Inventory syntax verified: `ansible-inventory --list`
- [ ] SSH connectivity tested: `ansible all -m ping`
- [ ] Vault password file configured (if using vault)

**After failure:**
- [ ] Read complete error message
- [ ] Check verbosity: Re-run with `-vvv`
- [ ] Test connectivity: `ansible all -m ping`
- [ ] Verify syntax: `ansible-playbook site.yml --syntax-check`
- [ ] Check dry run: `ansible-playbook site.yml --check`
- [ ] Review logs on target: `journalctl -u service_name`
- [ ] Check variables: `ansible-inventory --host hostname`

**For persistent issues:**
- [ ] Search GitHub issues
- [ ] Check role documentation
- [ ] Review user guides
- [ ] Consult FAQ
- [ ] Open new GitHub issue with details

---

## Quick Fixes Reference

```bash
# 1. Collection issues
ansible-galaxy collection install --force code3tech.devtools
ansible-galaxy collection install -r requirements.yml

# 2. SSH issues
ssh-keyscan hostname >> ~/.ssh/known_hosts
ssh-copy-id user@hostname

# 3. Permission issues
ansible-playbook site.yml --ask-become-pass
# Or configure: visudo -> user ALL=(ALL) NOPASSWD:ALL

# 4. Docker group
sudo usermod -aG docker $USER
newgrp docker

# 5. Service issues
sudo systemctl status service_name
sudo journalctl -u service_name -n 50

# 6. Clear facts cache
rm -rf /tmp/ansible_facts/*

# 7. Verify variables
ansible-inventory -i inventory.yml --host server1

# 8. Test specific task
ansible-playbook site.yml --start-at-task="Task Name" --limit server1

# 9. Full debug
ansible-playbook site.yml -vvvv --check --diff

# 10. Clean restart
sudo systemctl restart docker
sudo systemctl restart service_name
```

---

## Congratulations! 🎉

You've completed the **Getting Started Guide**!

### What You've Learned

✅ **Installation** - How to install and verify the collection  
✅ **First Playbook** - Running your first successful deployment  
✅ **Inventory Basics** - Organizing infrastructure and managing hosts  
✅ **Using Roles** - Deploying all 6 collection roles  
✅ **Common Patterns** - Production-ready patterns and best practices  
✅ **Troubleshooting** - Fixing common issues

### Next Steps

**For deeper knowledge:**
- **[User Guides](../user-guides/)** - Role-specific advanced topics
  - [Docker Complete Guide](../user-guides/docker/) - 8-part modular guide
  - [Podman Complete Guide](../user-guides/podman/) - Rootless containers
  - [GitHub Actions Runners](../user-guides/github-actions-runners/) - Advanced runner management
  - [Azure DevOps Agents](../user-guides/azure-devops-agents/) - Agent optimization
  - [GitLab CI Runners](../user-guides/gitlab-ci-runners/) - Runner configuration
  - [asdf Version Manager](../user-guides/asdf/) - Multi-language development

**For reference:**
- **[Variables Reference](../reference/VARIABLES.md)** - Complete variable documentation
- **[FAQ](../FAQ.md)** - Frequently asked questions
- **[Upgrade Guide](../maintenance/UPGRADE_GUIDE.md)** - Keeping collection updated

**For contributing:**
- **[Contributing Guide](../../CONTRIBUTING.md)** - How to contribute
- **[Development Guide](../development/)** - Collection development

---

[← Back: Common Patterns](05-common-patterns.md) | [User Guides →](../user-guides/README.md)
