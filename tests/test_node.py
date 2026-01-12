"""Tests for the Node orchestrator."""

import os
import signal
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from staker.node import Node
from staker.snapshot import NoOpSnapshotManager


class MockEnvironment:
    """Mock environment for testing."""

    def __init__(
        self,
        logs_path="/tmp/test.log",
        data_prefix="/tmp",
        colored=True,
        snapshots=False,
    ):
        self._logs_path = logs_path
        self._data_prefix = data_prefix
        self._colored = colored
        self._snapshots = snapshots

    def get_logs_path(self):
        return self._logs_path

    def get_data_prefix(self):
        return self._data_prefix

    def get_p2p_host_dns(self, is_dev):
        return None

    def use_colored_logs(self):
        return self._colored

    def should_manage_snapshots(self):
        return self._snapshots


class TestNodeInit:
    """Tests for Node initialization."""

    @pytest.fixture
    def mock_deps(self, mocker, tmp_path):
        """Set up mocked dependencies."""
        mocker.patch("staker.node.DOCKER", False)
        mocker.patch("staker.node.DEV", True)
        logs_file = tmp_path / "logs.txt"
        return MockEnvironment(logs_path=str(logs_file))

    def test_initializes_with_environment(self, mock_deps):
        node = Node(env=mock_deps, snapshot=NoOpSnapshotManager())
        assert node.env == mock_deps

    def test_initializes_with_snapshot_manager(self, mock_deps):
        snapshot = NoOpSnapshotManager()
        node = Node(env=mock_deps, snapshot=snapshot)
        assert node.snapshot == snapshot

    def test_creates_logs_file(self, mock_deps):
        node = Node(env=mock_deps, snapshot=NoOpSnapshotManager())
        assert os.path.exists(node.logs_file)

    def test_sets_correct_data_dirs(self, mock_deps, mocker):
        mocker.patch("staker.node.platform", "linux")
        node = Node(env=mock_deps, snapshot=NoOpSnapshotManager())
        assert ".ethereum" in node.geth_data_dir
        assert ".eth2" in node.prysm_data_dir


class TestNodeProcesses:
    """Tests for Node process management."""

    @pytest.fixture
    def node(self, mocker, tmp_path):
        mocker.patch("staker.node.DOCKER", False)
        mocker.patch("staker.node.DEV", True)
        logs_file = tmp_path / "logs.txt"
        env = MockEnvironment(logs_path=str(logs_file))
        return Node(env=env, snapshot=NoOpSnapshotManager())

    def test_run_cmd_starts_process(self, node, mocker):
        mock_popen = MagicMock()
        mocker.patch("staker.node.subprocess.Popen", return_value=mock_popen)

        result = node._run_cmd(["echo", "test"])

        assert result == mock_popen

    def test_signal_processes_sends_signal(self, node, mocker):
        mock_process = MagicMock()
        mock_process.pid = 12345
        node.processes = [{"process": mock_process}]

        mock_kill = mocker.patch("os.kill")

        node._signal_processes(signal.SIGINT, "Testing")

        mock_kill.assert_called_once_with(12345, signal.SIGINT)

    def test_signal_processes_handles_exception(self, node, mocker):
        mock_process = MagicMock()
        mock_process.pid = 12345
        node.processes = [{"process": mock_process}]

        mocker.patch("os.kill", side_effect=ProcessLookupError())

        # Should not raise
        node._signal_processes(signal.SIGINT, "Testing")

    def test_interrupt_sends_sigint(self, node, mocker):
        mock_signal = mocker.patch.object(node, "_signal_processes")
        node._interrupt(hard=True)
        mock_signal.assert_called_once()
        call_args = mock_signal.call_args
        assert call_args[0][0] == signal.SIGINT
        assert call_args[0][1] == "Interrupting"

    def test_terminate_sends_sigterm(self, node, mocker):
        mock_signal = mocker.patch.object(node, "_signal_processes")
        node._terminate(hard=True)
        mock_signal.assert_called_once()
        call_args = mock_signal.call_args
        assert call_args[0][0] == signal.SIGTERM
        assert call_args[0][1] == "Terminating"

    def test_kill_sends_sigkill(self, node, mocker):
        mock_signal = mocker.patch.object(node, "_signal_processes")
        node._kill(hard=True)
        mock_signal.assert_called_once()
        call_args = mock_signal.call_args
        assert call_args[0][0] == signal.SIGKILL
        assert call_args[0][1] == "Killing"


