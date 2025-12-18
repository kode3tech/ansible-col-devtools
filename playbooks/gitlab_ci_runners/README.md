# GitLab CI Runners Playbooks

Example playbooks for the `code3tech.devtools.gitlab_ci_runners` role.

## 🎯 Features Demonstrated

All playbooks showcase the latest features:

- ✅ **Multi-runner support** - N runners per host with isolated directories
- ✅ **Auto-create groups** - Automatically create GitLab groups via API
- ✅ **Tag management via API** - Dynamic tag updates without re-registration
- ✅ **Per-runner services** - Systemd template units (`gitlab-runner@{name}`)
- ✅ **Performance optimizations** - Concurrent jobs and request concurrency
- ✅ **Comprehensive verification** - Service, directory, and runner validation

## Vars Files

This directory includes a `vars/` folder with example configuration:

- `vars/gitlab_secrets.yml.example` - Example secrets file (copy/encrypt for real use)
- `vars/gitlab_runners.yml` - Runner configuration used by `install-production.yml`

These playbooks default to the API-based runner creation workflow (`gitlab_ci_runners_token_mode: auto`), which requires a GitLab PAT with `create_runner` scope.

To use Vault for secrets:

```bash
cp playbooks/gitlab_ci_runners/vars/gitlab_secrets.yml.example \
	playbooks/gitlab_ci_runners/vars/gitlab_secrets.yml

ansible-vault encrypt playbooks/gitlab_ci_runners/vars/gitlab_secrets.yml
```

## Playbooks

| Playbook | Description | Features |
|----------|-------------|----------|
| [install-production.yml](install-production.yml) | ⭐ **Production deployment** with all features | Multi-runner, auto-create group, tag management, verification |
| [install-multi-runner.yml](install-multi-runner.yml) | Deploy multiple runners per host | Multi-runner support with isolated directories |
| [install-with-proxy-ssl.yml](install-with-proxy-ssl.yml) | 🆕 **Corporate/Self-Managed setup** | Proxy and SSL/TLS configuration for GitLab Self-Managed |
| [install-single-runner.yml](install-single-runner.yml) | Basic single runner deployment | Simple installation example |

## Running

### Production Deployment (Recommended)

```bash
# Complete deployment with all features
ansible-playbook playbooks/gitlab_ci_runners/install-production.yml \
	-i inventory.ini \
	--ask-vault-pass
```

### Multi-Runner

```bash
# Deploy N runners on each host
ansible-playbook playbooks/gitlab_ci_runners/install-multi-runner.yml \
	-i inventory.ini \
	--ask-vault-pass
```

### With Proxy and SSL/TLS (Corporate/Self-Managed)

```bash
# For GitLab Self-Managed with proxy and custom CA certificate
ansible-playbook playbooks/gitlab_ci_runners/install-with-proxy-ssl.yml \
	-i inventory.ini \
	--ask-vault-pass
```

**Use cases:**
- Corporate environment with HTTP/HTTPS proxy
- GitLab Self-Managed with self-signed certificate
- GitLab Self-Managed with internal Certificate Authority

## Architecture

### Multi-Runner Structure

```
/opt/gitlab-ci-runners/
├── production-01/
│   ├── config.toml
│   ├── builds/
│   └── cache/
├── production-02/
│   ├── config.toml
│   ├── builds/
│   └── cache/
└── production-03/
    ├── config.toml
    ├── builds/
    └── cache/

Systemd services:
- gitlab-runner@production-01.service
- gitlab-runner@production-02.service
- gitlab-runner@production-03.service
```

### Service Management

```bash
# List all runner services
systemctl list-units 'gitlab-runner@*'

# Check specific runner
systemctl status gitlab-runner@production-01

# View logs
journalctl -u gitlab-runner@production-01 -f

# Restart runner
systemctl restart gitlab-runner@production-01
```

## Configuration Examples

### Minimal Configuration

```yaml
gitlab_ci_runners_gitlab_url: "https://gitlab.com"
gitlab_ci_runners_api_token: "{{ vault_gitlab_api_token }}"
gitlab_ci_runners_token_mode: "auto"
gitlab_ci_runners_api_runner_type: "group_type"
gitlab_ci_runners_api_group_full_path: "my-group"

gitlab_ci_runners_runners_list:
  - name: "runner-01"
    executor: "shell"
    tags: ["linux", "shell"]
```

### Full Production Configuration

```yaml
# Enable all features
gitlab_ci_runners_auto_create_group: true
gitlab_ci_runners_update_tags_via_api: true
gitlab_ci_runners_concurrent: 4
gitlab_ci_runners_request_concurrency: 2

# Multiple runners
gitlab_ci_runners_runners_list:
  - name: "production-01"
    executor: "shell"
    tags: ["production", "shell", "linux"]
    run_untagged: false
    
  - name: "production-02"
    executor: "shell"
    tags: ["production", "shell", "linux"]
    run_untagged: false
```

### With Proxy and SSL/TLS

```yaml
# Corporate proxy configuration
gitlab_ci_runners_proxy_url: "http://proxy.company.com:8080"
gitlab_ci_runners_no_proxy: "localhost,127.0.0.1,.internal.company.com"

# SSL/TLS for GitLab Self-Managed
gitlab_ci_runners_ssl_ca_cert: "/etc/ssl/certs/company-ca.crt"
gitlab_ci_runners_ssl_skip_cert_validation: false  # Keep true for security!

gitlab_ci_runners_runners_list:
  - name: "corporate-runner-01"
    executor: "shell"
    tags: ["corporate", "behind-proxy"]
```

## Verification

After deployment, verify:

1. **Services are running:**
   ```bash
   systemctl status gitlab-runner@production-01
   ```

2. **Runners are registered:**
   ```bash
   gitlab-runner list --config /opt/gitlab-ci-runners/production-01/config.toml
   ```

3. **Runners appear in GitLab UI:**
   - Navigate to: Group → Settings → CI/CD → Runners

4. **Test with a pipeline:**
   ```yaml
   # .gitlab-ci.yml
   test:
     tags:
       - production
     script:
       - echo "Testing runner"
   ```

## Troubleshooting

### Logs

```bash
# View runner logs
journalctl -u gitlab-runner@production-01 -f

# Check registration
gitlab-runner verify --config /opt/gitlab-ci-runners/production-01/config.toml
```

### Common Issues

**Runner not appearing in GitLab:**
- Check API token has `create_runner` scope
- Verify group path is correct
- Check runner is active: `systemctl status gitlab-runner@{name}`

**Permission errors:**
- Ensure runner user has correct permissions
- Check directory ownership: `/opt/gitlab-ci-runners/`

**Service won't start:**
- Check config file: `/opt/gitlab-ci-runners/{name}/config.toml`
- View service logs: `journalctl -u gitlab-runner@{name} -n 50`

## See Also

- [GitLab CI Runners Role README](../../roles/gitlab_ci_runners/README.md)
- [Complete User Guide](../../docs/user-guides/gitlab-ci-runners/)
- [Variables Reference](../../docs/reference/VARIABLES.md)

[← Back to Playbooks](../README.md)
