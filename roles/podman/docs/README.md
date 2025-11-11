# 📚 Podman Role - Additional Documentation

Additional documentation specific to the Podman role.

> **Main Documentation:** See [Podman Role README](../README.md) for complete role documentation.

## 📋 Available Documents

### [Podman XDG Runtime Fix](PODMAN_XDG_RUNTIME_FIX.md)
Comprehensive guide to fixing XDG_RUNTIME_DIR issues in Podman.
- **Problem:** `XDG_RUNTIME_DIR not found` errors
- **Solution:** systemd-tmpfiles configuration
- **Applies to:** Both root and rootless Podman
- **Status:** Implemented in role by default

---

## 🔍 When to Use These Docs

### You Need Podman XDG Runtime Fix If:
- You see "XDG_RUNTIME_DIR does not exist" warnings
- Registry authentication fails for root
- Podman commands fail with XDG-related errors

→ See [PODMAN_XDG_RUNTIME_FIX.md](PODMAN_XDG_RUNTIME_FIX.md)

---

## 📚 Related Documentation

### Role Documentation
- [Podman Role README](../README.md) - Main role documentation
- [Role Variables](../defaults/main.yml) - All available variables
- [Role Tasks](../tasks/main.yml) - Task implementation

### Collection Documentation
- [Registry Authentication](../../docs/user-guides/REGISTRY_AUTHENTICATION.md) - Docker & Podman registry auth
- [LXC Troubleshooting](../../docs/troubleshooting/TROUBLESHOOTING_LXC.md) - Podman in LXC containers
- [Known Issues](../../docs/troubleshooting/KNOWN_ISSUES.md) - Common Podman issues

---

[← Back to Podman Role](../README.md) | [← Back to Collection Docs](../../docs/README.md)