class TestNodeLogging:
    """Tests for Node logging functionality."""

    @pytest.fixture
    def node(self, mocker, tmp_path):
        mocker.patch("staker.node.DOCKER", False)
        mocker.patch("staker.node.DEV", True)
        logs_file = tmp_path / "logs.txt"
        env = MockEnvironment(logs_path=str(logs_file), colored=True)
        return Node(env=env, snapshot=NoOpSnapshotManager())

    def test_print_line_writes_to_file(self, node):
        node._print_line("PREFIX", b"test message\n")

        with open(node.logs_file) as f:
            content = f.read()
        assert "PREFIX test message" in content

    def test_print_line_returns_formatted_log(self, node):
        result = node._print_line("PREFIX", b"test\n")
        assert result == "PREFIX test"

    def test_print_line_returns_none_for_empty(self, node):
        result = node._print_line("PREFIX", b"   \n")
        assert result is None


class TestNodeProcessState:
    """Tests for Node process state checking."""

    @pytest.fixture
    def node(self, mocker, tmp_path):
        mocker.patch("staker.node.DOCKER", False)
        mocker.patch("staker.node.DEV", True)
        logs_file = tmp_path / "logs.txt"
        env = MockEnvironment(logs_path=str(logs_file))
        return Node(env=env, snapshot=NoOpSnapshotManager())

    def test_all_processes_are_dead_true(self, node):
        mock_proc1 = MagicMock()
        mock_proc1.poll.return_value = 0  # Dead
        mock_proc2 = MagicMock()
        mock_proc2.poll.return_value = 1  # Dead

        processes = [{"process": mock_proc1}, {"process": mock_proc2}]
        assert node._all_processes_are_dead(processes) is True

    def test_all_processes_are_dead_false(self, node):
        mock_proc1 = MagicMock()
        mock_proc1.poll.return_value = None  # Running
        mock_proc2 = MagicMock()
        mock_proc2.poll.return_value = 0  # Dead

        processes = [{"process": mock_proc1}, {"process": mock_proc2}]
        assert node._all_processes_are_dead(processes) is False

    def test_any_process_is_dead_true(self, node):
        mock_proc1 = MagicMock()
        mock_proc1.poll.return_value = None  # Running
        mock_proc2 = MagicMock()
        mock_proc2.poll.return_value = 0  # Dead

        processes = [{"process": mock_proc1}, {"process": mock_proc2}]
        assert node._any_process_is_dead(processes) is True

    def test_any_process_is_dead_false(self, node):
        mock_proc1 = MagicMock()
        mock_proc1.poll.return_value = None  # Running
        mock_proc2 = MagicMock()
        mock_proc2.poll.return_value = None  # Running

        processes = [{"process": mock_proc1}, {"process": mock_proc2}]
        assert node._any_process_is_dead(processes) is False


class TestNodeErrorHandling:
    """Tests for Node error detection."""

    @pytest.fixture
    def node(self, mocker, tmp_path):
        mocker.patch("staker.node.DOCKER", False)
        mocker.patch("staker.node.DEV", True)
        logs_file = tmp_path / "logs.txt"
        env = MockEnvironment(logs_path=str(logs_file))
        return Node(env=env, snapshot=NoOpSnapshotManager())

    def test_interrupt_on_error_detects_backfill_failure(self, node, mocker):
        mock_interrupt = mocker.patch.object(node, "_interrupt")

        logs = ["Normal log", "Beacon backfilling failed error", "Another log"]
        result = node._interrupt_on_error(logs)

        assert result is True
        mock_interrupt.assert_called_once_with(hard=False)

    def test_interrupt_on_error_ignores_normal_logs(self, node, mocker):
        mock_interrupt = mocker.patch.object(node, "_interrupt")

        logs = ["Normal log", "Everything OK", None]
        result = node._interrupt_on_error(logs)

        assert result is False
        mock_interrupt.assert_not_called()


