# APT Key Management - Modern Approach

## 📋 Overview

This document explains why and how we migrated from the deprecated `apt-key` command to the modern GPG key management approach in our Ansible roles.

## ❌ Old Method (Deprecated)

### What Was Used Before

```yaml
- name: Add Docker GPG apt key
  ansible.builtin.apt_key:
    url: "https://download.docker.com/linux/debian/gpg"
    state: present
```

### Problems with Old Method

1. **`apt-key` deprecated** in Debian 11 (Bullseye)
2. **`apt-key` removed** in Debian 12+ (Bookworm, Trixie)
3. **Security concerns**: Keys added globally affect all repositories
4. **No isolation**: All repositories trust the same keyring

### Error Example

```
TASK [Add Docker GPG apt key]
fatal: [debian13]: FAILED! => changed=false 
  msg: 'Failed to find required executable "apt-key" in paths: /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
```

## ✅ New Method (Modern & Secure)

### Current Implementation

```yaml
- name: Create keyrings directory
  ansible.builtin.file:
    path: /etc/apt/keyrings
    state: directory
    mode: '0755'

- name: Download Docker GPG key
  ansible.builtin.get_url:
    url: "https://download.docker.com/linux/debian/gpg"
    dest: /etc/apt/keyrings/docker.asc
    mode: '0644'
    force: false

- name: Add Docker repository
  ansible.builtin.apt_repository:
    repo: >-
      deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.asc]
      https://download.docker.com/linux/debian
      bookworm stable
```

### Advantages of New Method

1. ✅ **Works on all Debian/Ubuntu versions** (10, 11, 12, 13+)
2. ✅ **More secure**: Keys isolated per repository
3. ✅ **Official Debian standard** since Debian 11
4. ✅ **Future-proof**: Recommended approach going forward
5. ✅ **Explicit**: Clear which key signs which repository
6. ✅ **No deprecated commands**: Uses only supported tools

## 🔄 Compatibility Matrix

| Debian/Ubuntu Version | Old Method (apt-key) | New Method (keyrings) | Our Implementation |
|----------------------|---------------------|----------------------|-------------------|
| Debian 10 (Buster) | ✅ Works | ⚠️ Manual setup needed | ✅ **Works** (auto-creates dir) |
| Debian 11 (Bullseye) | ⚠️ Deprecated | ✅ Recommended | ✅ **Works** |
| Debian 12 (Bookworm) | ❌ Removed | ✅ Standard | ✅ **Works** |
| Debian 13 (Trixie) | ❌ Not available | ✅ Standard | ✅ **Works** |
| Ubuntu 20.04 (Focal) | ⚠️ Deprecated | ✅ Supported | ✅ **Works** |
| Ubuntu 22.04 (Jammy) | ❌ Removed | ✅ Standard | ✅ **Works** |
| Ubuntu 24.04 (Noble) | ❌ Not available | ✅ Standard | ✅ **Works** |

## 🎯 How It Works

### Step 1: Create Keyrings Directory

```yaml
- name: Create keyrings directory
  ansible.builtin.file:
    path: /etc/apt/keyrings
    state: directory
    mode: '0755'
```

**Why**: Ensures the directory exists on all systems, even older ones where it's not created by default.

### Step 2: Download GPG Key

```yaml
- name: Download Docker GPG key
  ansible.builtin.get_url:
    url: "{{ docker_apt_gpg_key }}"
    dest: /etc/apt/keyrings/docker.asc
    mode: '0644'
    force: false
```

**Key points**:
- Downloads key directly to the keyrings directory
- Uses `.asc` extension for ASCII-armored keys
- `force: false` prevents re-downloading on every run (idempotent)

### Step 3: Configure Repository with signed-by

```yaml
docker_apt_repository: >-
  deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.asc]
  https://download.docker.com/linux/debian
  bookworm stable
```

**Important**: The `signed-by=` option tells APT to use **only this specific key** to verify packages from this repository.

## 📚 Technical Details

### Directory Structure

```
/etc/apt/
├── keyrings/                    # Modern key storage (Debian 11+)
│   ├── docker.asc              # Docker GPG key
│   └── podman.asc              # Podman GPG key
├── sources.list.d/
│   ├── docker.list             # Docker repository
│   └── podman.list             # Podman repository
└── trusted.gpg.d/              # Legacy (deprecated, but still works)
```

