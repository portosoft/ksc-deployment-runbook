#!/usr/bin/env python3
import os
import sys
import paramiko
from dotenv import load_dotenv

# Documentação: Este script limpa as tabelas de MFA do serviço IAM do KSC 16.2.
# Ele deve ser usado em situações de lockout onde o MFA está impedindo o acesso administrativo.


def purge_iam_mfa():
    # Carrega variáveis de ambiente de forma segura
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    if not all([host, user, password]):
        print("ERROR: Missing environment variables in ksc_vars.env")
        sys.exit(1)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())

    try:
        client.connect(host, username=user, password=password)

        print("--- Purging IAM MFA tables ---")
        queries = [
            "TRUNCATE iam.authentication_factors CASCADE;",
            "TRUNCATE iam.authentication_factors_secret CASCADE;",
            "TRUNCATE iam.authentication_factors_totp_settings CASCADE;",
        ]

        for q in queries:
            cmd = f'sudo -S -u postgres psql -d ksciam -c "{q}"'
            stdin, stdout, stderr = client.exec_command(cmd)
            stdin.write(password + "\n")
            stdin.flush()
            stdin.channel.shutdown_write()
            print(f"Query: {q} | Status: {stdout.read().decode().strip()}")

        print("--- Restarting all KSC services ---")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S systemctl restart kladminserver_srv kliam_srv ksc-web-console"
        )
        stdin.write(password + "\n")
        stdin.flush()
        stdin.channel.shutdown_write()
        stdout.channel.recv_exit_status()

        client.close()
        print("--- Done. Please try to login now. ---")
    except Exception as e:
        print("ERROR:", e)


if __name__ == "__main__":
    purge_iam_mfa()
