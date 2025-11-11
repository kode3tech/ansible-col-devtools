# Molecule Testing Quick Reference

## 🚀 Quick Commands

### Docker Role Tests
```bash
# Full test cycle (destroy → create → converge → verify → destroy)
cd roles/docker && molecule test

# Quick converge (apply role)
cd roles/docker && molecule converge

# Run verification only
cd roles/docker && molecule verify

# Login to test instance
cd roles/docker && molecule login

# Cleanup
cd roles/docker && molecule destroy
```

### Podman Role Tests
```bash
# Full test cycle
cd roles/podman && molecule test

# Quick converge
cd roles/podman && molecule converge

# Run verification only
cd roles/podman && molecule verify

# Login to test instance
cd roles/podman && molecule login

# Cleanup
cd roles/podman && molecule destroy
```

### Both Roles (from project root)
```bash
# Using Makefile
make test-docker
make test-podman
make test-all

# Direct commands
for role in docker podman; do
    cd roles/$role && molecule test && cd ../..
done
```

---

## 🔍 What Gets Tested

### Insecure Registries - Docker
✅ `/etc/docker/daemon.json` exists  
✅ Valid JSON syntax  
✅ Contains `insecure-registries` key  
✅ Has 3 test registries:
- `localhost:5000`
- `registry.test.local:5000`
- `192.168.100.100:5000`

### Insecure Registries - Podman
✅ `/etc/containers/registries.conf` exists  
✅ Valid TOML syntax  
✅ Contains `[[registry]]` blocks  
✅ Each registry has `insecure = true`  
✅ Has 3 test registries configured  

---

## 📊 Test Phases

1. **Dependency** - Install Ansible dependencies
2. **Lint** - Check syntax (optional, can be skipped)
3. **Cleanup** - Destroy existing test instances
4. **Destroy** - Remove containers
5. **Syntax** - Validate playbook syntax
6. **Create** - Launch test containers (Ubuntu, Debian, Rocky)
7. **Prepare** - Pre-test setup (if prepare.yml exists)
8. **Converge** - Apply the role
9. **Idempotence** - Verify role is idempotent
10. **Verify** - Run verification tasks and pytest tests
11. **Cleanup** - Final cleanup
12. **Destroy** - Remove test instances

---

## 🐛 Common Issues & Solutions

### Issue: "Molecule not found"
```bash
# Activate venv first
source .venv/bin/activate
# Or
source activate.sh
```

### Issue: "Docker socket permission denied"
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Issue: "Port already in use"
```bash
# Destroy existing instances
molecule destroy
# Or force cleanup
docker ps -a | grep molecule | awk '{print $1}' | xargs docker rm -f
```

### Issue: "Platform not found"
```bash
# Pull Docker images manually
docker pull geerlingguy/docker-ubuntu2204-ansible:latest
docker pull geerlingguy/docker-debian12-ansible:latest
docker pull geerlingguy/docker-rockylinux9-ansible:latest
```

### Issue: Test fails with "invalid argument"
```
This is expected on some architectures (ARM/x86 emulation).
The test is configured to skip in this case.
Docker/Podman installation is still valid.
```

---

## 🎯 Selective Testing

### Test Specific Platform
```bash
cd roles/docker

# Test only Ubuntu
MOLECULE_DISTRO=ubuntu2204 molecule test

# Test only Debian
MOLECULE_DISTRO=debian12 molecule test

# Test only Rocky Linux
MOLECULE_DISTRO=rockylinux9 molecule test
```

### Run Only Pytest Tests
```bash
cd roles/docker/molecule/default
pytest test_default.py -v

# Or specific test
pytest test_default.py::test_docker_daemon_json_contains_insecure_registries -v
```

### Run Only Ansible Verify
```bash
cd roles/docker
molecule converge  # Apply role first
molecule verify    # Run verify.yml
```

---

## 📈 Expected Output

