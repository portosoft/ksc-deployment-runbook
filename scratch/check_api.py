#!/usr/bin/env python3
import os
import paramiko
from dotenv import load_dotenv

# Diagnóstico KSC 16.2 - Depuração Manual IAM
# Autor: Antigravity (Expert KSC Linux)

def debug_iam_manual():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv('KSC_HOST')
    user = os.getenv('KSC_USER')
    password = os.getenv('KSC_PASS')

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(host, username=user, password=password)

        print("--- Running kliam debug ---")
        cmd = "sudo -S -u ksc /opt/kaspersky/ksc64/sbin/kliam --config /var/opt/kaspersky/klnagent_srv/iam/iam_config.yaml"
        stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
        stdin.write(password + '\n')
        stdin.flush()

        # O comando deve rodar por um tempo
        try:
            print(f"STDOUT: {stdout.read().decode()}")
            print(f"STDERR: {stderr.read().decode()}")
        except Exception:
            print("Finished or timed out.")

        client.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    debug_iam_manual()
