import paramiko

import os

host = os.getenv("KSC_HOST", "<IP>")
user = os.getenv("KSC_USER", "<USER>")
password = os.getenv("KSC_PASS", "<SENHA>")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(hostname=host, username=user, password=password, timeout=10)
    print("Conectado. Fazendo upload do script de desinstalacao...")

    sftp = client.open_sftp()
    sftp.put("scratch/remote_uninstall.sh", "/tmp/remote_uninstall.sh")
    sftp.close()

    print("Executando desinstalacao...")
    stdin, stdout, stderr = client.exec_command(
        f"echo '{password}' | sudo -S bash /tmp/remote_uninstall.sh"
    )

    while True:
        line = stdout.readline()
        if not line:
            break
        print(line, end="")

    err = stderr.read().decode("utf-8")
    if err:
        print("STDERR:", err)

except Exception as e:
    print(e)
finally:
    client.close()
