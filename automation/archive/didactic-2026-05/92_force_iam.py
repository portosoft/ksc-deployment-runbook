import paramiko

import os

host = os.getenv("KSC_HOST", "<IP>")
user = os.getenv("KSC_USER", "<USER>")
password = os.getenv("KSC_PASS", "<SENHA>")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(hostname=host, username=user, password=password, timeout=10)
    print("Conectado. Recriando banco de dados ksciam e enviando yaml...")

    script = """#!/bin/bash
set -x

echo "=== CRIANDO BANCO KSCIAM ==="
sudo -u postgres psql << 'SQL'
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'ksciam' AND pid <> pg_backend_pid();
DROP DATABASE IF EXISTS ksciam;
CREATE DATABASE ksciam OWNER kluser ENCODING 'UTF8' LC_COLLATE 'pt_BR.UTF-8' LC_CTYPE 'pt_BR.UTF-8';
SQL

echo "=== INJETANDO IAM YAML ==="
sudo mkdir -p /var/opt/kaspersky/klnagent_srv/iam
sudo mv /tmp/iam_config.yaml /var/opt/kaspersky/klnagent_srv/iam/iam_config.yaml
sudo chown ksc:kladmins /var/opt/kaspersky/klnagent_srv/iam/iam_config.yaml
sudo chmod 640 /var/opt/kaspersky/klnagent_srv/iam/iam_config.yaml

echo "=== REINICIANDO IAM ==="
sudo systemctl restart kliam_srv
sleep 15
sudo systemctl status kliam_srv --no-pager
sudo journalctl -u kliam_srv -n 50 --no-pager
"""

    sftp = client.open_sftp()
    sftp.put("scratch/iam_config.yaml", "/tmp/iam_config.yaml")

    sftp.putfo(paramiko.SFTPAttributes(), "/tmp/force_iam.sh")
    with sftp.file("/tmp/force_iam.sh", "w") as f:
        f.write(script)
    sftp.close()

    stdin, stdout, stderr = client.exec_command(
        f"echo '{password}' | sudo -S bash /tmp/force_iam.sh"
    )

    while True:
        line = stdout.readline()
        if not line:
            break
        print(line.encode("ascii", errors="replace").decode("ascii"), end="")

    err = stderr.read().decode("utf-8", errors="replace")
    if err:
        print("STDERR:", err.encode("ascii", errors="replace").decode("ascii"))

except Exception as e:
    print(e)
finally:
    client.close()
