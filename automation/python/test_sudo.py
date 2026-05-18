#!/usr/bin/env python3
import os
import sys
import paramiko
from dotenv import load_dotenv


def test_sudo():
    env_path = "configs/env/ksc_vars.env"
    load_dotenv(env_path)
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(host, username=user, password=password, timeout=10)
        print("Conectado via SSH.")

        stdin, stdout, stderr = client.exec_command("sudo -S whoami")
        stdin.write(password + "\n")
        stdin.flush()

        print("WHOAMI:", stdout.read().decode().strip())
        client.close()
    except Exception as e:
        print("ERRO:", e)


if __name__ == "__main__":
    test_sudo()
