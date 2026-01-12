import logging
import os
import select
import signal
import subprocess
import sys
from glob import glob
from random import choice
from time import sleep, time

import requests
from rich.console import Console

from Backup import NoOpSnapshotManager, Snapshot, SnapshotManager
from Constants import (
    AWS,
    DEV,
    DOCKER,
    ETH_ADDR,
    KILL_TIME,
    SNAPSHOT_DAYS,
    VPN,
    VPN_TIMEOUT,
)
from Environment import AWSEnvironment, Environment, LocalEnvironment
from MEV import Booster

home_dir = os.path.expanduser("~")
platform = sys.platform.lower()
console = Console(highlight=False)
print = console.print


class Node:
    def __init__(self, env: Environment, snapshot: SnapshotManager, booster: Booster | None = None):
        self.env = env
        self.snapshot = snapshot
        self.booster = booster or Booster()

        on_mac = platform == "darwin"
        prefix = env.get_data_prefix() if DOCKER else home_dir
        geth_dir_base = f"/{'Library/Ethereum' if on_mac else '.ethereum'}"
        prysm_dir_base = f"/{'Library/Eth2' if on_mac else '.eth2'}"
        prysm_wallet_postfix = f"{'V' if on_mac else 'v'}alidators/prysm-wallet-v2"
        geth_dir_postfix = "/holesky" if DEV else ""

        self.geth_data_dir = f"{prefix}{geth_dir_base}{geth_dir_postfix}"
        self.prysm_data_dir = f"{prefix}{prysm_dir_base}"
        self.prysm_wallet_dir = f"{self.prysm_data_dir}{prysm_wallet_postfix}"

        ipc_postfix = "/geth.ipc"
        self.ipc_path = self.geth_data_dir + ipc_postfix
        self.kill_in_progress = False
        self.terminating = False
        self.processes = []
        self.logs_file = env.get_logs_path()
        with open(self.logs_file, "w") as _:
            pass

    def run_cmd(self, cmd):
        print(f"Running cmd: {' '.join(cmd)}")
        process = subprocess.Popen(
            cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        return process

    def execution(self):
        args = [
            "--http",
            "--http.api",
            "eth,net,engine,admin",
            "--state.scheme=path",
            # metrics flags
            # '--metrics', '--pprof',
            # '--metrics.expensive',
        ]

        if DEV:
            args.append("--holesky")
        else:
            args.append("--mainnet")

        if DOCKER:
            args += [
                f"--datadir={self.geth_data_dir}",
                # f"--maxpeers={MAX_PEERS}"
            ]

        cmd = ["geth"] + args
        return self.run_cmd(cmd)

    def consensus(self):
        args = [
            "--accept-terms-of-use",
            f"--execution-endpoint={self.ipc_path}",
            f"--suggested-fee-recipient={ETH_ADDR}",
            "--blob-storage-layout=by-epoch",
            # alternatively http://127.0.0.1:18550
            "--http-mev-relay=http://localhost:18550",
            "--enable-backfill",
        ]

        prysm_dir = "./consensus/prysm"

        if DEV:
            args.append("--holesky")
            args.append(f"--genesis-state={prysm_dir}/genesis.ssz")
        else:
            args.append("--mainnet")

        if DOCKER:
            args += [
                f"--datadir={self.prysm_data_dir}",
                # f"--p2p-max-peers={MAX_PEERS}"
            ]

        p2p_host = self.env.get_p2p_host_dns(DEV)
        if p2p_host:
            args += [f"--p2p-host-dns={p2p_host}"]

        state_filename = glob(f"{prysm_dir}/state*.ssz")[0]
        block_filename = glob(f"{prysm_dir}/block*.ssz")[0]
        args += [
            f"--checkpoint-state={state_filename}",
            f"--checkpoint-block={block_filename}",
            "--checkpoint-sync-url=https://sync-mainnet.beaconcha.in",
            "--genesis-beacon-api-url=https://sync-mainnet.beaconcha.in",
        ]
        cmd = ["beacon-chain"] + args
        return self.run_cmd(cmd)

    def validation(self):
        args = [
            "--accept-terms-of-use",
            # ENABLE THIS FOR MEV
            "--enable-builder",
            f"--wallet-dir={self.prysm_wallet_dir}",
            f"--suggested-fee-recipient={ETH_ADDR}",
            f"--wallet-password-file={self.prysm_wallet_dir}/password.txt",
        ]

        if DEV:
            args.append("--holesky")
        else:
            args.append("--mainnet")

        cmd = ["validator"] + args
        return self.run_cmd(cmd)

    def mev(self):
        args = ["-relay-check"]
        if DEV:
            args.append("-holesky")
        else:
            args.append("-mainnet")

        args += ["-relays", ",".join(self.relays)]
        cmd = ["mev-boost"] + args
        return self.run_cmd(cmd)

    def vpn(self):
        VPN_USER = os.environ["VPN_USER"]
        VPN_PASS = os.environ["VPN_PASS"]
        with open("vpn_creds.txt", "w") as file:
            file.write(f"{VPN_USER}\n{VPN_PASS}")
        cfg = choice(glob("config/us*.tcp.ovpn"))
        args = ["--config", cfg, "--auth-user-pass", "vpn_creds.txt"]
        cmd = ["openvpn"] + args
        return self.run_cmd(cmd)

    def start(self):
        processes = []
        if VPN:

            def get_ip():
                return requests.get("https://4.tnedi.me", timeout=5).text

            start_ip = get_ip()
            vpn_connected = False
            while not vpn_connected:
                vpn_process = self.vpn()
                processes.append({"process": vpn_process, "prefix": "xxx OPENVPN__ xxx"})
                elapsed = 0
                while start_ip == get_ip() and elapsed < VPN_TIMEOUT:
                    print("Waiting for VPN...")
                    sleep(VPN_TIMEOUT / 3)
                    elapsed += VPN_TIMEOUT / 3

                if start_ip == get_ip():
                    print(f"VPN connection timed out after {VPN_TIMEOUT}s, retrying...")
                    os.kill(vpn_process.pid, signal.SIGKILL)
                    processes.pop()
                else:
                    vpn_connected = True
        processes += [
            {"process": self.execution(), "prefix": "<<< EXECUTION >>>"},
            {"process": self.consensus(), "prefix": "[[[ CONSENSUS ]]]"},
            {"process": self.validation(), "prefix": "(( _VALIDATION ))"},
            {"process": self.mev(), "prefix": "+++ MEV_BOOST +++"},
        ]

        streams = []
        # Label processes with log prefix
        for meta in processes:
            meta["process"].stdout.prefix = meta["prefix"]
            streams.append(meta["process"].stdout)

        self.processes = processes
        self.streams = streams
        return processes, streams

    def signal_processes(self, sig, prefix, hard=True):
        if hard or not self.kill_in_progress:
            print(f"{prefix} all processes... [{'HARD' if hard else 'SOFT'}]")
            for meta in self.processes:
                try:
                    os.kill(meta["process"].pid, sig)
                except Exception as e:
                    logging.exception(e)

    def interrupt(self, **kwargs):
        self.signal_processes(signal.SIGINT, "Interrupting", **kwargs)

    def terminate(self, **kwargs):
        self.signal_processes(signal.SIGTERM, "Terminating", **kwargs)

    def kill(self, **kwargs):
        self.signal_processes(signal.SIGKILL, "Killing", **kwargs)

    def color(self, text):
        styles = {
            "OPENVPN": "orange",
            "EXECUTION": "bold magenta",
            "CONSENSUS": "bold cyan",
            "VALIDATION": "bold yellow",
            "MEV_BOOST": "bold green",
            "INFO": "green",
            "WARN": "bright_yellow",
            "WARNING": "bright_yellow",
            "ERROR": "bright_red",
            "level=info": "green",
            "level=warning": "bright_yellow",
            "level=error": "bright_red",
        }
        for key, style in styles.items():
            text = text.replace(key, f"[{style}]{key}[/{style}]")
        return text

    def print_line(self, prefix, line):
        line = line.decode("UTF-8").strip()
        if line:
            log = f"{prefix} {line}"
            colored = self.color(log)
            print(colored if self.env.use_colored_logs() else log)
            with open(self.logs_file, "a") as file:
                file.write(f"{log}\n")
            return log

    def stream_logs(self, rstreams):
        return [self.print_line(stream.prefix, stream.readline()) for stream in rstreams]

    def squeeze_logs(self, processes):
        for meta in processes:
            stream = meta["process"].stdout
            for line in iter(stream.readline, b""):
                self.print_line(stream.prefix, line)

    def interrupt_on_error(self, logs):
        for log in logs:
            if log and "Beacon backfilling failed" in log:
                self.interrupt(hard=False)
                return True

    def poll_processes(self, processes):
        return (meta["process"].poll() is not None for meta in processes)

    def all_processes_are_dead(self, processes):
        return all(self.poll_processes(processes))

    def any_process_is_dead(self, processes):
        return any(self.poll_processes(processes))

    def handle_gracefully(self, processes, hard):
        def wait_for_exit():
            start = time()
            while not self.all_processes_are_dead(processes) and time() - start < KILL_TIME:
                sleep(1)
            return self.all_processes_are_dead(processes)

        if not wait_for_exit():
            self.terminate(hard=hard)
        if not wait_for_exit():
            self.kill(hard=hard)
        # Log rest of output
        self.squeeze_logs(self.processes)

    def run(self):
        if self.env.should_manage_snapshots():
            terminate = self.snapshot.update()
            if terminate:
                self.terminating = True
                self.snapshot.terminate()
                while self.terminating:
                    pass
        while True:
            self.most_recent = self.snapshot.backup()
            self.relays = self.booster.get_relays()
            processes, streams = self.start()
            backup_is_recent = True
            sent_interrupt = False

            while True:
                rstreams, _, _ = select.select(streams, [], [])
                backup_is_recent = not self.snapshot.is_older_than(self.most_recent, SNAPSHOT_DAYS)
                if not backup_is_recent and not sent_interrupt:
                    print("Pausing node to initiate snapshot.")
                    self.interrupt(hard=False)
                    sent_interrupt = True

                # Stream output
                logs = self.stream_logs(rstreams)
                self.interrupt_on_error(logs)
                if self.any_process_is_dead(processes):
                    break

            self.handle_gracefully(self.processes, hard=False)

    def stop(self):
        self.kill_in_progress = True
        self.handle_gracefully(self.processes, hard=True)
        print("Node stopped")
        if (
            self.env.should_manage_snapshots()
            and self.snapshot.instance_is_draining()
            and not self.terminating
        ):
            self.snapshot.force_create()
            self.snapshot.update()
        exit(0)


def main():
    env = AWSEnvironment() if AWS else LocalEnvironment()
    snapshot = Snapshot() if AWS else NoOpSnapshotManager()
    node = Node(env=env, snapshot=snapshot)

    def handle_signal(*_):
        node.stop()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    node.run()


if __name__ == "__main__":
    main()

# TODO:
# - export metrics / have an easy way to monitor, Prometheus and Grafana Cloud free, node exporter
# for prod, use savings plan (strictly better alt to reserved instances)
#   - compute savings plan ec2 - r6g.xlarge $0.10 53% 3 yrs upfront / $0.14 32% 1 yr upfront
#       ∧∧∧ More flexible
#       ∨∨∨ Limited to instance family r6g - bad if using t4g, fine for either r6g or m6g
#   - ec2 instance savings pla - r6g.xlarge $0.08 62% 3 yrs upfront / $0.12 41% 1 yr upfront
# - cut max peers to save on data out costs

# Extra:
# turn off node for 10 min every 24 hrs?
# - data integrity protection
#   - shutdown / terminate instance if process fails and others continue => forces new vol from last snapshot
#       - perhaps implement counter so if 3 process failures in a row, terminate instance
#   - use `geth --exec '(eth?.syncing?.currentBlock/eth?.syncing?.highestBlock)*100' attach --datadir /mnt/ebs/.ethereum/holesky`
#       - will yield NaN if already synced or 68.512213 if syncing
# - enable swap space if need more memory w 4vCPUs
#   - disabled on host by default for ecs optimized amis
#   - also need to set swap in task def
#   - https://docs.aws.amazon.com/AmazonECS/latest/developerguide/container-swap.html
# - use trusted nodes json
#   - perhaps this https://www.ethernodes.org/tor-seed-nodes
#   - and this https://www.reddit.com/r/ethdev/comments/kklm0j/comment/gyndv4a/?utm_source=share&utm_medium=web2x&context=3