class TestNodeGracefulShutdown:
    """Tests for graceful shutdown handling."""

    @pytest.fixture
    def node(self, mocker, tmp_path):
        mocker.patch("staker.node.DOCKER", False)
        mocker.patch("staker.node.DEV", True)
        logs_file = tmp_path / "logs.txt"
        env = MockEnvironment(logs_path=str(logs_file))
        return Node(env=env, snapshot=NoOpSnapshotManager())

    def test_handle_gracefully_calls_interrupt(self, node, mocker):
        """Verify interrupt is called during graceful shutdown."""
        mock_interrupt = mocker.patch.object(node, "_interrupt")
        mocker.patch.object(node, "_terminate")
        mocker.patch.object(node, "_kill")
        mocker.patch.object(node, "_all_processes_are_dead", return_value=True)
        mocker.patch.object(node, "_squeeze_logs")

        node._handle_gracefully([], hard=True)

        mock_interrupt.assert_called_once()

    def test_handle_gracefully_squeezes_logs(self, node, mocker):
        """Verify logs are squeezed at end of graceful shutdown."""
        mocker.patch.object(node, "_interrupt")
        mocker.patch.object(node, "_terminate")
        mocker.patch.object(node, "_kill")
        mocker.patch.object(node, "_all_processes_are_dead", return_value=True)
        mock_squeeze = mocker.patch.object(node, "_squeeze_logs")

        node._handle_gracefully([], hard=True)

        mock_squeeze.assert_called_once()

    def test_stop_sets_kill_in_progress(self, node, mocker):
        """Verify stop sets the kill_in_progress flag."""
        mocker.patch.object(node, "_handle_gracefully")
        mocker.patch("staker.node.exit")

        node.stop()

        assert node.kill_in_progress is True

    def test_stop_calls_handle_gracefully(self, node, mocker):
        """Verify stop calls handle_gracefully."""
        mock_handle = mocker.patch.object(node, "_handle_gracefully")
        mocker.patch("staker.node.exit")

        node.stop()

        mock_handle.assert_called_once()


class TestNodeClientProcesses:
    """Tests for Ethereum client process methods."""

    @pytest.fixture
    def node(self, mocker, tmp_path):
        mocker.patch("staker.node.DOCKER", True)
        mocker.patch("staker.node.DEV", True)
        logs_file = tmp_path / "logs.txt"
        env = MockEnvironment(logs_path=str(logs_file))
        return Node(env=env, snapshot=NoOpSnapshotManager())

    def test_execution_includes_holesky_for_dev(self, node, mocker):
        mock_run = mocker.patch.object(node, "_run_cmd", return_value=MagicMock())
        node._execution()
        
        call_args = mock_run.call_args[0][0]
        assert "--holesky" in call_args

    def test_execution_includes_datadir_for_docker(self, node, mocker):
        mock_run = mocker.patch.object(node, "_run_cmd", return_value=MagicMock())
        node._execution()
        
        call_args = mock_run.call_args[0][0]
        assert any("--datadir=" in arg for arg in call_args)

    def test_consensus_includes_checkpoint_sync(self, node, mocker):
        mocker.patch("staker.node.glob", return_value=["prysm/state.ssz"])
        mock_run = mocker.patch.object(node, "_run_cmd", return_value=MagicMock())
        node._consensus()
        
        call_args = mock_run.call_args[0][0]
        assert any("checkpoint-sync-url" in arg for arg in call_args)

    def test_validation_includes_enable_builder(self, node, mocker):
        mock_run = mocker.patch.object(node, "_run_cmd", return_value=MagicMock())
        node._validation()
        
        call_args = mock_run.call_args[0][0]
        assert "--enable-builder" in call_args

    def test_mev_includes_relays(self, node, mocker):
        node.relays = ["http://relay1", "http://relay2"]
        mock_run = mocker.patch.object(node, "_run_cmd", return_value=MagicMock())
        node._mev()
        
        call_args = mock_run.call_args[0][0]
        assert "-relays" in call_args
        # Check that comma-separated relays are present
        relay_arg_idx = call_args.index("-relays") + 1
        assert "relay1" in call_args[relay_arg_idx]


