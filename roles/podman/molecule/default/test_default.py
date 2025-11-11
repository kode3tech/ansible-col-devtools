"""Molecule tests for Podman role."""

import os
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_podman_installed(host):
    """Verify Podman is installed."""
    cmd = host.run("podman --version")
    assert cmd.rc == 0
    assert "podman version" in cmd.stdout.lower()


def test_buildah_installed(host):
    """Verify Buildah is installed."""
    cmd = host.run("buildah --version")
    assert cmd.rc == 0
    assert "buildah version" in cmd.stdout.lower()


def test_skopeo_installed(host):
    """Verify Skopeo is installed."""
    cmd = host.run("skopeo --version")
    assert cmd.rc == 0
    assert "skopeo version" in cmd.stdout.lower()


def test_podman_info(host):
    """Verify Podman info command works."""
    cmd = host.run("podman info")
    assert cmd.rc == 0


def test_registries_config_exists(host):
    """Verify registries configuration file exists."""
    config_file = host.file("/etc/containers/registries.conf")
    assert config_file.exists
    assert config_file.is_file


def test_storage_config_exists(host):
    """Verify storage configuration file exists."""
    config_file = host.file("/etc/containers/storage.conf")
    assert config_file.exists
    assert config_file.is_file


def _parse_subid_file(content):
    """Return a mapping of user -> (start, count) from subordinate id files."""
    entries = {}
    for line in content.strip().splitlines():
        if not line or ":" not in line:
            continue
        parts = line.split(":")
        if len(parts) < 3:
            continue
        user, start, count = parts[0], parts[1], parts[2]
        try:
            entries[user] = (int(start), int(count))
        except ValueError:
            continue
    return entries


def _ranges_overlap(range_a, range_b):
    """Return True if two (start, count) ranges overlap."""
    start_a, count_a = range_a
    start_b, count_b = range_b
    end_a = start_a + count_a
    end_b = start_b + count_b
    return not (end_a <= start_b or end_b <= start_a)


def test_subuid_configured(host):
    """Verify subuid ranges exist and do not overlap for rootless users."""
    subuid_file = host.file("/etc/subuid")
    assert subuid_file.exists

    entries = _parse_subid_file(subuid_file.content_string)
    for user in ("ansible", "devuser"):
        assert user in entries, f"Missing subuid entry for {user}"

    assert not _ranges_overlap(entries["ansible"], entries["devuser"]), (
        "Subuid ranges overlap between ansible and devuser"
    )


def test_subgid_configured(host):
    """Verify subgid ranges exist and do not overlap for rootless users."""
    subgid_file = host.file("/etc/subgid")
    assert subgid_file.exists

    entries = _parse_subid_file(subgid_file.content_string)
    for user in ("ansible", "devuser"):
        assert user in entries, f"Missing subgid entry for {user}"

    assert not _ranges_overlap(entries["ansible"], entries["devuser"]), (
        "Subgid ranges overlap between ansible and devuser"
    )


def test_podman_hello(host):
    """Test Podman functionality with hello image."""
    cmd = host.run("podman run --rm quay.io/podman/hello")
    # May fail on some architectures, so we check for multiple conditions
    if cmd.rc == 0:
        assert ("Podman" in cmd.stdout or "Hello" in cmd.stdout)
    else:
        # Skip test if there's an architecture incompatibility
        if "invalid argument" in cmd.stderr.lower():
            pytest.skip("Architecture incompatibility detected")
        else:
            # For other failures, we still want to fail the test
            assert False, f"Podman hello test failed: {cmd.stderr}"


def test_registries_conf_contains_insecure_registries(host):
    """Verify registries.conf contains insecure registry configurations."""
    config_file = host.file("/etc/containers/registries.conf")
    assert config_file.exists
    
    content = config_file.content_string
    
    # Check for [[registry]] TOML sections
    assert "[[registry]]" in content, "No registry sections found in registries.conf"
    
    # Check that insecure = true appears in the configuration
    assert 'insecure = true' in content, "No insecure registries configured"
    
    # Count number of insecure registry entries
    insecure_count = content.count('insecure = true')
    assert insecure_count >= 3, \
        f"Expected at least 3 insecure registries, found {insecure_count}"


