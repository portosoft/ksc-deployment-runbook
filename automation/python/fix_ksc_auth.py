#!/usr/bin/env python3
import os
import sys
import paramiko
import shlex
from dotenv import load_dotenv


def fix_ksc_auth():
    env_path = "configs/env/ksc_vars.env"
    load_dotenv(env_path)
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    # Senha administrativa - obtida do ambiente de forma segura
    ksc_admin_pass = os.getenv("KSC_ADMIN_PASS")
    if not ksc_admin_pass:
        print("ERROR: A variavel KSC_ADMIN_PASS nao esta definida no ambiente.")
        sys.exit(1)

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())

    try:
        client.connect(host, username=user, password=password, timeout=30)

        cmd = f"LD_LIBRARY_PATH=/opt/kaspersky/ksc64/lib /opt/kaspersky/ksc64/sbin/kladduser -n kscadmin -u kscadmin -r Administrator"

        print(f"Executando no servidor...")
        # 🛡️ Sentinel: Never pass secrets as command-line arguments (e.g. -p) to remote binaries
        # to prevent exposure in the process list (ps aux). Pass them via stdin instead.
        stdin, stdout, stderr = client.exec_command(f"sudo -S {cmd}")
        # Provide sudo password
        stdin.write(password + "\n")
        # Provide kladduser password via stdin prompt
        stdin.write(ksc_admin_pass + "\n")
        # In case kladduser asks for confirmation, provide it again
        stdin.write(ksc_admin_pass + "\n")
        stdin.flush()
        stdin.channel.shutdown_write()

        out = stdout.read().decode("utf-8").strip()
        err = stderr.read().decode("utf-8").strip()
        status = stdout.channel.recv_exit_status()

        print(f"STATUS: {status}")
        if out:
            print(f"STDOUT: {out}")
        if err:
            print(f"STDERR: {err}")

        if status == 0:
            print("SUCCESS: Usuario kscadmin atualizado.")
        else:
            print("FAILURE: O comando kladduser falhou.")

        client.close()
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    fix_ksc_auth()
