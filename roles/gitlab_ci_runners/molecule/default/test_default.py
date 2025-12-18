"""Molecule tests for gitlab_ci_runners role."""

import os

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")


def test_gitlab_runner_package_installed(host):
    """Ensure gitlab-runner package is installed."""
    package = host.package("gitlab-runner")
    assert package.is_installed


def test_gitlab_runner_service_running(host):
    """Ensure gitlab-runner service is running and enabled."""
    service = host.service("gitlab-runner")
    assert service.is_running
    assert service.is_enabled


def test_gitlab_runner_binary_available(host):
    """Ensure gitlab-runner binary is available."""
    cmd = host.run("gitlab-runner --version")
    assert cmd.rc == 0
