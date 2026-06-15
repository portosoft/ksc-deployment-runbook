import os
import paramiko
from dotenv import load_dotenv

def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")
    admin_pass = os.getenv("KSC_ADMIN_PASS")

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect(host, username=user, password=password)

    print("=== Creating kscadmin2 ===")
    cmd = f'sudo -S LD_LIBRARY_PATH=/opt/kaspersky/ksc64/lib /opt/kaspersky/ksc64/sbin/kladduser -n kscadmin2 -p "{admin_pass}"'
    stdin, stdout, stderr = client.exec_command(cmd)
    stdin.write(password + "\n")
    stdin.flush()
    print("Output:", stdout.read().decode().strip())
    print("Error:", stderr.read().decode().strip())

    print("\n=== Creating KLAdmins (default) ===")
    cmd2 = f'sudo -S LD_LIBRARY_PATH=/opt/kaspersky/ksc64/lib /opt/kaspersky/ksc64/sbin/kladduser -n KLAdmins -p "{admin_pass}"'
    stdin, stdout, stderr = client.exec_command(cmd2)
    stdin.write(password + "\n")
    stdin.flush()
    print("Output:", stdout.read().decode().strip())
    print("Error:", stderr.read().decode().strip())

    client.close()

if __name__ == "__main__":
    main()
