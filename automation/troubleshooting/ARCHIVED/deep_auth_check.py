import paramiko
import os
import sys


def run_ssh(host, user, password, commands):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect(host, username=user, password=password)
    results = {}
    for cmd in commands:
        stdin, stdout, stderr = client.exec_command(f"sudo -S {cmd}")
        stdin.write(password + "\n")
        stdin.flush()
        results[cmd] = stdout.read().decode("utf-8")
    client.close()
    return results


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    check_cmds = [
        "sudo cat /var/lib/pgsql/data/pg_hba.conf",
        "sudo -u postgres psql -c \"SELECT usename, passwd FROM pg_shadow WHERE usename = 'kluser';\"",
    ]

    results = run_ssh(host, user, password, check_cmds)
    for cmd, out in results.items():
        print(f"--- {cmd} ---\n{out}")