### Key File Formats

- **ASCII-armored (`.asc`)**: Human-readable, starts with `-----BEGIN PGP PUBLIC KEY BLOCK-----`
- **Binary (`.gpg`)**: Binary format, more compact

Both formats work with the `signed-by=` option.

### APT Version Support

The `signed-by=` option requires:
- **APT >= 1.2** (Debian 9+, Ubuntu 16.04+)
- All target distributions in this collection meet this requirement

## 🔐 Security Improvements

### Old Method Security Issues

```bash
# Old way - adds key globally
apt-key add docker.gpg
# Now ALL repositories can use this key!
```

**Risk**: If a malicious repository is added, it could potentially use the Docker key to sign malicious packages.

### New Method Security Benefits

```bash
# New way - key scoped to specific repository
deb [signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/...
```

**Benefit**: Each repository has its own key. Even if a malicious repository is added, it can't use Docker's key.

## 🧪 Testing

### Verify Implementation

```bash
# 1. Check if keyrings directory exists
ls -la /etc/apt/keyrings/

# 2. Check if keys are present
ls -la /etc/apt/keyrings/*.asc

# 3. Check if repository is configured correctly
cat /etc/apt/sources.list.d/docker.list

# 4. Verify signed-by in repository config
grep "signed-by" /etc/apt/sources.list.d/docker.list

# 5. Test repository update
apt-get update
```

### Expected Output

```bash
$ cat /etc/apt/sources.list.d/docker.list
deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian bookworm stable
```

## 📖 References

- [Debian Wiki - SecureApt](https://wiki.debian.org/SecureApt)
- [Debian apt-key Deprecation Notice](https://manpages.debian.org/testing/apt/apt-key.8.en.html)
- [APT Sources Format](https://manpages.debian.org/testing/apt/sources.list.5.en.html)
- [Docker Official Installation Guide](https://docs.docker.com/engine/install/debian/)

## 🔄 Migration Guide

If you have playbooks using the old method:

### Before (Old)
```yaml
- name: Add Docker GPG apt key
  ansible.builtin.apt_key:
    url: "https://download.docker.com/linux/debian/gpg"
    state: present

- name: Add Docker repository
  ansible.builtin.apt_repository:
    repo: "deb [arch=amd64] https://download.docker.com/linux/debian {{ ansible_distribution_release }} stable"
```

### After (New)
```yaml
- name: Create keyrings directory
  ansible.builtin.file:
    path: /etc/apt/keyrings
    state: directory
    mode: '0755'

- name: Download Docker GPG key
  ansible.builtin.get_url:
    url: "https://download.docker.com/linux/debian/gpg"
    dest: /etc/apt/keyrings/docker.asc
    mode: '0644'
    force: false

- name: Add Docker repository
  ansible.builtin.apt_repository:
    repo: "deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian {{ ansible_distribution_release }} stable"
```

## ❓ FAQ

### Q: Will this work on older Debian/Ubuntu versions?
**A**: Yes! Our implementation creates the `/etc/apt/keyrings` directory if it doesn't exist, making it fully backward compatible with Debian 10+, Ubuntu 20.04+.

### Q: What if I already have keys in the old location?
**A**: The new method is independent. Old keys in `/etc/apt/trusted.gpg.d/` will continue to work but are no longer needed for repositories using `signed-by=`.

### Q: Do I need to remove old keys?
**A**: Not required, but recommended for cleanup:
```bash
rm -f /etc/apt/trusted.gpg.d/docker.gpg
```

### Q: Can I use `.gpg` instead of `.asc` files?
**A**: Yes! Both formats work. We use `.asc` (ASCII-armored) because it's more portable and easier to inspect.

### Q: What about Ubuntu PPAs?
**A**: Ubuntu PPAs still work with the old method, but it's recommended to migrate them too. The `signed-by=` approach works for PPAs as well.

## 🎉 Summary

Our implementation:
- ✅ Uses modern, secure GPG key management
- ✅ Compatible with Debian 10, 11, 12, 13+ and Ubuntu 20.04+
- ✅ More secure (key isolation per repository)
- ✅ Future-proof (follows current Debian standards)
- ✅ Idempotent and production-ready

---

**Updated**: November 2025  
**Authors**: Kode3Tech DevOps Team
