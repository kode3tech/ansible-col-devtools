"""
Molecule tests for azure_devops_agents role using testinfra.

These tests verify the role's ability to:
- Create agent user and group
- Set up directory structure for multi-agent deployment
- Install prerequisite packages
- Configure proper file permissions
- Remove agents with state: absent
"""
import os
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


class TestAzureDevOpsAgentsUser:
    """Test agent user and group configuration."""

    def test_agent_group_exists(self, host):
        """Verify the agent group exists."""
        group = host.group("azagent")
        assert group.exists, "Agent group 'azagent' should exist"

    def test_agent_user_exists(self, host):
        """Verify the agent user exists."""
        user = host.user("azagent")
        assert user.exists, "Agent user 'azagent' should exist"
        assert user.group == "azagent", "User should belong to 'azagent' group"

    def test_agent_user_home_directory(self, host):
        """Verify the agent user has correct home directory."""
        user = host.user("azagent")
        assert user.home == "/opt/azure-devops-agents", \
            "Agent user home should be /opt/azure-devops-agents"


class TestAzureDevOpsAgentsDirectories:
    """Test directory structure for multi-agent deployment."""

    def test_base_directory_exists(self, host):
        """Verify the base directory for agents exists."""
        base_dir = host.file("/opt/azure-devops-agents")
        assert base_dir.exists, "Base directory should exist"
        assert base_dir.is_directory, "Base path should be a directory"

    def test_base_directory_permissions(self, host):
        """Verify base directory has correct permissions."""
        base_dir = host.file("/opt/azure-devops-agents")
        assert base_dir.user == "azagent", "Base dir should be owned by azagent"
        assert base_dir.group == "azagent", "Base dir group should be azagent"
        assert base_dir.mode == 0o755, "Base dir should have 755 permissions"

    @pytest.mark.parametrize("agent_name", [
        "test-agent-01",
        "test-agent-02",
        "test-agent-03",
    ])
    def test_agent_directories_exist(self, host, agent_name):
        """Verify each agent has its own directory."""
        agent_dir = host.file(f"/opt/azure-devops-agents/{agent_name}")
        assert agent_dir.exists, f"Agent directory for {agent_name} should exist"
        assert agent_dir.is_directory, f"{agent_name} path should be a directory"

    @pytest.mark.parametrize("agent_name", [
        "test-agent-01",
        "test-agent-02",
        "test-agent-03",
    ])
    def test_agent_directories_permissions(self, host, agent_name):
        """Verify agent directories have correct permissions."""
        agent_dir = host.file(f"/opt/azure-devops-agents/{agent_name}")
        assert agent_dir.user == "azagent", \
            f"{agent_name} dir should be owned by azagent"
        assert agent_dir.group == "azagent", \
            f"{agent_name} dir group should be azagent"


class TestAzureDevOpsAgentsPrerequisites:
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


class TestAzureDevOpsAgentsMultiAgent:
    """Test multi-agent deployment structure."""

    def test_multiple_agent_directories_isolated(self, host):
        """Verify multiple agents have isolated directories."""
        agents = ["test-agent-01", "test-agent-02", "test-agent-03"]

        for agent in agents:
            agent_dir = host.file(f"/opt/azure-devops-agents/{agent}")
            assert agent_dir.exists, f"Agent {agent} should have its own directory"
            assert agent_dir.is_directory, f"Agent {agent} path should be a directory"

    def test_agent_count(self, host):
        """Verify correct number of agent directories exist."""
        cmd = host.run("ls -d /opt/azure-devops-agents/test-agent-* | wc -l")
        assert cmd.rc == 0, "Should be able to list agent directories"
        assert int(cmd.stdout.strip()) == 3, "Should have 3 test agent directories"


class TestAzureDevOpsAgentsRemoval:
    """Test agent removal functionality (state: absent)."""

    def test_removed_agent_directory_not_exists(self, host):
        """Verify that the agent marked with state: absent was removed."""
        removed_agent_dir = host.file("/opt/azure-devops-agents/test-agent-to-remove")
        assert not removed_agent_dir.exists, \
            "Agent 'test-agent-to-remove' directory should NOT exist after removal"

    def test_remaining_agents_still_exist(self, host):
        """Verify agents with state: present were NOT removed."""
        remaining_agents = ["test-agent-01", "test-agent-02", "test-agent-03"]

        for agent in remaining_agents:
            agent_dir = host.file(f"/opt/azure-devops-agents/{agent}")
            assert agent_dir.exists, \
                f"Agent {agent} should still exist (state: present)"

    def test_mock_config_script_exists_for_remaining(self, host):
        """Verify mock config.sh exists for remaining agents."""
        remaining_agents = ["test-agent-01", "test-agent-02", "test-agent-03"]

        for agent in remaining_agents:
            config_script = host.file(f"/opt/azure-devops-agents/{agent}/config.sh")
            assert config_script.exists, \
                f"config.sh should exist for {agent}"
            assert config_script.mode == 0o755, \
                f"config.sh should be executable for {agent}"


class TestAzureDevOpsAgentsSystemd:
    """Test systemd-related configurations."""

    def test_systemd_directory_exists(self, host):
        """Verify systemd service directory exists."""
        systemd_dir = host.file("/etc/systemd/system")
        assert systemd_dir.exists, "Systemd service directory should exist"
        assert systemd_dir.is_directory, "Systemd path should be a directory"

    def test_systemctl_available(self, host):
        """Verify systemctl command is available."""
        cmd = host.run("which systemctl")
        assert cmd.rc == 0, "systemctl should be available"
