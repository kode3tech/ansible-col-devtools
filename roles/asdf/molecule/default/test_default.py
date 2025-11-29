"""
Molecule tests for asdf role (v2.0 - Centralized Architecture).
Tests the new group-based, centralized plugin management approach.
"""
import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_asdf_directory_exists(host):
    """Test that asdf installation directory exists with correct permissions."""
    asdf_dir = host.file('/opt/asdf')
    assert asdf_dir.exists
    assert asdf_dir.is_directory
    # Test group-based permissions (should be root:asdf or similar)
    assert asdf_dir.mode & 0o755  # At least 755 permissions


def test_asdf_executable_exists(host):
    """Test that asdf executable exists and is executable."""
    asdf_bin = host.file('/opt/asdf/bin/asdf')
    assert asdf_bin.exists
    assert asdf_bin.is_file
    assert asdf_bin.mode & 0o111  # Check executable bit


def test_asdf_version_command(host):
    """Test that asdf version command works."""
    cmd = host.run('/opt/asdf/bin/asdf version')
    assert cmd.rc == 0
    assert 'v0.' in cmd.stdout  # Should show version like 'v0.14.1'


def test_required_packages_installed(host):
    """Test that required system packages are installed."""
    required_packages = ['git', 'curl']
    for package in required_packages:
        pkg = host.package(package)
        assert pkg.is_installed


def test_asdf_group_exists(host):
    """Test that asdf group exists for shared access."""
    group = host.group('asdf')
    assert group.exists


def test_user_in_asdf_group(host):
    """Test that root user is added to asdf group."""
    user = host.user('root')
    assert 'asdf' in user.groups


def test_system_wide_path_configuration(host):
    """Test that system-wide PATH configuration exists."""
    profile_script = host.file('/etc/profile.d/asdf.sh')
    assert profile_script.exists
    assert profile_script.is_file
    assert profile_script.mode & 0o644  # Should be readable

    # Check content has correct PATH configuration
    content = profile_script.content_string
    assert 'export PATH="/opt/asdf/shims:$PATH"' in content
    assert 'ASDF_DATA_DIR="/opt/asdf"' in content


def test_direnv_plugin_installed(host):
    """Test that direnv plugin is installed centrally."""
    # Test plugin is listed
    cmd = host.run('ASDF_DATA_DIR=/opt/asdf /opt/asdf/bin/asdf plugin list')
    assert cmd.rc == 0
    assert 'direnv' in cmd.stdout


def test_direnv_version_installed(host):
    """Test that direnv version 2.32.3 is installed."""
    cmd = host.run('ASDF_DATA_DIR=/opt/asdf /opt/asdf/bin/asdf list direnv')
    assert cmd.rc == 0
    assert '2.32.3' in cmd.stdout


def test_direnv_global_version_set(host):
    """Test that direnv global version is set to 2.32.3."""
    cmd = host.run('ASDF_DATA_DIR=/opt/asdf /opt/asdf/bin/asdf current direnv')
    assert cmd.rc == 0
    assert '2.32.3' in cmd.stdout


def test_user_shell_configuration(host):
    """Test that user shell is configured with asdf."""
    bashrc = host.file('/root/.bashrc')
    assert bashrc.exists

    # Check for asdf configuration block
    content = bashrc.content_string
    assert 'ANSIBLE MANAGED BLOCK - asdf' in content
    assert 'export PATH="/opt/asdf/shims:$PATH"' in content


def test_asdf_shims_directory(host):
    """Test that shims directory exists and is functional."""
    shims_dir = host.file('/opt/asdf/shims')
    assert shims_dir.exists
    assert shims_dir.is_directory

    # Should have direnv shim
    direnv_shim = host.file('/opt/asdf/shims/direnv')
    assert direnv_shim.exists
    assert direnv_shim.is_file
    assert direnv_shim.mode & 0o111  # Should be executable


def test_centralized_data_directory(host):
    """Test that centralized data directory structure is correct."""
    # Main directories should exist
    essential_dirs = [
        '/opt/asdf/plugins',
        '/opt/asdf/installs',
        '/opt/asdf/shims'
    ]

    for directory in essential_dirs:
        dir_obj = host.file(directory)
        assert dir_obj.exists, f"Directory {directory} should exist"
        assert dir_obj.is_directory, f"{directory} should be a directory"


def test_asdf_binary_installation_method(host):
    """Test that asdf was installed via binary (not git clone)."""
    # Should NOT have .git directory (binary installation)
    git_dir = host.file('/opt/asdf/.git')
    assert not git_dir.exists, "Binary installation should not have .git directory"

    # Should have bin/asdf directly
    asdf_bin = host.file('/opt/asdf/bin/asdf')
    assert asdf_bin.exists
