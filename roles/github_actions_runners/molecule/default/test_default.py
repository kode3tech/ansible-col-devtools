"""
Molecule tests for github_actions_runners role using testinfra.

These tests verify the role's ability to:
- Create runner user and group
- Set up directory structure for multi-runner deployment
- Install prerequisite packages
- Configure proper file permissions
- Remove runners with state: absent
"""
import os
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


class TestGitHubActionsRunnersUser:
    """Test runner user and group configuration."""

    def test_runner_group_exists(self, host):
        """Verify the runner group exists."""
        group = host.group("ghrunner")
        assert group.exists, "Runner group 'ghrunner' should exist"

    def test_runner_user_exists(self, host):
        """Verify the runner user exists."""
        user = host.user("ghrunner")
        assert user.exists, "Runner user 'ghrunner' should exist"
        assert user.group == "ghrunner", "User should belong to 'ghrunner' group"

    def test_runner_user_home_directory(self, host):
        """Verify the runner user has correct home directory."""
        user = host.user("ghrunner")
        assert user.home == "/opt/github-actions-runners", \
            "Runner user home should be /opt/github-actions-runners"


class TestGitHubActionsRunnersDirectories:
    """Test directory structure for multi-runner deployment."""

    def test_base_directory_exists(self, host):
        """Verify the base directory for runners exists."""
        base_dir = host.file("/opt/github-actions-runners")
        assert base_dir.exists, "Base directory should exist"
        assert base_dir.is_directory, "Base path should be a directory"

    def test_base_directory_permissions(self, host):
        """Verify base directory has correct permissions."""
        base_dir = host.file("/opt/github-actions-runners")
        assert base_dir.user == "ghrunner", "Base dir should be owned by ghrunner"
        assert base_dir.group == "ghrunner", "Base dir group should be ghrunner"
        assert base_dir.mode == 0o755, "Base dir should have 755 permissions"

    @pytest.mark.parametrize("runner_name", [
        "test-runner-01",
        "test-runner-02",
        "test-runner-03",
    ])
    def test_runner_directories_exist(self, host, runner_name):
        """Verify each runner has its own directory."""
        runner_dir = host.file(f"/opt/github-actions-runners/{runner_name}")
        assert runner_dir.exists, f"Runner directory for {runner_name} should exist"
        assert runner_dir.is_directory, f"{runner_name} path should be a directory"

    @pytest.mark.parametrize("runner_name", [
        "test-runner-01",
        "test-runner-02",
        "test-runner-03",
    ])
    def test_runner_directories_permissions(self, host, runner_name):
        """Verify runner directories have correct permissions."""
        runner_dir = host.file(f"/opt/github-actions-runners/{runner_name}")
        assert runner_dir.user == "ghrunner", \
            f"{runner_name} dir should be owned by ghrunner"
        assert runner_dir.group == "ghrunner", \
            f"{runner_name} dir group should be ghrunner"


class TestGitHubActionsRunnersPrerequisites:
    """Test prerequisite packages installation."""

    @pytest.mark.parametrize("package_name", [
        "curl",
        "wget",
        "tar",
        "git",
    ])
    def test_prerequisite_packages_installed(self, host, package_name):
        """Verify prerequisite packages are installed."""
        package = host.package(package_name)
        assert package.is_installed, f"Package {package_name} should be installed"

    def test_curl_command_available(self, host):
        """Verify curl command is available."""
        cmd = host.run("curl --version")
        assert cmd.rc == 0, "curl command should be available"

    def test_wget_command_available(self, host):
        """Verify wget command is available."""
        cmd = host.run("wget --version")
        assert cmd.rc == 0, "wget command should be available"

    def test_tar_command_available(self, host):
        """Verify tar command is available."""
        cmd = host.run("tar --version")
        assert cmd.rc == 0, "tar command should be available"

    def test_git_command_available(self, host):
        """Verify git command is available."""
        cmd = host.run("git --version")
        assert cmd.rc == 0, "git command should be available"

    def test_jq_command_available(self, host):
        """Verify jq command is available."""
        cmd = host.run("jq --version")
        assert cmd.rc == 0, "jq command should be available"


class TestGitHubActionsRunnersMultiRunner:
    """Test multi-runner deployment structure."""

    def test_multiple_runner_directories_isolated(self, host):
        """Verify multiple runners have isolated directories."""
        runners = ["test-runner-01", "test-runner-02", "test-runner-03"]

        for runner in runners:
            runner_dir = host.file(f"/opt/github-actions-runners/{runner}")
            assert runner_dir.exists, f"Runner {runner} should have its own directory"
            assert runner_dir.is_directory, f"Runner {runner} path should be a directory"

    def test_runner_count(self, host):
        """Verify correct number of runner directories exist."""
        cmd = host.run("ls -d /opt/github-actions-runners/test-runner-* | wc -l")
        assert cmd.rc == 0, "Should be able to list runner directories"
        assert int(cmd.stdout.strip()) == 3, "Should have 3 test runner directories"


class TestGitHubActionsRunnersRemoval:
    """Test runner removal functionality (state: absent)."""

    def test_removed_runner_directory_not_exists(self, host):
        """Verify that the runner marked with state: absent was removed."""
        removed_runner_dir = host.file("/opt/github-actions-runners/test-runner-to-remove")
        assert not removed_runner_dir.exists, \
            "Runner 'test-runner-to-remove' directory should NOT exist after removal"

    def test_remaining_runners_still_exist(self, host):
        """Verify runners with state: present were NOT removed."""
        remaining_runners = ["test-runner-01", "test-runner-02", "test-runner-03"]

        for runner in remaining_runners:
            runner_dir = host.file(f"/opt/github-actions-runners/{runner}")
            assert runner_dir.exists, \
                f"Runner '{runner}' should still exist after removal test"


class TestGitHubActionsRunnersMockFiles:
    """Test mock files created for testing."""

    @pytest.mark.parametrize("runner_name", [
        "test-runner-01",
        "test-runner-02",
        "test-runner-03",
    ])
    def test_mock_config_script_exists(self, host, runner_name):
        """Verify mock config.sh exists for remaining runners."""
        config_script = host.file(f"/opt/github-actions-runners/{runner_name}/config.sh")
        assert config_script.exists, f"config.sh should exist for {runner_name}"
        assert config_script.mode == 0o755, f"config.sh should be executable for {runner_name}"

    @pytest.mark.parametrize("runner_name", [
        "test-runner-01",
        "test-runner-02",
        "test-runner-03",
    ])
    def test_mock_svc_script_exists(self, host, runner_name):
        """Verify mock svc.sh exists for remaining runners."""
        svc_script = host.file(f"/opt/github-actions-runners/{runner_name}/svc.sh")
        assert svc_script.exists, f"svc.sh should exist for {runner_name}"
        assert svc_script.mode == 0o755, f"svc.sh should be executable for {runner_name}"

    @pytest.mark.parametrize("runner_name", [
        "test-runner-01",
        "test-runner-02",
        "test-runner-03",
    ])
    def test_mock_runner_marker_exists(self, host, runner_name):
        """Verify .runner marker file exists for remaining runners."""
        runner_marker = host.file(f"/opt/github-actions-runners/{runner_name}/.runner")
        assert runner_marker.exists, f".runner should exist for {runner_name}"
