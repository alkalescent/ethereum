import os
from abc import ABC, abstractmethod


class Environment(ABC):
    """
    Abstract base class for runtime environment configuration.

    This abstracts the differences between running on AWS (container)
    vs locally, separate from network choice (dev/prod).
    """

    @abstractmethod
    def get_logs_path(self) -> str:
        """Path to the logs file."""
        ...

    @abstractmethod
    def get_data_prefix(self) -> str:
        """Base directory for data (geth, prysm data dirs)."""
        ...

    @abstractmethod
    def get_p2p_host_dns(self, is_dev: bool) -> str | None:
        """P2P host DNS for beacon chain, or None if not applicable."""
        ...

    @abstractmethod
    def use_colored_logs(self) -> bool:
        """Whether to use colored console output."""
        ...

    @abstractmethod
    def should_manage_snapshots(self) -> bool:
        """Whether to manage EBS snapshots."""
        ...


class AWSEnvironment(Environment):
    """Runtime environment for AWS ECS containers."""

    def get_logs_path(self) -> str:
        return "/mnt/ebs/logs.txt"

    def get_data_prefix(self) -> str:
        return "/mnt/ebs"

    def get_p2p_host_dns(self, is_dev: bool) -> str:
        return f"aws.{'dev.' if is_dev else ''}eth.forcepu.sh"

    def use_colored_logs(self) -> bool:
        return False

    def should_manage_snapshots(self) -> bool:
        return True


class LocalEnvironment(Environment):
    """Runtime environment for local development."""

    def get_logs_path(self) -> str:
        return "/mnt/ebs/ethereum/logs.txt"

    def get_data_prefix(self) -> str:
        return os.path.expanduser("~")

    def get_p2p_host_dns(self, is_dev: bool) -> str | None:
        return None

    def use_colored_logs(self) -> bool:
        return True

    def should_manage_snapshots(self) -> bool:
        return False


def get_environment() -> Environment:
    """Factory function to get the appropriate environment based on AWS env var."""
    from Constants import AWS

    return AWSEnvironment() if AWS else LocalEnvironment()
