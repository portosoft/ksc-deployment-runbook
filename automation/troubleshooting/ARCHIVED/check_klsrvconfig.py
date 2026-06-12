import paramiko
import os
import sys


def run_ssh_commands_with_sudo(host, user, password, commands):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=10)
        results = {}
        for cmd in commands:
            full_cmd = f"sudo -S {cmd}"
            stdin, stdout, stderr = client.exec_command(full_cmd)
            stdin.write(password + "\n")
            stdin.flush()
            results[cmd] = stdout.read().decode("utf-8")
        client.close()
        return results
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    if not all([host, user, password]):
        print("Missing env vars: KSC_HOST, KSC_USER, KSC_PASS")
        sys.exit(1)

    cmds = [
        "LD_LIBRARY_PATH=/opt/kaspersky/ksc64/lib /opt/kaspersky/ksc64/sbin/klsrvconfig --help"
    ]
    res = run_ssh_commands_with_sudo(host, user, password, cmds)
    print(res)
