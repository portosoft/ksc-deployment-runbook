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
    print("Conectado. Enviando script...")

    sftp = client.open_sftp()
    sftp.put("scratch/remote_script.sh", "/tmp/remote_script.sh")
    sftp.close()

    print("Executando script remoto...")
    stdin, stdout, stderr = client.exec_command(
        f"echo '{password}' | sudo -S bash /tmp/remote_script.sh"
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