class TestNodeVPN:
    """Tests for VPN handling."""

    @pytest.fixture
    def node(self, mocker, tmp_path):
        mocker.patch("staker.node.DOCKER", False)
        mocker.patch("staker.node.DEV", True)
        logs_file = tmp_path / "logs.txt"
        env = MockEnvironment(logs_path=str(logs_file))
        return Node(env=env, snapshot=NoOpSnapshotManager())

    def test_vpn_creates_creds_file(self, node, mocker, tmp_path):
        mocker.patch.dict(os.environ, {"VPN_USER": "testuser", "VPN_PASS": "testpass"})
        mocker.patch("staker.node.glob", return_value=["config/us1.tcp.ovpn"])
        mock_run = mocker.patch.object(node, "_run_cmd", return_value=MagicMock())
        mocker.patch("staker.node.choice", return_value="config/us1.tcp.ovpn")
        
        # Change to tmp dir to write creds file there
        original_dir = os.getcwd()
        os.chdir(tmp_path)
        try:
            node._vpn()
        finally:
            os.chdir(original_dir)
        
        mock_run.assert_called_once()
        assert "openvpn" in mock_run.call_args[0][0]


class TestNodeStart:
    """Tests for the start method."""

    @pytest.fixture
    def node(self, mocker, tmp_path):
        mocker.patch("staker.node.DOCKER", False)
        mocker.patch("staker.node.DEV", True)
        mocker.patch("staker.node.VPN", False)
        logs_file = tmp_path / "logs.txt"
        env = MockEnvironment(logs_path=str(logs_file))
        return Node(env=env, snapshot=NoOpSnapshotManager())

    def test_start_returns_processes_and_streams(self, node, mocker):
        mock_proc = MagicMock()
        mock_proc.stdout = MagicMock()
        mocker.patch.object(node, "_execution", return_value=mock_proc)
        mocker.patch.object(node, "_consensus", return_value=mock_proc)
        mocker.patch.object(node, "_validation", return_value=mock_proc)
        mocker.patch.object(node, "_mev", return_value=mock_proc)
        
        processes, streams = node._start()
        
        assert len(processes) == 4
        assert len(streams) == 4

    def test_start_assigns_prefixes_to_streams(self, node, mocker):
        mock_proc = MagicMock()
        mock_proc.stdout = MagicMock()
        mocker.patch.object(node, "_execution", return_value=mock_proc)
        mocker.patch.object(node, "_consensus", return_value=mock_proc)
        mocker.patch.object(node, "_validation", return_value=mock_proc)
        mocker.patch.object(node, "_mev", return_value=mock_proc)
        
        processes, _ = node._start()
        
        prefixes = [p["prefix"] for p in processes]
        assert "<<< EXECUTION >>>" in prefixes
        assert "[[[ CONSENSUS ]]]" in prefixes


class TestNodeStreamLogs:
    """Tests for log streaming."""

    @pytest.fixture
    def node(self, mocker, tmp_path):
        mocker.patch("staker.node.DOCKER", False)
        mocker.patch("staker.node.DEV", True)
        logs_file = tmp_path / "logs.txt"
        env = MockEnvironment(logs_path=str(logs_file))
        return Node(env=env, snapshot=NoOpSnapshotManager())

    def test_stream_logs_processes_multiple_streams(self, node, mocker):
        mock_stream1 = MagicMock()
        mock_stream1.prefix = "PRE1"
        mock_stream1.readline.return_value = b"log1\n"
        
        mock_stream2 = MagicMock()
        mock_stream2.prefix = "PRE2"
        mock_stream2.readline.return_value = b"log2\n"
        
        result = node._stream_logs([mock_stream1, mock_stream2])
        
        assert len(result) == 2
        assert "PRE1 log1" in result
        assert "PRE2 log2" in result

    def test_squeeze_logs_drains_all_output(self, node, mocker):
        mock_stream = MagicMock()
        mock_stream.prefix = "TEST"
        mock_stream.readline.side_effect = [b"line1\n", b"line2\n", b""]
        
        mock_proc = MagicMock()
        mock_proc.stdout = mock_stream
        
        node._squeeze_logs([{"process": mock_proc}])
        
        # Verify readline was called until empty
        assert mock_stream.readline.call_count == 3


