import paramiko

import os

host = os.getenv("KSC_HOST", "<IP>")
user = os.getenv("KSC_USER", "<USER>")
password = os.getenv("KSC_PASS", "<SENHA>")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())

try:
    client.connect(hostname=host, username=user, password=password, timeout=10)
    print("Reinstalando via yum reinstall...")

    script = """#!/bin/bash
set -x
sudo yum reinstall -y /home/suporte/ksc64-16.2.0-1023.x86_64.rpm

echo "=== PREPARANDO POSTINSTALL ==="
cat > /tmp/ksc_response.txt << 'EOF'
KLSRV_ACCEPT_EULA=1
KLSRV_DB_TYPE=PostgreSQL
KLSRV_DB_HOST=127.0.0.1
KLSRV_DB_PORT=5432
KLSRV_DB_NAME=ksc
KLSRV_DB_USER=kluser
KLSRV_DB_PASSWORD=[REDACTED_DB_PASS]
KLSRV_ADMIN_PASSWORD=[REDACTED_ADMIN_PASS]
EOF

if [ -f /opt/kaspersky/ksc64/lib/bin/setup/postinstall.pl ]; then
    sudo /opt/kaspersky/ksc64/lib/bin/setup/postinstall.pl --auto-install=/tmp/ksc_response.txt
    sudo systemctl daemon-reload
    sudo systemctl enable kladminserver_srv kliam_srv
    sudo systemctl restart kladminserver_srv
    sleep 30
    sudo systemctl restart kliam_srv
    sleep 15
    sudo systemctl status kliam_srv --no-pager
    sudo ls -la /var/opt/kaspersky/klnagent_srv/iam
else
    echo "ERRO: postinstall.pl nao encontrado apos reinstall!"
fi
"""

    sftp = client.open_sftp()
    sftp.putfo(paramiko.SFTPAttributes(), "/tmp/force_reinstall.sh")
    with sftp.file("/tmp/force_reinstall.sh", "w") as f:
        f.write(script)
    sftp.close()

    stdin, stdout, stderr = client.exec_command(
        f"echo '{password}' | sudo -S bash /tmp/force_reinstall.sh"
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
