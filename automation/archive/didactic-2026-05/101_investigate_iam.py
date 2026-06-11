import paramiko

import os

host = os.getenv("KSC_HOST", "<IP>")
user = os.getenv("KSC_USER", "<USER>")
password = os.getenv("KSC_PASS", "<SENHA>")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())


def run_sudo(cmd):
    full_cmd = f"echo '{password}' | sudo -S sh -c '{cmd}'"
    print(f"=== CMD: {cmd} ===")
    stdin, stdout, stderr = client.exec_command(full_cmd)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    if out:
        print(out.encode("ascii", errors="replace").decode("ascii"))
    if err and "senha para" not in err:
        print("STDERR:", err.encode("ascii", errors="replace").decode("ascii"))


try:
    client.connect(hostname=host, username=user, password=password, timeout=10)
    print("Conectado.")

    run_sudo("systemctl status kliam_srv.service")
    run_sudo("journalctl -u kliam_srv.service -n 20 --no-pager")
    run_sudo(
        "ls -la /var/opt/kaspersky/klnagent_srv/iam || echo 'Diretorio nao existe'"
    )
    run_sudo("find /var/opt/kaspersky -maxdepth 6 -iname 'iam_config*.yaml'")
    run_sudo("find /etc/opt/kaspersky -maxdepth 6 -iname 'iam_config*.yaml'")

except Exception as e:
    print(e)
finally:
    client.close()