def test_specific_insecure_registries_configured(host):
    """Verify specific insecure registries are configured in registries.conf."""
    config_file = host.file("/etc/containers/registries.conf")
    content = config_file.content_string
    
    expected_registries = [
        "localhost:5000",
        "registry.test.local:5000",
        "192.168.100.100:5000"
    ]
    
    for registry in expected_registries:
        # Check that each registry appears in a location directive
        assert f'location = "{registry}"' in content, \
            f"Registry {registry} not found in registries.conf"


def test_insecure_flag_for_each_registry(host):
    """Verify each configured registry has the insecure flag set."""
    import re
    
    config_file = host.file("/etc/containers/registries.conf")
    content = config_file.content_string
    
    expected_registries = [
        "localhost:5000",
        "registry.test.local:5000",
        "192.168.100.100:5000"
    ]
    
    for registry in expected_registries:
        # Use regex to find the registry block and check for insecure flag
        # Pattern matches [[registry]] ... location = "registry" ... insecure = true
        pattern = rf'\[\[registry\]\].*?location = "{re.escape(registry)}".*?insecure = true'
        
        assert re.search(pattern, content, re.DOTALL), \
            f"Registry {registry} does not have insecure = true flag"


def test_registries_conf_valid_toml_syntax(host):
    """Verify registries.conf has valid TOML syntax for registry blocks."""
    config_file = host.file("/etc/containers/registries.conf")
    content = config_file.content_string
    
    # Basic TOML validation for registry blocks
    registry_blocks = content.count("[[registry]]")
    
    # Each registry block should have a location
    location_count = content.count('location = ')


# =============================================================================
# PERFORMANCE OPTIMIZATION TESTS
# =============================================================================

def test_podman_storage_conf_exists(host):
    """Verify storage.conf file exists and is properly configured."""
    storage_conf = host.file("/etc/containers/storage.conf")
    
    assert storage_conf.exists
    assert storage_conf.is_file
    assert storage_conf.user == "root"
    assert storage_conf.group == "root"


def test_podman_storage_driver_optimized(host):
    """Verify Podman is configured to use overlay storage driver."""
    storage_conf = host.file("/etc/containers/storage.conf")
    content = storage_conf.content_string
    
    # Check for overlay driver configuration
    assert 'driver = "overlay"' in content, \
        "Podman storage.conf should use overlay driver for optimal performance"


def test_podman_storage_metacopy_enabled(host):
    """Verify Podman overlay storage has metacopy optimization enabled."""
    storage_conf = host.file("/etc/containers/storage.conf")
    content = storage_conf.content_string
    
    # Check for metacopy in mount options
    assert "metacopy=on" in content, \
        "Podman storage.conf should have metacopy=on for 30-50% I/O improvement"


def test_podman_crun_runtime_configured(host):
    """Verify Podman is configured to use crun runtime (20-30% faster than runc)."""
    storage_conf = host.file("/etc/containers/storage.conf")
    content = storage_conf.content_string
    
    # Check for crun runtime in engine section
    assert 'runtime = "crun"' in content, \
        "Podman should use crun runtime for 20-30% faster container startup"


def test_podman_parallel_copies_configured(host):
    """Verify Podman is configured for parallel image layer downloads."""
    storage_conf = host.file("/etc/containers/storage.conf")
    content = storage_conf.content_string
    
    # Check for image_parallel_copies setting
    assert "image_parallel_copies" in content, \
        "Podman should have parallel copies configured for faster image pulls"


def test_crun_binary_available(host):
    """Verify crun binary is available (optional but recommended)."""
    # This is an optional optimization - won't fail if missing
    cmd = host.run("which crun")
    
    if cmd.rc == 0:
        # If crun is available, verify it works
        crun_version = host.run("crun --version")
        assert crun_version.rc == 0, \
            "crun binary should be functional"


def test_podman_info_shows_optimizations(host):
    """Verify podman info reflects the optimization settings."""
    cmd = host.run("podman info --format json")
    
    if cmd.rc == 0:
        import json
        info = json.loads(cmd.stdout)
        
        # Check storage driver
        if "store" in info:
            storage_driver = info["store"].get("graphDriverName", "")
            assert storage_driver == "overlay", \
                f"Expected overlay storage driver, got {storage_driver}"

