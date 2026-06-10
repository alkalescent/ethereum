"""Tests for Environment classes."""

from staker.environment import AWSEnvironment, LocalEnvironment


class TestAWSEnvironment:
    """Tests for AWSEnvironment."""

    def test_logs_path(self):
        env = AWSEnvironment()
        assert env.get_logs_path() == "/mnt/ebs/logs.txt"

    def test_data_prefix(self):
        env = AWSEnvironment()
        assert env.get_data_prefix() == "/mnt/ebs"

    def test_p2p_host_dns_dev(self):
        env = AWSEnvironment()
        assert env.get_p2p_host_dns(is_dev=True) is None

    def test_p2p_host_dns_prod(self):
        env = AWSEnvironment()
        assert env.get_p2p_host_dns(is_dev=False) is None

    def test_no_colored_logs(self):
        env = AWSEnvironment()
        assert env.use_colored_logs() is False

    def test_manages_snapshots(self):
        env = AWSEnvironment()
        assert env.should_manage_snapshots() is True


class TestLocalEnvironment:
    """Tests for LocalEnvironment."""

    def test_logs_path(self):
        env = LocalEnvironment()
        assert env.get_logs_path() == "/mnt/ebs/ethereum/logs.txt"

    def test_data_prefix_is_home(self):
        env = LocalEnvironment()
        assert env.get_data_prefix() == "/mnt/ebs"

    def test_no_p2p_host_dns(self):
        env = LocalEnvironment()
        assert env.get_p2p_host_dns(is_dev=True) is None
        assert env.get_p2p_host_dns(is_dev=False) is None

    def test_uses_colored_logs(self):
        env = LocalEnvironment()
        assert env.use_colored_logs() is True

    def test_no_snapshot_management(self):
        env = LocalEnvironment()
        assert env.should_manage_snapshots() is False


class TestGetEnvironment:
    """Tests for the get_environment factory function."""

    def test_returns_local_when_not_aws(self, mocker):
        """Test factory returns LocalEnvironment when AWS is False."""
        from staker.environment import LocalEnvironment, get_environment

        mocker.patch("staker.config.AWS", False)
        env = get_environment()
        assert isinstance(env, LocalEnvironment)

    def test_returns_aws_when_aws(self, mocker):
        """Test factory returns AWSEnvironment when AWS is True."""
        from staker.environment import AWSEnvironment, get_environment

        mocker.patch("staker.config.AWS", True)
        env = get_environment()
        assert isinstance(env, AWSEnvironment)
