# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

The Code3Tech team takes security vulnerabilities seriously. We appreciate your efforts to responsibly disclose your findings.

### How to Report a Security Vulnerability?

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report security vulnerabilities by email to:

**suporte@kode3.tech**

Please include the following information:

- Type of vulnerability
- Full paths of source file(s) related to the manifestation of the vulnerability
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours
- **Communication**: We will send you regular updates about our progress
- **Timeline**: We aim to patch critical vulnerabilities within 7 days
- **Credit**: If you wish, we will publicly acknowledge your responsible disclosure

### Security Update Process

1. **Receive Report**: Security vulnerability reported via email
2. **Validate**: Confirm the vulnerability and assess its severity
3. **Develop Fix**: Create and test the security patch
4. **Release**: Deploy the security fix in a new version
5. **Announce**: Publish security advisory with details
6. **Credit**: Acknowledge the reporter (if desired)

## Security Best Practices

When using this collection, we recommend:

### General Security

- **Keep Updated**: Always use the latest version of the collection
- **Review Changes**: Review CHANGELOG.md for security-related updates
- **Principle of Least Privilege**: Run Ansible with minimum required privileges
- **Secure Storage**: Store sensitive data (passwords, keys) in Ansible Vault
- **Network Security**: Use SSH keys instead of passwords for authentication

### Docker/Podman Security

- **Rootless Mode**: Use rootless containers when possible
- **User Namespaces**: Configure user namespace remapping
- **Resource Limits**: Set appropriate resource limits for containers
- **Network Isolation**: Use network namespaces and proper firewall rules
- **Image Security**: Use trusted base images and scan for vulnerabilities

### Configuration Security

```yaml
# Example: Secure Docker configuration
docker_daemon_config:
  live-restore: true
  userland-proxy: false
  no-new-privileges: true
  userns-remap: default
```

```yaml
# Example: Secure Podman rootless configuration
podman_enable_rootless: true
podman_rootless_users:
  - "{{ ansible_user }}"
```

### Secrets Management

**Never commit secrets to git!**

Use Ansible Vault for sensitive data:

```bash
# Create encrypted file
ansible-vault create secrets.yml

# Edit encrypted file
ansible-vault edit secrets.yml

# Use in playbook
ansible-playbook playbook.yml --ask-vault-pass
```

## Known Security Considerations

### Docker

- **Docker Socket**: Mounting `/var/run/docker.sock` in containers gives root access
- **Privileged Containers**: Should be avoided in production
- **Network Exposure**: Be careful with port mappings

### Podman

- **Rootless Limitations**: Some features require root privileges
- **User Namespace**: Properly configure subuid/subgid ranges
- **SELinux**: Ensure proper SELinux context on RHEL-based systems

## Security Checklist

Before using this collection in production:

- [ ] Review all default variables in `defaults/main.yml`
- [ ] Configure firewall rules appropriately
- [ ] Enable rootless mode for containers (when possible)
- [ ] Use Ansible Vault for sensitive data
- [ ] Review and customize daemon configuration
- [ ] Implement proper backup procedures
- [ ] Set up monitoring and alerting
- [ ] Document your security configuration
- [ ] Test disaster recovery procedures
- [ ] Keep collection and dependencies updated

## Vulnerability Disclosure Policy

We follow a **90-day disclosure timeline**:

1. **Day 0**: Vulnerability reported
2. **Day 7**: Security patch released (for critical vulnerabilities)
3. **Day 30**: Security patch released (for medium/low vulnerabilities)
4. **Day 90**: Full public disclosure (if not patched earlier)

## Security Advisories

Security advisories are published at:
- GitHub Security Advisories: https://github.com/kode3tech/ansible-col-devtools/security/advisories
- Collection README.md
- CHANGELOG.md

## Contact

- **Security Email**: suporte@kode3.tech
- **General Issues**: https://github.com/kode3tech/ansible-col-devtools/issues
- **Website**: https://github.com/kode3tech

## Hall of Fame

We would like to thank the following individuals for responsibly disclosing security vulnerabilities:

<!-- List will be updated as vulnerabilities are reported and fixed -->
- *No vulnerabilities reported yet*

---

**Thank you for helping keep code3tech.devtools secure!** 🔒