### Successful Test Run
```
PLAY RECAP *********************************************************************
instance                   : ok=25   changed=3    unreachable=0    failed=0

--> Scenario: 'default'
--> Action: 'verify'
--> Running Ansible Verifier

PLAY [Verify] ******************************************************************

TASK [Verify insecure-registries is configured] *******************************
ok: [instance] => {
    "msg": "insecure-registries configured correctly"
}

--> Scenario: 'default'
--> Action: 'idempotence'
--> Running default playbook

PLAY RECAP *********************************************************************
instance                   : ok=25   changed=0    unreachable=0    failed=0

--> Scenario: 'default'
--> Action: 'verify'

============================= test session starts ==============================
collected 10 items

test_default.py::test_docker_is_installed PASSED                        [ 10%]
test_default.py::test_docker_service_running PASSED                     [ 20%]
test_default.py::test_docker_daemon_json_contains_insecure_registries PASSED [ 90%]
test_default.py::test_docker_daemon_json_valid_format PASSED           [100%]

============================== 10 passed in 12.34s ==============================
```

### Failed Test Example
```
TASK [Verify insecure-registries is configured] *******************************
fatal: [instance]: FAILED! => {
    "assertion": "'insecure-registries' in daemon_config",
    "failed": true,
    "msg": "insecure-registries not configured in daemon.json"
}
```

---

## 🔧 Debug Mode

### Enable Verbose Output
```bash
# Ansible verbose
molecule --debug test

# More verbosity
molecule test -- -vvv

# Pytest verbose
cd roles/docker/molecule/default
pytest test_default.py -vvs
```

### Manual Verification
```bash
# Login to instance
molecule login

# Check Docker config
cat /etc/docker/daemon.json | jq .

# Check Podman config
cat /etc/containers/registries.conf

# Test registry connectivity (if registry is running)
docker pull localhost:5000/test-image
podman pull localhost:5000/test-image

# Exit instance
exit
```

---

## 📝 Test Development Workflow

1. **Modify role**:
   ```bash
   vim roles/docker/tasks/main.yml
   ```

2. **Converge (apply changes)**:
   ```bash
   cd roles/docker
   molecule converge
   ```

3. **Verify manually** (optional):
   ```bash
   molecule login
   cat /etc/docker/daemon.json
   exit
   ```

4. **Update tests**:
   ```bash
   vim molecule/default/verify.yml
   vim molecule/default/test_default.py
   ```

5. **Run verification**:
   ```bash
   molecule verify
   ```

6. **Full test cycle**:
   ```bash
   molecule test
   ```

7. **Cleanup**:
   ```bash
   molecule destroy
   ```

---

## 🎓 Useful Tips

1. **Keep instances running** for faster iterations:
   ```bash
   molecule converge  # Instead of molecule test
   molecule verify
   # Make changes
   molecule converge
   molecule verify
   # When done
   molecule destroy
   ```

2. **Skip linting** for faster tests:
   ```bash
   molecule test --destroy=never
   ```

3. **Test only changed files**:
   ```bash
   # If only tasks changed, no need for full test
   molecule converge
   molecule verify
   ```

4. **Use check mode** for dry runs:
   ```bash
   molecule converge -- --check
   ```

5. **Parallel testing** (from project root):
   ```bash
   (cd roles/docker && molecule test) &
   (cd roles/podman && molecule test) &
   wait
   ```

---

## 📊 CI/CD Integration

### GitHub Actions Example
```yaml
name: Molecule Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        role: [docker, podman]
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          ansible-galaxy collection install -r requirements.yml
      
      - name: Run Molecule tests
        run: |
          cd roles/${{ matrix.role }}
          molecule test
```

---

## 📚 Additional Resources

- [Molecule Documentation](https://molecule.readthedocs.io/)
- [Testinfra Documentation](https://testinfra.readthedocs.io/)
- [TESTING.md](./TESTING.md) - Detailed testing guide
- [MOLECULE_TESTS_UPDATE.md](./MOLECULE_TESTS_UPDATE.md) - Test update documentation

---

## 🎯 Test Matrix

| Role | Platform | Python | Ansible | Status |
|------|----------|--------|---------|--------|
| Docker | Ubuntu 22.04 | 3.11 | 2.15+ | ✅ |
| Docker | Debian 12 | 3.11 | 2.15+ | ✅ |
| Docker | Rocky 9 | 3.9 | 2.15+ | ✅ |
| Podman | Ubuntu 22.04 | 3.11 | 2.15+ | ✅ |
| Podman | Debian 12 | 3.11 | 2.15+ | ✅ |
| Podman | Rocky 9 | 3.9 | 2.15+ | ✅ |

---

**Last Updated**: 2024  
**Maintainer**: Kode3Tech DevOps Team
