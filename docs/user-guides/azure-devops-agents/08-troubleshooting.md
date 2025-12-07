# Part 8: Troubleshooting

This guide covers common issues, diagnostic commands, and complete reference tables for Azure DevOps agents.

## 📋 Table of Contents

- [Common Issues](#common-issues)
- [Diagnostic Commands](#diagnostic-commands)
- [Log Analysis](#log-analysis)
- [Reference Tables](#reference-tables)
- [FAQ](#faq)

## Common Issues

### Agent Registration Fails

#### Symptom: Authorization Error

```
VS30063: You are not authorized to access https://dev.azure.com/myorg
```

**Causes:**
1. PAT token invalid or expired
2. PAT missing required scopes
3. Network connectivity issues

**Solutions:**

```bash
# 1. Test PAT token
curl -s -u ":YOUR_PAT" \
  "https://dev.azure.com/myorg/_apis/projects?api-version=7.0" | jq .

# If this fails, create a new PAT with correct scopes

# 2. Check network connectivity
curl -I https://dev.azure.com/myorg

# 3. Verify PAT scopes
# Go to Azure DevOps → User Settings → Personal Access Tokens
# Ensure scopes match agent type (see Part 2)
```

#### Symptom: Pool Not Found

```
VS30011: Agent pool 'Linux-Pool' not found
```

**Solutions:**

```bash
# 1. List available pools (use PAT)
curl -s -u ":YOUR_PAT" \
  "https://dev.azure.com/myorg/_apis/distributedtask/pools?api-version=7.0" | jq '.value[] | {id, name}'

# 2. Create the pool in Azure DevOps
# Organization Settings → Agent pools → Add pool
```

#### Symptom: Deployment Group/Environment Not Found

```
TF400813: Resource not found for project 'ProjectName'
```

**Solutions:**

```yaml
# Enable auto-create
azure_devops_agents_list:
  - name: "agent"
    type: "deployment-group"  # or "environment"
    project: "ProjectName"
    deployment_group: "GroupName"
    auto_create: true         # ← Add this
```

### Service Won't Start

#### Symptom: Service Fails Immediately

```bash
$ systemctl status vsts.agent.myorg.agent-name
● vsts.agent.myorg.agent-name.service
   Active: failed (Result: exit-code)
```

**Diagnostic Steps:**

```bash
# 1. Check service logs
journalctl -u vsts.agent.myorg.agent-name --no-pager -n 50

# 2. Check agent diagnostic logs
cat /opt/azure-devops-agents/agent-name/_diag/Agent_*.log | tail -100

# 3. Check file permissions
ls -la /opt/azure-devops-agents/agent-name/

# 4. Verify agent user exists
id azagent

# 5. Try manual run
cd /opt/azure-devops-agents/agent-name
sudo -u azagent ./run.sh
```

#### Symptom: Permission Denied

```
System.UnauthorizedAccessException: Access to the path is denied
```

**Solutions:**

```bash
# Fix ownership
sudo chown -R azagent:azagent /opt/azure-devops-agents/agent-name

# Fix permissions
sudo chmod -R u+rwX /opt/azure-devops-agents/agent-name
```

### Package Conflicts

#### Symptom: curl-minimal Conflict (Rocky Linux)

```
Error: Problem: package curl-minimal conflicts with curl
```

**Solution:**

The role handles this automatically with `allowerasing: true`. Manual fix:

```bash
sudo dnf install curl --allowerasing
```

#### Symptom: libicu Missing

```
Failed to load libicu
```

**Solutions:**

```bash
# Ubuntu/Debian
sudo apt-get install -y libicu70  # or libicu72, depending on version

# RHEL/Rocky
sudo dnf install -y libicu
```

### Agent Shows Offline

#### Symptom: Agent Appears Offline in Azure DevOps

**Diagnostic Steps:**

```bash
# 1. Check if service is running
systemctl is-active vsts.agent.myorg.agent-name

# 2. Check network connectivity
curl -I https://dev.azure.com/myorg

# 3. Check agent logs for errors
tail -f /opt/azure-devops-agents/agent-name/_diag/Agent_*.log

# 4. Restart service
sudo systemctl restart vsts.agent.myorg.agent-name
```

**Common Causes:**
- Network firewall blocking outbound HTTPS
- DNS resolution issues
- PAT token expired
- System time out of sync

### Invalid Agent Name

#### Symptom: Agent Name Contains Invalid Characters

```
The agent name 'server.domain.com' contains invalid characters
```

**Solution:**

The role automatically sanitizes hostnames (replaces `.` with `-`). For custom naming:

```yaml
azure_devops_agents_list:
  - name: "custom-agent-name"  # Use alphanumeric and hyphens only
    type: "self-hosted"
    pool: "Default"
```

### Time Synchronization Issues

#### Symptom: Authentication Fails Intermittently

```
The time on the machine appears to be out of sync
```

**Solutions:**

```bash
# Check time sync status
timedatectl status

# Enable NTP
sudo timedatectl set-ntp true

# Verify
timedatectl status | grep synchronized
```

## Diagnostic Commands

### Service Management

```bash
# List all agent services
systemctl list-units 'vsts.agent.*'

# Check specific service
systemctl status vsts.agent.myorg.agent-name

# View service logs
journalctl -u vsts.agent.myorg.agent-name -f

# Restart service
sudo systemctl restart vsts.agent.myorg.agent-name

# Stop service
sudo systemctl stop vsts.agent.myorg.agent-name

# Start service
sudo systemctl start vsts.agent.myorg.agent-name
```

### Agent Files

```bash
# Agent directory
cd /opt/azure-devops-agents/agent-name

# View agent configuration
cat .agent | jq .

# View credentials info (no secrets shown)
cat .credentials | jq .

# List diagnostic logs
ls -la _diag/

# View latest agent log
tail -f _diag/Agent_$(date +%Y%m%d)*.log

# View worker logs
tail -f _diag/Worker_*.log

# Check disk usage
du -sh /opt/azure-devops-agents/*/

# Check work directory size
du -sh /opt/azure-devops-agents/*/_work/
```

### Network Diagnostics

```bash
# Test Azure DevOps connectivity
curl -I https://dev.azure.com/myorg

# Test with PAT
curl -s -u ":YOUR_PAT" \
  "https://dev.azure.com/myorg/_apis/projects?api-version=7.0" | jq .

# Check DNS resolution
nslookup dev.azure.com

# Test HTTPS connectivity
openssl s_client -connect dev.azure.com:443 -brief

# Check proxy settings (if configured)
cat /opt/azure-devops-agents/agent-name/.proxy
cat /opt/azure-devops-agents/agent-name/.proxybypass
```

### User and Permissions

```bash
# Check agent user
id azagent

# Check file ownership
ls -la /opt/azure-devops-agents/

# Check running processes
ps aux | grep Agent.Listener

# Check which user the service runs as
systemctl show vsts.agent.myorg.agent-name --property=User
```

## Log Analysis

### Agent Log Locations

```
/opt/azure-devops-agents/agent-name/
├── _diag/
│   ├── Agent_20240115-093045-utc.log     # Agent startup/connection logs
│   ├── Worker_20240115-093050-utc.log    # Job execution logs
│   └── capabilities.txt                   # Agent capabilities
└── _work/
    └── _temp/                             # Job-specific temp files
```

### Common Log Patterns

**Successful Connection:**
```
[2024-01-15 09:30:45Z INFO Agent] Agent connect to server successful.
[2024-01-15 09:30:45Z INFO Agent] Running job: BuildJob
```

**Connection Failed:**
```
[2024-01-15 09:30:45Z ERR Agent] Failed to connect. Will retry in 30 seconds.
[2024-01-15 09:30:45Z ERR Agent] Exception: HttpRequestException: Response status code does not indicate success: 401 (Unauthorized).
```

**Token Expired:**
```
[2024-01-15 09:30:45Z ERR Agent] Access token has expired.
```

### Log Rotation

Agent logs are automatically rotated. To manually clean old logs:

```bash
# Remove logs older than 7 days
find /opt/azure-devops-agents/*/_diag -name "*.log" -mtime +7 -delete
```

## Reference Tables

### All Role Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `azure_devops_agents_url` | string | **required** | Azure DevOps organization URL |
| `azure_devops_agents_pat` | string | **required** | Personal Access Token |
| `azure_devops_agents_list` | list | **required** | List of agents to configure |
| `azure_devops_agents_state` | string | `present` | Global state: present/absent |
| `azure_devops_agents_version` | string | `""` | Agent version (empty = latest) |
| `azure_devops_agents_base_path` | string | `/opt/azure-devops-agents` | Base directory |
| `azure_devops_agents_user` | string | `azagent` | Agent user |
| `azure_devops_agents_group` | string | `azagent` | Agent group |
| `azure_devops_agents_create_user` | bool | `true` | Create user if missing |
| `azure_devops_agents_run_as_service` | bool | `true` | Install as systemd service |
| `azure_devops_agents_service_enabled` | bool | `true` | Enable service on boot |
| `azure_devops_agents_service_state` | string | `started` | Service state |
| `azure_devops_agents_accept_tee_eula` | bool | `true` | Accept TEE EULA |
| `azure_devops_agents_delete_on_remove` | bool | `true` | Delete directory on removal |
| `azure_devops_agents_proxy_url` | string | `""` | Proxy URL |
| `azure_devops_agents_proxy_user` | string | `""` | Proxy username |
| `azure_devops_agents_proxy_password` | string | `""` | Proxy password |
| `azure_devops_agents_proxy_bypass` | string | `""` | Proxy bypass list |

### Agent List Properties

| Property | Type | Required | Agent Types | Description |
|----------|------|----------|-------------|-------------|
| `name` | string | Yes | All | Agent name |
| `type` | string | Yes | All | `self-hosted`, `deployment-group`, `environment` |
| `state` | string | No | All | `present` (default) or `absent` |
| `pool` | string | self-hosted | self-hosted | Agent pool name |
| `project` | string | DG/Env | DG, Env | Azure DevOps project name |
| `deployment_group` | string | DG | DG | Deployment group name |
| `environment` | string | Env | Env | Environment name |
| `auto_create` | bool | No | DG, Env | Create resource if missing |
| `open_access` | bool | No | Env | Allow all pipelines |
| `replace` | bool | No | All | Replace existing agent |
| `update_tags` | bool | No | DG, Env | Update tags via API |
| `work_dir` | string | No | All | Work directory name |
| `tags` | list | No | All | Agent tags/capabilities |

### API Endpoints Used

| Operation | HTTP Method | Endpoint |
|-----------|-------------|----------|
| List Pools | GET | `/_apis/distributedtask/pools` |
| List Agents | GET | `/_apis/distributedtask/pools/{poolId}/agents` |
| Create Deployment Group | POST | `/{project}/_apis/distributedtask/deploymentgroups` |
| List Deployment Groups | GET | `/{project}/_apis/distributedtask/deploymentgroups` |
| Create Environment | POST | `/{project}/_apis/pipelines/environments` |
| List Environments | GET | `/{project}/_apis/pipelines/environments` |
| Set Pipeline Permissions | PATCH | `/{project}/_apis/pipelines/pipelinepermissions/environment/{id}` |
| Update DG Agent Tags | PATCH | `/{project}/_apis/distributedtask/deploymentgroups/{dgId}/targets/{targetId}` |
| Update Env Agent Tags | PATCH | `/{project}/_apis/pipelines/environments/{envId}/providers/virtualmachines/{vmId}` |

### PAT Scopes Reference

| Agent Type | Required Scope | Permission Level |
|------------|----------------|------------------|
| Self-hosted | Agent Pools | Read & manage |
| Deployment Group | Deployment Groups | Read & manage |
| Environment | Environment | Read & manage |
| Auto-create DG | Deployment Groups | Read & manage |
| Auto-create Env | Environment | Read & manage |
| Open Access | Environment | Read & manage |
| Update Tags | Deployment Groups or Environment | Read & manage |

### Systemd Service Files

```
/etc/systemd/system/vsts.agent.{org}.{agent-name}.service

[Unit]
Description=Azure Pipelines Agent ({agent-name})
After=network.target

[Service]
ExecStart=/opt/azure-devops-agents/{agent-name}/runsvc.sh
User=azagent
WorkingDirectory=/opt/azure-devops-agents/{agent-name}
KillMode=process
KillSignal=SIGTERM
TimeoutStopSec=5min

[Install]
WantedBy=multi-user.target
```

## FAQ

### General Questions

**Q: Can I run multiple agents on one host?**

A: Yes! Configure multiple agents in `azure_devops_agents_list`. Each gets its own directory and systemd service.

**Q: Does the agent auto-update?**

A: Yes, by default. Azure DevOps pushes updates automatically. To pin a version, set `azure_devops_agents_version`.

**Q: Can agents run as root?**

A: No. Azure DevOps agents refuse to run as root for security reasons.

### Configuration Questions

**Q: How do I change agent tags after deployment?**

A: Set `update_tags: true` in the agent config and re-run the playbook. Works for Deployment Groups and Environments only.

**Q: How do I move an agent to a different pool?**

A: Remove the agent (`state: absent`), then redeploy with the new pool configuration.

**Q: Can I use the same agent name on different hosts?**

A: For self-hosted pools, yes (but not recommended). For Deployment Groups and Environments, each agent name must be unique.

### Troubleshooting Questions

**Q: Agent is online but jobs aren't running?**

A: Check:
1. Pool/Environment is assigned to the pipeline
2. Agent capabilities match job demands
3. Agent isn't disabled in Azure DevOps UI

**Q: How do I completely reset an agent?**

A: 
```bash
# Stop and remove
sudo systemctl stop vsts.agent.myorg.agent-name
cd /opt/azure-devops-agents/agent-name
sudo ./svc.sh uninstall
sudo ./config.sh remove --auth pat --token YOUR_PAT

# Delete directory
sudo rm -rf /opt/azure-devops-agents/agent-name

# Redeploy with Ansible
ansible-playbook install-agents.yml --ask-vault-pass
```

**Q: Jobs fail with "No space left on device"?**

A: Clean up work directories:
```bash
# Check disk usage
du -sh /opt/azure-devops-agents/*/_work/

# Clean old workspaces (be careful!)
# Best done through Azure DevOps pipeline settings
```

### Security Questions

**Q: Where are credentials stored?**

A: In `/opt/azure-devops-agents/{agent-name}/.credentials`. The file is encrypted by the agent.

**Q: How often should I rotate PATs?**

A: Every 90 days minimum. Set calendar reminders for rotation.

**Q: Can I restrict which pipelines use an agent?**

A: Yes. For Environments, use `open_access: false` and authorize specific pipelines. For pools, configure pool security in Azure DevOps.

---

## Quick Reference

### Documentation Map

```
... → 7. Security → [8. Troubleshooting] ← Complete!
```

### Emergency Commands

```bash
# Restart all agents
sudo systemctl restart 'vsts.agent.*'

# View all agent logs
journalctl -u 'vsts.agent.*' --since today

# Quick health check
systemctl list-units 'vsts.agent.*' --state=running

# Test Azure DevOps connectivity
curl -s -o /dev/null -w "%{http_code}" https://dev.azure.com/myorg
```

---

[← Previous: Security](07-security.md) | [Back to Guide Index](README.md)

---

## 🎉 Congratulations!

You've completed the Azure DevOps Agents Complete Guide! You now know how to:

- ✅ Deploy self-hosted, deployment group, and environment agents
- ✅ Configure auto-creation and open access
- ✅ Manage agents in production environments
- ✅ Secure your deployment with best practices
- ✅ Troubleshoot common issues

### Next Steps

- Explore the [Example Playbooks](../../../playbooks/azure_devops_agents/)
- Check the [Role README](../../../roles/azure_devops_agents/README.md) for quick reference
- Join our community for questions and support

Happy deploying! 🚀
