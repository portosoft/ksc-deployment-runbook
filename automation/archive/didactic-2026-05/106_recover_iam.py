import paramiko
import time

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

    # 1. Faz upload do yaml limpo para /tmp
    sftp = client.open_sftp()
    sftp.put("scratch/iam_config.yaml", "/tmp/iam_config.yaml")
    sftp.close()

    # 2. Move e acerta permissoes
    target_dir = "/var/opt/kaspersky/klnagent_srv/iam"
    run_sudo(f"mkdir -p {target_dir}")
    run_sudo(f"mv /tmp/iam_config.yaml {target_dir}/iam_config.yaml")
    run_sudo(f"chown ksc:kladmins {target_dir}/iam_config.yaml")
    run_sudo(f"chmod 660 {target_dir}/iam_config.yaml")

    # 3. Reinicia servico
    run_sudo("systemctl restart kliam_srv")
    print("Aguardando 10s para estabilizar...")
    time.sleep(10)

    # 4. Checa status
    run_sudo("systemctl status kliam_srv --no-pager")
    run_sudo("journalctl -u kliam_srv -n 20 --no-pager")

except Exception as e:
    print(e)
finally:
    client.close()
