import paramiko
import os
import sys
import time


def verify(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect(host, username=user, password=password)

    print("Restarting KSC services...")
    client.exec_command(
        "sudo -S systemctl restart kladminserver_srv klnagent_srv klwebsrv_srv kliam_srv"
    )
    time.sleep(5)

    stdin, stdout, stderr = client.exec_command(
        "systemctl is-active kladminserver_srv klnagent_srv klwebsrv_srv kliam_srv"
    )
    print(f"Service States:\n{stdout.read().decode()}")
    client.close()


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")
    verify(host, user, password)
