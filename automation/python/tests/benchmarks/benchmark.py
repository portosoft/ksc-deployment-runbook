import time
from unittest.mock import MagicMock
import paramiko

class MockChannel:
    def recv_exit_status(self):
        time.sleep(0.05)
        return 0

class MockSSHClient(MagicMock):
    def exec_command(self, cmd):
        time.sleep(0.05)
        stdin = MagicMock()
        stdout = MagicMock()
        stdout.channel = MockChannel()
        stderr = MagicMock()
        return stdin, stdout, stderr

def run_unoptimized(client, harden_cmds):
    for cmd in harden_cmds:
        stdin, stdout, stderr = client.exec_command(f"sudo -S {cmd}")
        stdin.write("pass" + "\n")
        stdin.flush()
        status = stdout.channel.recv_exit_status()

def run_optimized(client, harden_cmds):
    # This is a sample optimized implementation using sh -c
    import shlex
    batch_cmd = " && ".join(harden_cmds)
    escaped_batch = shlex.quote(batch_cmd)
    stdin, stdout, stderr = client.exec_command(f"sudo -S sh -c {escaped_batch}")
    stdin.write("pass" + "\n")
    stdin.flush()
    status = stdout.channel.recv_exit_status()

cmds = [
    'sed -i "s/^#max_connections = .*/max_connections = 1000/" /var/lib/pgsql/16/data/postgresql.conf',
    "grep -q 'shared_preload_libraries' /var/lib/pgsql/16/data/postgresql.conf || echo \"shared_preload_libraries = 'pg_stat_statements'\" >> /var/lib/pgsql/16/data/postgresql.conf",
    "systemctl restart postgresql-16",
]

client = MockSSHClient()
start = time.time()
run_unoptimized(client, cmds)
unopt_time = time.time() - start
print(f"Unoptimized time: {unopt_time:.4f} seconds")

start = time.time()
run_optimized(client, cmds)
opt_time = time.time() - start
print(f"Optimized time:   {opt_time:.4f} seconds")
print(f"Improvement:      {unopt_time / opt_time:.2f}x faster")
