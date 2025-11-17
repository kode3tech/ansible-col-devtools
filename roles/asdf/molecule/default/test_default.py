"""
Molecule tests for asdf role.
"""
import os
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_asdf_directory_exists(host):
    """Test that asdf installation directory exists."""
    asdf_dir = host.file('/opt/asdf')
    assert asdf_dir.exists
    assert asdf_dir.is_directory


def test_asdf_executable_exists(host):
    """Test that asdf executable exists and is executable."""
    asdf_bin = host.file('/opt/asdf/bin/asdf')
    assert asdf_bin.exists
    assert asdf_bin.is_file
    assert asdf_bin.mode & 0o111  # Check executable bit


def test_asdf_version_command(host):
    """Test that asdf version command works."""
    cmd = host.run('/opt/asdf/bin/asdf --version')
    assert cmd.rc == 0
    assert 'v' in cmd.stdout or 'version' in cmd.stdout.lower()


def test_required_packages_installed(host):
    """Test that required system packages are installed."""
    required_packages = ['git', 'curl']
    for package in required_packages:
        pkg = host.package(package)
        assert pkg.is_installed


def test_asdf_git_repository(host):
    """Test that asdf was cloned from git repository."""
    git_dir = host.file('/opt/asdf/.git')
    assert git_dir.exists
    assert git_dir.is_directory
