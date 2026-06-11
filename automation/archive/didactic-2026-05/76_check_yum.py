import paramiko

import os

host = os.getenv("KSC_HOST", "<IP>")
user = os.getenv("KSC_USER", "<USER>")
password = os.getenv("KSC_PASS", "<SENHA>")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())

try:
    client.connect(hostname=host, username=user, password=password, timeout=10)
    stdin, stdout, stderr = client.exec_command(
        f"echo '{password}' | sudo -S yum install -y /home/suporte/ksc64-16.2.0-1023.x86_64.rpm"
    )
    print("STDOUT:", stdout.read().decode("utf-8"))
    print("STDERR:", stderr.read().decode("utf-8"))
except Exception as e:
    print(e)
finally:
    client.close()
