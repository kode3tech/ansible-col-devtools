# Part 8: Troubleshooting & FAQ

> 🎬 **Video Tutorial Section**: Learn to diagnose and fix common issues with GitHub Actions runners. This section covers error messages, diagnostic commands, and solutions for the most frequent problems.

## 📋 Table of Contents

- [Diagnostic Commands](#diagnostic-commands)
- [Common Errors and Solutions](#common-errors-and-solutions)
- [Service Management](#service-management)
- [Log Analysis](#log-analysis)
- [Registration Issues](#registration-issues)
- [Network Issues](#network-issues)
- [Permission Issues](#permission-issues)
- [Disk Space Issues](#disk-space-issues)
- [Frequently Asked Questions](#frequently-asked-questions)

---

## Diagnostic Commands

### Quick Health Check

```bash
# Check if runner service is running
systemctl status actions.runner.*

# List all runner services
systemctl list-units 'actions.runner.*' --no-pager

# Check runner logs (last 50 lines)
journalctl -u 'actions.runner.*' -n 50

# Check disk usage
df -h /opt/github-actions-runners

# Check runner user
id ghrunner

# Check network connectivity to GitHub
curl -sI https://api.github.com | head -5
```

### Detailed Diagnostic Script

```bash
#!/bin/bash
# runner-diagnostics.sh
# Comprehensive runner health check

echo "════════════════════════════════════════════════════════════════"
echo "GitHub Actions Runner Diagnostics"
echo "════════════════════════════════════════════════════════════════"

echo ""
echo "📋 RUNNER SERVICES"
echo "────────────────────────────────────────────────────────────────"
systemctl list-units 'actions.runner.*' --no-pager

echo ""
echo "💾 DISK USAGE"
echo "────────────────────────────────────────────────────────────────"
df -h /opt/github-actions-runners
du -sh /opt/github-actions-runners/*/

echo ""
echo "👤 RUNNER USER"
echo "────────────────────────────────────────────────────────────────"
id ghrunner 2>/dev/null || echo "User ghrunner not found!"
groups ghrunner 2>/dev/null || echo ""

echo ""
echo "🌐 NETWORK CONNECTIVITY"
echo "────────────────────────────────────────────────────────────────"
echo "GitHub API: $(curl -sI https://api.github.com | head -1)"
echo "GitHub: $(curl -sI https://github.com | head -1)"

echo ""
echo "📁 RUNNER DIRECTORIES"
echo "────────────────────────────────────────────────────────────────"
ls -la /opt/github-actions-runners/

echo ""
echo "🔧 RUNNER CONFIGURATIONS"
echo "────────────────────────────────────────────────────────────────"
for dir in /opt/github-actions-runners/*/; do
  if [ -f "$dir/.runner" ]; then
    echo "Runner: $(basename $dir)"
    cat "$dir/.runner" | jq '.' 2>/dev/null || cat "$dir/.runner"
    echo ""
  fi
done

echo ""
echo "📊 RECENT LOGS (last 10 lines per runner)"
echo "────────────────────────────────────────────────────────────────"
for service in $(systemctl list-units 'actions.runner.*' --no-pager --no-legend | awk '{print $1}'); do
  echo "=== $service ==="
  journalctl -u "$service" -n 10 --no-pager
  echo ""
done
```

---

## Common Errors and Solutions

### Error: "Token is invalid or expired"

```
┌─────────────────────────────────────────────────────────────────────────┐
│ ERROR: Could not authenticate with provided token                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│ CAUSES:                                                                  │
│ • Token has expired (PATs expire)                                       │
│ • Token lacks required permissions                                      │
│ • Wrong token type (classic vs fine-grained)                           │
│ • Token was revoked                                                     │
│                                                                          │
│ SOLUTION:                                                                │
│ 1. Generate new PAT at github.com/settings/tokens                       │
│ 2. Ensure permissions:                                                  │
│    • Organization scope: admin:org                                      │
│    • Repository scope: repo                                             │
│ 3. Update vault with new token                                          │
│ 4. Re-run playbook                                                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Fix:**

```bash
# Generate new token and update vault
ansible-vault edit vars/github_secrets.yml

# Update vault_github_token with new token
# Save and re-run playbook

ansible-playbook playbook.yml -i inventory.ini --ask-vault-pass
```

### Error: "Runner with same name already exists"

```
┌─────────────────────────────────────────────────────────────────────────┐
│ ERROR: A runner with the name 'runner-01' already exists                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│ CAUSES:                                                                  │
│ • Runner was registered but not removed before re-registering           │
│ • Previous failed installation left orphan registration                 │
│ • Same name used on different server                                    │
│                                                                          │
│ SOLUTION A: Replace existing runner                                     │
│ Add replace_existing: true to runner config                             │
│                                                                          │
│ SOLUTION B: Remove from GitHub first                                    │
│ 1. Go to org settings → Actions → Runners                               │
│ 2. Find and remove the orphan runner                                    │
│ 3. Re-run playbook                                                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Fix A: Replace in playbook:**

```yaml
github_actions_runners_replace_existing: true

github_actions_runners_list:
  - name: "runner-01"
    # Will replace existing registration
```

**Fix B: Remove from GitHub UI:**

1. Go to `https://github.com/organizations/YOURORG/settings/actions/runners`
2. Find the orphan runner
3. Click "Remove"
4. Re-run playbook

### Error: "Permission denied" during installation

```
┌─────────────────────────────────────────────────────────────────────────┐
│ ERROR: Permission denied: /opt/github-actions-runners/runner-01         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│ CAUSES:                                                                  │
│ • Directory owned by different user                                     │
│ • Running without become: true                                          │
│ • SELinux blocking access                                               │
│                                                                          │
│ SOLUTION:                                                                │
│ 1. Ensure become: true in playbook                                      │
│ 2. Fix ownership: chown -R ghrunner:ghrunner /opt/github-actions-runners│
│ 3. Check SELinux: restorecon -Rv /opt/github-actions-runners            │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Fix:**

```bash
# Fix ownership
sudo chown -R ghrunner:ghrunner /opt/github-actions-runners

# Restore SELinux context (RHEL/CentOS)
sudo restorecon -Rv /opt/github-actions-runners

# Verify
ls -la /opt/github-actions-runners/
```

### Error: "Service failed to start"

```
┌─────────────────────────────────────────────────────────────────────────┐
│ ERROR: actions.runner.org.runner-01.service: Failed with result 'exit'  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│ CAUSES:                                                                  │
│ • Missing dependencies                                                  │
│ • Corrupt installation                                                  │
│ • Missing .runner or .credentials files                                 │
│ • Incorrect user permissions                                            │
│                                                                          │
│ SOLUTION:                                                                │
│ 1. Check detailed logs: journalctl -u actions.runner.*.runner-01 -n 100│
│ 2. Verify files exist: ls -la /opt/github-actions-runners/runner-01/    │
│ 3. Check permissions: namei -l /opt/github-actions-runners/runner-01    │
│ 4. Try manual start: sudo -u ghrunner ./run.sh                          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Diagnostic:**

```bash
# Get detailed service status
systemctl status actions.runner.*.runner-01 -l

# Check logs
journalctl -u actions.runner.*.runner-01 -n 100 --no-pager

# Try manual start to see errors
cd /opt/github-actions-runners/runner-01
sudo -u ghrunner ./run.sh
```

### Error: "Runner group not found"

```
┌─────────────────────────────────────────────────────────────────────────┐
│ ERROR: Runner group 'production' not found                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│ CAUSES:                                                                  │
│ • Group doesn't exist yet (first run)                                   │
│ • Wrong group name spelling                                             │
│ • Token lacks permission to create groups                               │
│                                                                          │
│ SOLUTION:                                                                │
│ 1. Define group in github_actions_runners_groups                        │
│ 2. Verify spelling matches exactly                                      │
│ 3. Ensure token has admin:org permission                                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Fix:**

```yaml
# Define the group BEFORE referencing it
github_actions_runners_groups:
  - name: "production"        # Exact name
    visibility: "selected"

github_actions_runners_list:
  - name: "runner-01"
    runner_group: "production"  # Must match exactly!
```

---

## Service Management

### Starting and Stopping Runners

```bash
# List all runner services
systemctl list-units 'actions.runner.*'

# Stop specific runner
sudo systemctl stop actions.runner.myorg.runner-01

# Start specific runner
sudo systemctl start actions.runner.myorg.runner-01

# Restart all runners
sudo systemctl restart 'actions.runner.*'

# Check status
systemctl status 'actions.runner.*'
```

### Enabling/Disabling Auto-Start

```bash
# Disable auto-start for a runner
sudo systemctl disable actions.runner.myorg.runner-01

# Enable auto-start
sudo systemctl enable actions.runner.myorg.runner-01

# Check if enabled
systemctl is-enabled actions.runner.myorg.runner-01
```

### Service File Location

```bash
# Service files are located at:
/etc/systemd/system/actions.runner.*.service

# View service file
cat /etc/systemd/system/actions.runner.myorg.runner-01.service

# Reload after manual changes
sudo systemctl daemon-reload
```

---

## Log Analysis

### Log Locations

```
/opt/github-actions-runners/runner-01/
├── _diag/
│   ├── Runner_20240115-123456-utc.log    # Runner process logs
│   ├── Worker_20240115-123456-utc.log    # Job execution logs
│   └── pages/                            # GitHub Actions step logs
```

### Viewing Logs

```bash
# Real-time log streaming (systemd)
journalctl -u 'actions.runner.*' -f

# Last 100 lines
journalctl -u actions.runner.myorg.runner-01 -n 100

# Since specific time
journalctl -u 'actions.runner.*' --since "1 hour ago"

# Between dates
journalctl -u 'actions.runner.*' --since "2024-01-15 00:00" --until "2024-01-15 23:59"

# Export to file
journalctl -u 'actions.runner.*' --since today > /tmp/runner-logs.txt
```

### Log Analysis Commands

```bash
# Count errors in logs
journalctl -u 'actions.runner.*' --since today | grep -i error | wc -l

# Find connection issues
journalctl -u 'actions.runner.*' | grep -i "connection\|timeout\|network"

# Find authentication issues
journalctl -u 'actions.runner.*' | grep -i "auth\|token\|credential"

# Find job failures
journalctl -u 'actions.runner.*' | grep -i "fail\|error\|exception"
```

---

## Registration Issues

### Re-registering a Runner

```bash
# Stop the service
sudo systemctl stop actions.runner.myorg.runner-01

# Navigate to runner directory
cd /opt/github-actions-runners/runner-01

# Remove registration (unregister from GitHub)
sudo -u ghrunner ./config.sh remove --token YOUR_TOKEN

# Re-register
sudo -u ghrunner ./config.sh \
  --url https://github.com/myorg \
  --token YOUR_TOKEN \
  --name runner-01 \
  --labels docker,linux \
  --unattended

# Start service
sudo systemctl start actions.runner.myorg.runner-01
```

### Checking Registration Status

```bash
# Check if registered
cat /opt/github-actions-runners/runner-01/.runner | jq '.'

# Output shows:
# {
#   "agentId": 12345,
#   "agentName": "runner-01",
#   "poolId": 1,
#   "serverUrl": "https://pipelines.actions.githubusercontent.com/..."
# }
```

---

## Network Issues

### Testing Connectivity

```bash
# Test GitHub API
curl -sI https://api.github.com | head -5

# Test with authentication
curl -sH "Authorization: token YOUR_TOKEN" https://api.github.com/user

# Test runner download URL
curl -sI https://github.com/actions/runner/releases/latest

# Test with timeout
curl -m 10 -sI https://api.github.com
```

### Proxy Configuration

```yaml
# If behind proxy, add to playbook
github_actions_runners_proxy_url: "http://proxy.company.com:8080"
github_actions_runners_no_proxy: "localhost,127.0.0.1,internal.company.com"
```

**Manual proxy setup:**

```bash
# Set for current session
export https_proxy="http://proxy.company.com:8080"
export http_proxy="http://proxy.company.com:8080"
export no_proxy="localhost,127.0.0.1"

# Test
curl -sI https://api.github.com | head -5
```

### DNS Issues

```bash
# Check DNS resolution
nslookup api.github.com
nslookup github.com

# Check /etc/resolv.conf
cat /etc/resolv.conf

# Test with specific DNS
nslookup api.github.com 8.8.8.8
```

---

## Permission Issues

### Common Permission Fixes

```bash
# Fix runner directory ownership
sudo chown -R ghrunner:ghrunner /opt/github-actions-runners

# Fix specific runner
sudo chown -R ghrunner:ghrunner /opt/github-actions-runners/runner-01

# Fix permissions
sudo chmod -R 700 /opt/github-actions-runners

# Restore SELinux context (RHEL/CentOS)
sudo restorecon -Rv /opt/github-actions-runners
```

### Docker Permission (if needed)

```bash
# Add runner user to docker group
sudo usermod -aG docker ghrunner

# Verify
groups ghrunner

# Restart runner for changes to take effect
sudo systemctl restart actions.runner.*.runner-01
```

---

## Disk Space Issues

### Checking Disk Usage

```bash
# Overall disk usage
df -h /opt/github-actions-runners

# Per-runner usage
du -sh /opt/github-actions-runners/*/

# Find large files
find /opt/github-actions-runners -type f -size +100M -exec ls -lh {} \;

# Work folder usage
du -sh /opt/github-actions-runners/*/_work/
```

### Manual Cleanup

```bash
# Clean old work folders (older than 7 days)
find /opt/github-actions-runners/*/_work -type d -mtime +7 -exec rm -rf {} \;

# Clean temporary files
find /opt/github-actions-runners/*/_work/_temp -type f -mtime +1 -delete

# Clean tool cache
rm -rf /opt/github-actions-runners/*/_work/_tool/*

# ⚠️ CAREFUL: This deletes all job data!
# rm -rf /opt/github-actions-runners/*/_work/*
```

### Preventing Disk Issues

```yaml
# Enable automatic cleanup in playbook
github_actions_runners_work_folder_cleanup_days: 7
github_actions_runners_cleanup_toolcache: true
github_actions_runners_toolcache_cleanup_days: 30
```

---

## Frequently Asked Questions

### General Questions

#### Q: How do I update runners to the latest version?

**A:** Set version to empty string and re-run playbook:

```yaml
github_actions_runners_version: ""  # Empty = latest
```

Then run:
```bash
ansible-playbook playbook.yml -i inventory.ini --ask-vault-pass
```

#### Q: Can I run multiple runners on one server?

**A:** Yes! Add multiple entries to the list:

```yaml
github_actions_runners_list:
  - name: "runner-01"
  - name: "runner-02"
  - name: "runner-03"
```

#### Q: How do I change labels after deployment?

**A:** Update labels in playbook and re-run. Labels are updated via GitHub API:

```yaml
github_actions_runners_list:
  - name: "runner-01"
    labels:
      - "new-label"
      - "another-label"
```

### Token Questions

#### Q: What token permissions do I need?

**A:** 

| Scope | Required Permission |
|-------|---------------------|
| Organization | `admin:org` |
| Repository | `repo` |
| Enterprise | `enterprise:admin` |

#### Q: My token expired, what do I do?

**A:** 
1. Generate new token at github.com/settings/tokens
2. Update vault: `ansible-vault edit vars/github_secrets.yml`
3. Re-run playbook

#### Q: Can I use a GitHub App instead of PAT?

**A:** Currently the role supports PAT tokens. GitHub App support may be added in future versions.

### Troubleshooting Questions

#### Q: Runner shows offline in GitHub but service is running?

**A:** Check network connectivity:

```bash
# Test connectivity
curl -sI https://api.github.com | head -5

# Check logs for errors
journalctl -u actions.runner.*.runner-01 -n 50 | grep -i error

# Restart the service
sudo systemctl restart actions.runner.*.runner-01
```

#### Q: Jobs are queued but not running?

**A:** Check:
1. Runner is online (green dot in GitHub UI)
2. Labels match workflow `runs-on`
3. Runner group allows the repository
4. No other job is running (if not ephemeral)

#### Q: How do I debug a failing job?

**A:** 
1. Check GitHub Actions workflow logs (in browser)
2. Check runner logs: `journalctl -u actions.runner.*.runner-01 -f`
3. Check `_diag/` folder for detailed logs

### Performance Questions

#### Q: How do I make runners faster?

**A:**
1. Use SSD storage
2. Add more RAM (4GB+ recommended)
3. Enable caching in workflows
4. Use multiple runners for parallelism
5. Consider ephemeral runners for clean state

#### Q: How many runners should I deploy?

**A:** Depends on:
- Number of concurrent workflows
- Average job duration
- Peak usage times

Start with 2-3 per server and monitor queue times.

---

## Quick Reference Card

### Essential Commands

| Task | Command |
|------|---------|
| List services | `systemctl list-units 'actions.runner.*'` |
| Check status | `systemctl status 'actions.runner.*'` |
| View logs | `journalctl -u 'actions.runner.*' -f` |
| Restart all | `systemctl restart 'actions.runner.*'` |
| Check disk | `df -h /opt/github-actions-runners` |
| Fix permissions | `chown -R ghrunner:ghrunner /opt/github-actions-runners` |

### Key File Locations

| Path | Description |
|------|-------------|
| `/opt/github-actions-runners/` | Base installation directory |
| `{runner}/_diag/` | Runner diagnostic logs |
| `{runner}/_work/` | Job work directory |
| `{runner}/.runner` | Runner configuration |
| `{runner}/.credentials` | Authentication credentials |
| `/etc/systemd/system/actions.runner.*.service` | Service files |

### Ansible Tags

```bash
# Run only cleanup tasks
ansible-playbook playbook.yml --tags cleanup

# Run only registration tasks
ansible-playbook playbook.yml --tags register

# Skip cleanup during deployment
ansible-playbook playbook.yml --skip-tags cleanup
```

---

**This completes the GitHub Actions Runners Complete Guide!**

← **Previous Section**: [Part 7: Security Best Practices](07-security.md)

---

[← Back to User Guides](../README.md)
