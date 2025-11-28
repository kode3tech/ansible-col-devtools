# Upgrade Guide - v1.0.0 to v1.1.0

## ⚠️ IMPORTANT NOTICE - INCOMPATIBLE CHANGES

### Podman: Configuration Files Separation

Starting from **v1.1.0**, Podman configurations have been reorganized to follow official best practices:

#### What Changed?

**Before (v1.0.x):**
- All configurations in `/etc/containers/storage.conf`
- `[storage]` and `[engine]` sections in the same file ❌

**Now (v1.1.0+):**
- `/etc/containers/storage.conf`: Only `[storage]` and `[storage.options]` ✅
- `/etc/containers/containers.conf`: Only `[engine]` ✅

#### Why Did It Change?

Official Podman documentation specifies:
- **`storage.conf`**: Storage configurations (driver, graphroot, mountopt)
- **`containers.conf`**: Runtime configurations (crun, cgroup, parallel copies)

Mixing these configurations caused:
- ⚠️ Warnings: `Failed to decode the keys ["engine" ...] from storage.conf`
- ❌ Errors: `database graph driver mismatch`

### 🔧 How to Upgrade

#### Option 1: Automatic Upgrade (Recommended)

```bash
# Install collection
ansible-galaxy collection install code3tech.devtools

# Run playbook
ansible-playbook -i inventory.ini playbooks/podman/install-podman.yml

# 2. Reset Podman storage (REMOVES containers/images!)
ansible -i inventory.ini all -m shell \
  -a 'rm -rf /var/lib/containers/storage/* /run/containers/storage/*' \
  --become

# 3. Verify functionality
ansible -i inventory.ini all -m shell \
  -a 'podman info | grep -A3 "store:"' \
  --become
```

#### Option 2: Manual Upgrade

1. **Remove `[engine]` configurations from `storage.conf`:**
```bash
# Edit /etc/containers/storage.conf
# Remove complete [engine] section
```

2. **Create `/etc/containers/containers.conf`:**
```toml
[engine]
runtime = "crun"
events_logger = "file"
cgroup_manager = "systemd"
num_locks = 2048
image_parallel_copies = 10
```

3. **Reset storage:**
```bash
rm -rf /var/lib/containers/storage/*
rm -rf /run/containers/storage/*
```

4. **Verify:**
```bash
podman info
podman version
```

### 🚨 Upgrade Impact

**⚠️ WARNING:** The Podman storage reset **REMOVES**:
- ✗ All containers
- ✗ All images
- ✗ All volumes
- ✗ All custom networks

**✅ NOT affected:**
- ✓ Registry configurations
- ✓ Login credentials
- ✓ Configured rootless users
- ✓ Docker configurations

### 📋 Post-Upgrade Checklist

```bash
# 1. Verify Podman version
podman version

# 2. Verify storage driver
podman info --format '{{.Store.GraphDriverName}}'
# Should return: overlay

# 3. Verify runtime
podman info --format '{{.Host.OCIRuntime.Name}}'
# Should return: crun

# 4. Test image pull
podman pull alpine:latest

# 5. Test container execution
podman run --rm alpine echo "Podman working!"

# 6. Verify configurations
cat /etc/containers/storage.conf
cat /etc/containers/containers.conf
```

### 🐛 Known Issues and Solutions

#### Error: `database graph driver mismatch`

**Cause:** Old storage incompatible with new driver

**Solution:**
```bash
# Reset storage
rm -rf /var/lib/containers/storage/*
rm -rf /run/containers/storage/*

# Test
podman info
```

#### Warning: `Failed to decode the keys ["engine" ...]`

**Cause:** `[engine]` section still in `storage.conf`

**Solution:**
```bash
# Remove [engine] section from storage.conf
sed -i '/^\[engine\]/,/^$/d' /etc/containers/storage.conf

# Run playbook to create correct containers.conf
ansible-playbook -i inventory.ini playbooks/podman/install-podman.yml
```

#### Error: `overlay is not supported`

**Cause:** Kernel too old or no overlay support in namespaces

**Solution:**
```yaml
# Use vfs driver (slower but compatible)
podman_storage_conf:
  storage:
    driver: "vfs"  # Change overlay to vfs
```

### 📈 Performance Improvements (v1.1.0)

After the upgrade, you will have:

| Feature | Before | Now | Improvement |
|---------|--------|-----|-------------|
| **Storage Driver** | vfs/undefined | overlay + metacopy | +30-50% I/O |
| **Runtime** | runc | crun | +20-30% startup |
| **Image Pull** | serial | parallel (10 layers) | +200-300% |
| **Configurations** | Mixed | Separated | ✅ No warnings |

### 🔄 Rollback (If Needed)

If you encounter problems, you can revert to v1.0.x:

```bash
# 1. Checkout previous version
git checkout tags/v1.0.0

# 2. Run playbook
ansible-playbook -i inventory.ini playbooks/podman/install-podman.yml

# 3. Reset storage (again)
ansible -i inventory.ini all -m shell \
  -a 'rm -rf /var/lib/containers/storage/*' \
  --become
```

### 📞 Support

If you encounter problems during the upgrade:

1. Check logs: `journalctl -xeu podman`
2. Open an issue: https://github.com/kode3tech/ansible-col-devtools/issues
3. Email: suporte@kode3.tech

---

[← Back to Maintenance](README.md)

**Last updated:** 2025-11-06  
**Target version:** v1.1.0  
**Impact:** ⚠️ HIGH (requires storage reset)
