# Part 8: Troubleshooting

## 📋 Table of Contents

- [Service Issues](#service-issues)
- [Registration and API Errors](#registration-and-api-errors)
- [Pipeline Execution Problems](#pipeline-execution-problems)
- [Docker Executor Issues](#docker-executor-issues)
- [Performance Problems](#performance-problems)
- [Verification Commands](#verification-commands)

---

## Service Issues

### Runner Service Won't Start

**Symptom:**
```bash
$ systemctl status gitlab-runner@myrunner.service
● gitlab-runner@myrunner.service - GitLab Runner (myrunner)
   Loaded: loaded
   Active: failed (Result: exit-code)
```

**Diagnosis:**
```bash
# Check detailed logs
journalctl -u gitlab-runner@myrunner.service -n 50 --no-pager

# Check configuration syntax
sudo /usr/bin/gitlab-runner verify \
  --config /etc/gitlab-runner/myrunner/config.toml
```

**Common causes:**

#### 1. Invalid config.toml

```bash
# Check for syntax errors
cat /etc/gitlab-runner/myrunner/config.toml

# Look for:
# - Missing quotes
# - Unbalanced brackets
# - Invalid TOML syntax
```

**Fix:** Regenerate config by running playbook again.

#### 2. Missing runner user

```bash
# Check if user exists
id gitlab-runner

# If not found, create:
sudo useradd -r -d /opt/gitlab-ci-runners -s /bin/bash gitlab-runner
```

#### 3. Permission issues

```bash
# Fix permissions
sudo chown -R gitlab-runner:gitlab-runner /etc/gitlab-runner/myrunner
sudo chown -R gitlab-runner:gitlab-runner /opt/gitlab-ci-runners/myrunner
sudo chmod 700 /etc/gitlab-runner/myrunner
```

### Runner Shows Offline in GitLab

**Symptom:** Runner appears offline in GitLab UI, even though service is running.

**Diagnosis:**
```bash
# 1. Check service is actually running
systemctl status gitlab-runner-myrunner.service

# 2. Check network connectivity
curl -I https://gitlab.com

# 3. Check runner logs for connection errors
journalctl -u gitlab-runner-myrunner.service -f
```

**Common causes:**

#### 1. Invalid runner token

```bash
# Check config.toml token
sudo cat /etc/gitlab-runner/myrunner/config.toml | grep token

# Token should start with "glrt-" (runner token)
# NOT "glpat-" (personal access token)
```

**Fix:** Re-run Ansible playbook to regenerate runner.

#### 2. Network/firewall blocking GitLab

```bash
# Test HTTPS connectivity
curl -v https://gitlab.com/api/v4/version

# Test from runner user
sudo -u gitlab-runner curl -v https://gitlab.com/api/v4/version
```

**Fix:** Adjust firewall rules to allow outbound HTTPS.

#### 3. GitLab URL mismatch

```bash
# Check configured URL
grep "url = " /etc/gitlab-runner/myrunner/config.toml

# Should match your GitLab instance
# gitlab.com → url = "https://gitlab.com"
# Self-hosted → url = "https://gitlab.yourcompany.com"
```

**Fix:** Update `gitlab_ci_runners_gitlab_url` in playbook.

---

## Registration and API Errors

### API Token Issues

**Error:**
```
Failed to create runner: 401 Unauthorized
```

**Diagnosis:**
```bash
# Test API token
curl -H "PRIVATE-TOKEN: YOUR_TOKEN" \
  https://gitlab.com/api/v4/user
```

**Causes and fixes:**

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Invalid token | Create new PAT, update vault |
| 403 Forbidden | Insufficient scopes | Add `api`, `create_runner` scopes |
| Token expired | Token past expiration | Create new PAT with longer expiry |

### Group/Project Not Found

**Error:**
```
Failed to create runner: 404 Not Found
Group 'myteam' does not exist
```

**Diagnosis:**
```bash
# Verify group exists
curl -H "PRIVATE-TOKEN: YOUR_TOKEN" \
  https://gitlab.com/api/v4/groups/myteam
```

**Fixes:**

1. **Enable auto-create:**
```yaml
gitlab_ci_runners_auto_create_group: true
gitlab_ci_runners_group_visibility: "private"
```

2. **Verify group path:**
```yaml
# Use full path (case-sensitive!)
gitlab_ci_runners_api_group_full_path: "my-team"  # NOT "My Team"
```

3. **Verify project ID:**
```bash
# Get project ID from GitLab
# Project → Settings → General → Project ID
gitlab_ci_runners_api_project_id: "12345678"  # Numeric ID
```

### PAT Scope Insufficient

**Error:**
```
Failed to create runner: 403 Forbidden
Insufficient permissions to create runner
```

**Fix:** Recreate PAT with correct scopes:
- ✅ `api` - Full API access
- ✅ `read_api` - Read-only API
- ✅ `create_runner` - Create runners

---

## Pipeline Execution Problems

### Jobs Not Picked Up by Runner

**Symptom:** Pipeline stuck on "pending", never starts.

**Diagnosis:**
```bash
# Check runner is online
curl -H "PRIVATE-TOKEN: YOUR_TOKEN" \
  https://gitlab.com/api/v4/runners | jq '.[] | select(.description=="myrunner")'

# Check runner tags
cat /etc/gitlab-runner/myrunner/config.toml | grep "tags ="
```

**Common causes:**

#### 1. Tag mismatch

```yaml
# .gitlab-ci.yml
job:
  tags: [docker, linux, nodejs]  # Requires ALL these tags
  script: npm test

# Runner must have ALL tags
tags = ["docker", "linux", "nodejs"]  # ✅ Match
tags = ["docker", "linux"]            # ❌ Missing "nodejs"
```

**Fix:** Update runner tags in playbook:
```yaml
gitlab_ci_runners_list:
  - name: "myrunner"
    tags:
      - docker
      - linux
      - nodejs  # Add missing tag
```

#### 2. Runner paused

```bash
# Check if runner is paused
curl -H "PRIVATE-TOKEN: YOUR_TOKEN" \
  https://gitlab.com/api/v4/runners | jq '.[] | select(.description=="myrunner") | .active'

# Should return: true
```

**Fix:** Unpause via GitLab UI or API:
```bash
curl -X PUT -H "PRIVATE-TOKEN: YOUR_TOKEN" \
  "https://gitlab.com/api/v4/runners/RUNNER_ID" \
  -d "active=true"
```

#### 3. Protected branch restrictions

```yaml
# Runner configured for protected branches only
access_level: "ref_protected"

# Job runs on feature branch (not protected)
# → Runner won't pick it up!
```

**Fix:** Either:
- Use `access_level: "not_protected"` for dev runners
- Or protect the branch in GitLab settings

### Job Fails with "Executor Not Found"

**Error:**
```
ERROR: Executor "docker" not found
```

**Diagnosis:**
```bash
# Check Docker is installed
docker --version

# Check Docker is running
systemctl status docker

# Check runner user has Docker access
sudo -u gitlab-runner docker ps
```

**Fix:**
```bash
# Add runner user to docker group
sudo usermod -aG docker gitlab-runner

# Restart runner service
sudo systemctl restart gitlab-runner-myrunner.service
```

---

## Docker Executor Issues

### "Cannot Connect to Docker Daemon"

**Error:**
```
ERROR: Cannot connect to the Docker daemon at unix:///var/run/docker.sock
```

**Diagnosis:**
```bash
# Test Docker access as runner user
sudo -u gitlab-runner docker ps

# Check Docker socket permissions
ls -la /var/run/docker.sock
# Should be: srw-rw---- 1 root docker
```

**Fix:**
```bash
# Ensure user in docker group
sudo usermod -aG docker gitlab-runner

# Restart service
sudo systemctl restart gitlab-runner-myrunner.service

# If still failing, check Docker is running
sudo systemctl status docker
```

### "Docker Image Pull Failed"

**Error:**
```
ERROR: Failed to pull image "myimage:latest": error pulling image
```

**Diagnosis:**
```bash
# Test pull manually
docker pull myimage:latest

# Check network connectivity
curl -I https://registry-1.docker.io
```

**Common causes:**

#### 1. Private registry authentication

```yaml
# Add registry auth to playbook
gitlab_ci_runners_list:
  - name: "myrunner"
    docker_pull_policy: "if-not-present"
    environment:
      - "DOCKER_AUTH_CONFIG={\"auths\":{\"registry.company.com\":{\"auth\":\"base64token\"}}}"
```

#### 2. Network/firewall blocking registry

```bash
# Test registry connectivity
telnet registry-1.docker.io 443
```

**Fix:** Allow outbound HTTPS to Docker registries.

#### 3. Rate limiting (Docker Hub)

**Error:**
```
ERROR: toomanyrequests: You have reached your pull rate limit
```

**Fix:** Authenticate with Docker Hub:
```yaml
environment:
  - "DOCKER_AUTH_CONFIG={\"auths\":{\"https://index.docker.io/v1/\":{\"auth\":\"dXNlcjpwYXNz\"}}}"
```

### "Permission Denied" in Container

**Error:**
```
/bin/sh: can't create /workspace/file.txt: Permission denied
```

**Cause:** File ownership mismatch between host and container.

**Fix:**
```yaml
# Run container with same UID as runner user
- name: "myrunner"
  docker_user: "gitlab-runner:gitlab-runner"
```

---

## Performance Problems

### Slow Job Execution

**Diagnosis:**
```bash
# Check system resources
top
htop
vmstat 1

# Check Docker disk usage
docker system df

# Check concurrent jobs
cat /etc/gitlab-runner/myrunner/config.toml | grep concurrent
```

**Optimizations:**

#### 1. Increase concurrency (if resources available)

```yaml
- name: "myrunner"
  concurrent: 5  # Increase from default (1)
```

#### 2. Enable Docker layer caching

```yaml
- name: "myrunner"
  docker_volumes:
    - "/cache:/cache:rw"  # Persistent cache volume
```

#### 3. Use faster Docker storage driver

```yaml
environment:
  - "DOCKER_DRIVER=overlay2"  # Faster than vfs
```

### High Resource Usage

**Diagnosis:**
```bash
# Check per-container resources
docker stats

# Check runner processes
ps aux | grep gitlab-runner
```

**Fixes:**

#### 1. Limit concurrent jobs

```yaml
concurrent: 3  # Reduce if overwhelming system
```

#### 2. Set resource limits

```yaml
docker_cpus: "2.0"     # Max 2 CPUs per container
docker_memory: "2g"    # Max 2GB RAM per container
```

#### 3. Implement job queuing

```yaml
request_concurrency: 2  # Limit concurrent API requests
```

---

## Verification Commands

### Quick Health Check

```bash
#!/bin/bash
# check-runners.sh - Quick runner health check

echo "=== GitLab Runner Services ==="
systemctl list-units --type=service --state=running | grep gitlab-runner

echo ""
echo "=== Recent Errors (last hour) ==="
journalctl -u "gitlab-runner-*" -p err --since "1 hour ago" --no-pager

echo ""
echo "=== Runner Registration Status ==="
for config in /etc/gitlab-runner/*/config.toml; do
  runner_name=$(basename $(dirname "$config"))
  token=$(grep "token = " "$config" | cut -d'"' -f2)
  echo "Runner: $runner_name"
  echo "Token: ${token:0:20}..."
  echo ""
done

echo "=== Docker Status ==="
systemctl status docker --no-pager | head -n 5

echo ""
echo "=== Disk Usage ==="
df -h / | tail -n 1
docker system df
```

### Test API Connectivity

```bash
# Test GitLab API
curl -H "PRIVATE-TOKEN: YOUR_TOKEN" \
  https://gitlab.com/api/v4/version

# List all runners
curl -H "PRIVATE-TOKEN: YOUR_TOKEN" \
  https://gitlab.com/api/v4/runners | jq '.'

# Get specific runner
curl -H "PRIVATE-TOKEN: YOUR_TOKEN" \
  https://gitlab.com/api/v4/runners/RUNNER_ID | jq '.'
```

### Manual Runner Verification

```bash
# Verify runner configuration
sudo /usr/bin/gitlab-runner verify \
  --config /etc/gitlab-runner/myrunner/config.toml

# Test runner connectivity
sudo /usr/bin/gitlab-runner verify \
  --config /etc/gitlab-runner/myrunner/config.toml \
  --name myrunner
```

---

## Getting Help

### Collect Diagnostic Information

```bash
# System info
uname -a
cat /etc/os-release

# Runner version
gitlab-runner --version

# Service status
systemctl status gitlab-runner-myrunner.service

# Configuration (REDACT TOKENS!)
cat /etc/gitlab-runner/myrunner/config.toml | sed 's/token = .*/token = "REDACTED"/'

# Recent logs
journalctl -u gitlab-runner-myrunner.service -n 100 --no-pager
```

### Support Resources

- **GitLab Docs**: https://docs.gitlab.com/runner/
- **GitLab Forum**: https://forum.gitlab.com/
- **Role Issues**: https://github.com/kode3tech/ansible-col-devtools/issues

---

## Congratulations! 🎉

You've completed the GitLab CI Runners user guide!

### What You've Learned

- ✅ GitLab CI/CD concepts and architecture
- ✅ Runner types (Instance, Group, Project)
- ✅ Basic and advanced deployment
- ✅ Security best practices
- ✅ Production patterns
- ✅ Troubleshooting techniques

### Next Steps

- Deploy runners in your environment
- Explore [Role README](../../roles/gitlab_ci_runners/README.md) for API reference
- Check [Production Playbook](../../playbooks/gitlab_ci_runners/install-production.yml) for examples
- Review [FAQ](../FAQ.md) for common questions

---

[← Back to Guide Index](README.md)
