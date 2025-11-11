# 🔧 Troubleshooting

Solutions to common issues when using the kode3tech.devtools collection.

## 📋 Available Guides

### [LXC Containers](TROUBLESHOOTING_LXC.md)
Running Docker and Podman inside LXC containers (Proxmox, LXD).
- **Applies to:** Both Docker and Podman roles
- AppArmor permission issues
- Network permission errors
- Performance considerations
- LXC configuration requirements

### [APT Key Deprecation](APT_KEY_DEPRECATION.md)
Modern GPG key management for Debian/Ubuntu.
- **Applies to:** Both Docker and Podman roles
- Migration from `apt_key` module
- Using `/etc/apt/keyrings/`
- Debian 12+ compatibility

### [Known Issues](KNOWN_ISSUES.md)
Common problems and their solutions.
- Platform-specific issues
- Version compatibility problems
- Known bugs and workarounds

---

## 🆘 Quick Help

### Docker Won't Start in LXC
→ See [LXC Containers - Docker Issues](TROUBLESHOOTING_LXC.md#docker-issues)

### Podman DNS Errors
→ See [Known Issues - Podman DNS](KNOWN_ISSUES.md#podman-dns-permission-issue)

### APT Key Warnings
→ See [APT Key Deprecation](APT_KEY_DEPRECATION.md)

---

## 🔍 Still Need Help?

1. Check [Known Issues](KNOWN_ISSUES.md)
2. Search [GitHub Issues](https://github.com/kode3tech/ansible-devtools/issues)
3. Create a new issue with details
4. Email: devops@kode3.com.br

---

[← Back to Documentation Index](../README.md)
