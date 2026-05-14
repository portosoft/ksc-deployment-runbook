#!/usr/bin/env python3
import os
import sys
import paramiko
import shlex
from dotenv import load_dotenv

def fix_ksc_auth():
    env_path = "configs/env/ksc_vars.env"
    load_dotenv(env_path)
    host = os.getenv('KSC_HOST')
    user = os.getenv('KSC_USER')
    password = os.getenv('KSC_PASS')

    # Senha administrativa - usando uma fixa para teste se a do env falhar
    ksc_admin_pass = "Porto@2024!"

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Escapar a senha administrativa para o shell
        safe_pass = shlex.quote(ksc_admin_pass)

        cmd = f"LD_LIBRARY_PATH=/opt/kaspersky/ksc64/lib /opt/kaspersky/ksc64/sbin/kladduser -n kscadmin -u kscadmin -p {safe_pass} -r Administrator"

        print(f"Executando no servidor...")
        stdin, stdout, stderr = client.exec_command(f"sudo -S {cmd}")
        stdin.write(password + '\n')
        stdin.flush()

        out = stdout.read().decode('utf-8').strip()
        err = stderr.read().decode('utf-8').strip()
        status = stdout.channel.recv_exit_status()

        print(f"STATUS: {status}")
        if out: print(f"STDOUT: {out}")
        if err: print(f"STDERR: {err}")

        if status == 0:
            print("SUCCESS: Usuario kscadmin atualizado.")
        else:
            print("FAILURE: O comando kladduser falhou.")

        client.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    fix_ksc_auth()
