#!/usr/bin/env python3
import os
import sys
import paramiko
from dotenv import load_dotenv

# Diagnóstico KSC 16.2 - Remediação Script SQL
# Autor: Antigravity (Expert KSC Linux)

def remediate_sql_script():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv('KSC_HOST')
    user = os.getenv('KSC_USER')
    password = os.getenv('KSC_PASS')

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(host, username=user, password=password)

        sql = """
        UPDATE mfa_totp_settings SET \"bMfaRequiredForAll\" = 0;
        SELECT \"bMfaRequiredForAll\" FROM mfa_totp_settings;
        """

        # Criar script temporário no servidor
        print("--- Creating temporary SQL script ---")
        client.exec_command(f"echo '{sql}' > /tmp/fix_mfa.sql")

        print("--- Executing SQL script as postgres ---")
        cmd = "sudo -S -u postgres psql -d ksc -f /tmp/fix_mfa.sql"
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + '\n')
        stdin.flush()

        print(f"STDOUT: {stdout.read().decode()}")
        print(f"STDERR: {stderr.read().decode()}")

        client.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    remediate_sql_script()
