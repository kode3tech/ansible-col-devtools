# Inventory Basics

Learn how to organize and manage your infrastructure with Ansible inventory files.

## 📋 Table of Contents

- [What is an Inventory?](#what-is-an-inventory)
- [Inventory Formats](#inventory-formats)
- [Groups and Patterns](#groups-and-patterns)
- [Variables in Inventory](#variables-in-inventory)
- [Dynamic Inventory](#dynamic-inventory)
- [Best Practices](#best-practices)

---

## What is an Inventory?

An **inventory** defines **where** Ansible will run tasks. It's a list of managed hosts (servers) organized into groups.

**Think of it as:**
- 📋 Address book of your servers
- 🏷️ Organized by environment, role, or location
- 🔧 With configuration specific to each host

---

## Inventory Formats

### INI Format (Simple)

Create `inventory`:

```ini
# Single host
webserver.example.com

# Multiple hosts
webserver1.example.com
webserver2.example.com

# Hosts in a group
[webservers]
web1.example.com
web2.example.com

[databases]
db1.example.com
db2.example.com
```

### YAML Format (Structured)

Create `inventory.yml`:

```yaml
all:
  children:
    webservers:
      hosts:
        web1.example.com:
        web2.example.com:
    databases:
      hosts:
        db1.example.com:
        db2.example.com:
```

**When to use each:**
- **INI**: Simple, quick to write, easier to read
- **YAML**: Complex hierarchies, better for version control

---

## Groups and Patterns

### Basic Groups

```ini
[production]
prod-web-01.example.com
prod-web-02.example.com
prod-db-01.example.com

[staging]
staging-web-01.example.com
staging-db-01.example.com

[development]
dev-server-01.example.com
```

**Target specific groups in playbooks:**

```yaml
- hosts: production        # Only production servers
- hosts: staging           # Only staging servers
- hosts: all               # ALL servers
```

### Nested Groups

Create logical hierarchies:

```ini
[webservers]
web1.example.com
web2.example.com

[databases]
db1.example.com
db2.example.com

# Nested group
[production:children]
webservers
databases

[staging:children]
staging_webservers
staging_databases
```

Use in playbooks:
```yaml
- hosts: production        # Targets webservers + databases
```

### Patterns

Target multiple groups or specific hosts:

```yaml
# Multiple groups
- hosts: webservers:databases

# Exclude groups
- hosts: all:!staging              # All except staging

# Intersection (both groups)
- hosts: webservers:&production    # Only production webservers

# Wildcards
- hosts: *.example.com
- hosts: web*.example.com
```

---

## Variables in Inventory

### Host Variables

```ini
[webservers]
web1.example.com ansible_user=ubuntu ansible_port=22
web2.example.com ansible_user=admin ansible_port=2222
```

**Common host variables:**

| Variable | Purpose | Example |
|----------|---------|---------|
| `ansible_host` | IP address or hostname | `192.168.1.100` |
| `ansible_user` | SSH username | `ubuntu`, `admin` |
| `ansible_port` | SSH port | `22`, `2222` |
| `ansible_ssh_private_key_file` | SSH key path | `~/.ssh/id_rsa` |
| `ansible_python_interpreter` | Python path | `/usr/bin/python3` |
| `ansible_become_user` | Sudo to this user | `root` |

### Group Variables

```ini
[webservers]
web1.example.com
web2.example.com

[webservers:vars]
ansible_user=ubuntu
http_port=80
```

**Or use separate files:**

```
inventory/
├── hosts                          # Main inventory
├── group_vars/
│   ├── all.yml                   # Variables for ALL hosts
│   ├── webservers.yml            # Variables for webservers group
│   └── production.yml            # Variables for production group
└── host_vars/
    ├── web1.example.com.yml      # Variables for specific host
    └── db1.example.com.yml
```

**Example `group_vars/webservers.yml`:**
```yaml
---
ansible_user: ubuntu
docker_users:
  - www-data
  - deploy
nginx_port: 80
```

### Variable Precedence

**From lowest to highest priority:**

1. `group_vars/all.yml`
2. `group_vars/{group_name}.yml`
3. `host_vars/{hostname}.yml`
4. Inventory file host variables
5. Playbook variables (`vars:`)
6. Command-line variables (`-e`)

**Example:**
```bash
# This will override all other variables
ansible-playbook -i inventory playbook.yml -e "docker_version=24.0.7"
```

---

## Dynamic Inventory

### Use Case

Instead of static files, generate inventory dynamically from:
- Cloud providers (AWS, Azure, GCP)
- Configuration management databases (CMDB)
- Container orchestrators (Kubernetes)

### Example: AWS EC2 Dynamic Inventory

**Install AWS collection:**
```bash
ansible-galaxy collection install amazon.aws
```

**Create `aws_ec2.yml`:**
```yaml
---
plugin: amazon.aws.aws_ec2
regions:
  - us-east-1
  - us-west-2
filters:
  tag:Environment:
    - production
keyed_groups:
  - key: tags.Role
    prefix: role
```

**Use dynamic inventory:**
```bash
ansible-inventory -i aws_ec2.yml --graph
```

**Output:**
```
@all:
  |--@role_webserver:
  |  |--ec2-54-123-45-67.compute-1.amazonaws.com
  |  |--ec2-54-123-45-68.compute-1.amazonaws.com
  |--@role_database:
  |  |--ec2-54-123-45-69.compute-1.amazonaws.com
```

---

## Real-World Examples

### Example 1: Multi-Environment Setup

```ini
# inventory/production
[webservers]
prod-web-01.example.com
prod-web-02.example.com
prod-web-03.example.com

[databases]
prod-db-01.example.com
prod-db-02.example.com

[all:vars]
ansible_user=ubuntu
env=production
```

```ini
# inventory/staging
[webservers]
staging-web-01.example.com

[databases]
staging-db-01.example.com

[all:vars]
ansible_user=ubuntu
env=staging
```

**Run playbook per environment:**
```bash
# Production
ansible-playbook -i inventory/production deploy.yml

# Staging
ansible-playbook -i inventory/staging deploy.yml
```

### Example 2: CI/CD Infrastructure

```ini
[ci_servers]
jenkins-01.example.com
gitlab-runner-01.example.com
github-runner-01.example.com

[ci_servers:vars]
ansible_user=ubuntu
docker_users=['jenkins', 'runner']

[docker_hosts]
docker-01.example.com
docker-02.example.com

[docker_hosts:vars]
ansible_user=admin
docker_daemon_config={'log-driver': 'json-file', 'log-opts': {'max-size': '10m'}}

[monitoring]
prometheus-01.example.com
grafana-01.example.com

[all:vars]
ansible_python_interpreter=/usr/bin/python3
```

### Example 3: Geographic Distribution

```ini
[us_east]
web-us-east-01.example.com
web-us-east-02.example.com

[us_west]
web-us-west-01.example.com
web-us-west-02.example.com

[europe]
web-eu-west-01.example.com
web-eu-west-02.example.com

[us:children]
us_east
us_west

[all_webservers:children]
us
europe

[all_webservers:vars]
ansible_user=ubuntu
ntp_server=time.google.com
```

---

## Testing Inventory

### List All Hosts

```bash
ansible-inventory -i inventory --list
```

Output (JSON):
```json
{
  "all": {
    "children": ["webservers", "databases"]
  },
  "webservers": {
    "hosts": ["web1.example.com", "web2.example.com"]
  }
}
```

### List Specific Group

```bash
ansible-inventory -i inventory --graph webservers
```

Output:
```
@webservers:
  |--web1.example.com
  |--web2.example.com
```

### Test Connectivity

```bash
# Ping all hosts
ansible -i inventory all -m ping

# Ping specific group
ansible -i inventory webservers -m ping

# Ping specific host
ansible -i inventory web1.example.com -m ping
```

### Run Ad-Hoc Commands

```bash
# Get hostname from all hosts
ansible -i inventory all -m command -a "hostname"

# Check disk space
ansible -i inventory all -m shell -a "df -h"

# Gather facts (system information)
ansible -i inventory all -m setup
```

---

## Best Practices

### ✅ Do's

1. **Use descriptive group names**
   ```ini
   [production_webservers]    # ✅ Clear
   [web]                      # ❌ Ambiguous
   ```

2. **Separate environments**
   ```
   inventory/
   ├── production
   ├── staging
   └── development
   ```

3. **Use group_vars for shared configuration**
   ```yaml
   # group_vars/webservers.yml
   docker_users: ['deploy', 'www-data']
   nginx_port: 80
   ```

4. **Version control your inventory**
   ```bash
   git add inventory/ group_vars/ host_vars/
   ```

5. **Document your inventory structure**
   ```ini
   # inventory/production
   # Production environment
   # Updated: 2025-12-17
   # Contact: devops@example.com
   ```

### ❌ Don'ts

1. **Don't hardcode secrets in inventory**
   ```ini
   # ❌ BAD
   [databases]
   db1.example.com db_password=secret123

   # ✅ GOOD - Use Ansible Vault
   [databases]
   db1.example.com
   
   # In group_vars/databases.yml (encrypted)
   db_password: "{{ vault_db_password }}"
   ```

2. **Don't use `ansible_password` in inventory**
   ```ini
   # ❌ Security risk
   server1.example.com ansible_password=mypassword

   # ✅ Use SSH keys instead
   server1.example.com ansible_ssh_private_key_file=~/.ssh/id_rsa
   ```

3. **Don't duplicate configuration**
   ```ini
   # ❌ Repetitive
   [webservers]
   web1.example.com ansible_user=ubuntu ansible_port=22
   web2.example.com ansible_user=ubuntu ansible_port=22
   web3.example.com ansible_user=ubuntu ansible_port=22

   # ✅ Use group variables
   [webservers]
   web1.example.com
   web2.example.com
   web3.example.com

   [webservers:vars]
   ansible_user=ubuntu
   ansible_port=22
   ```

---

## Troubleshooting

### "No hosts matched"

**Problem:**
```bash
ansible-playbook -i inventory playbook.yml
# ERROR! No hosts matched
```

**Solutions:**

1. **Check group name in playbook:**
   ```yaml
   hosts: webservers  # Must match group in inventory
   ```

2. **Verify inventory file:**
   ```bash
   ansible-inventory -i inventory --list
   ```

3. **Test host connectivity:**
   ```bash
   ansible -i inventory all -m ping
   ```

### "Unreachable hosts"

**Problem:**
```
TASK [Gathering Facts]
fatal: [server1.example.com]: UNREACHABLE!
```

**Solutions:**

1. **Check SSH connectivity:**
   ```bash
   ssh ubuntu@server1.example.com
   ```

2. **Verify ansible_user:**
   ```ini
   [webservers]
   server1.example.com ansible_user=correct_username
   ```

3. **Test with ping module:**
   ```bash
   ansible -i inventory server1.example.com -m ping -vvv
   ```

---

## Next Steps

✅ **Mastered inventory!** Continue learning:

1. **[Using Roles](04-using-roles.md)** - Deploy Docker, Podman, CI/CD runners
2. **[Common Patterns](05-common-patterns.md)** - Multi-environment, vault, tags
3. **[Troubleshooting Guide](06-troubleshooting.md)** - Fix common issues

---

[← Back: First Playbook](02-first-playbook.md) | [Next: Using Roles →](04-using-roles.md)
