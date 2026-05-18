import paramiko

import os

host = os.getenv("KSC_HOST", "<IP>")
user = os.getenv("KSC_USER", "<USER>")
password = os.getenv("KSC_PASS", "<SENHA>")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(hostname=host, username=user, password=password, timeout=10)
    stdin, stdout, stderr = client.exec_command(
        f"echo '{password}' | sudo -S find / -name '*ksc*.rpm' -o -name '*kaspersky*.rpm' -type f 2>/dev/null"
    )
    print("Arquivos RPM encontrados:")
    print(stdout.read().decode("utf-8"))
except Exception as e:
    print(e)
finally:
    client.close()
