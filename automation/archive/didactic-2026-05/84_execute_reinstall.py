import paramiko

import os

host = os.getenv("KSC_HOST", "<IP>")
user = os.getenv("KSC_USER", "<USER>")
password = os.getenv("KSC_PASS", "<SENHA>")

client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.RejectPolicy())

try:
    client.connect(hostname=host, username=user, password=password, timeout=10)
    print("Conectado. Fazendo upload...")

    sftp = client.open_sftp()
    sftp.put("scratch/remote_reinstall.sh", "/tmp/remote_reinstall.sh")
    sftp.close()

    print("Executando reinstall...")
    stdin, stdout, stderr = client.exec_command(
        f"echo '{password}' | sudo -S bash /tmp/remote_reinstall.sh"
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
