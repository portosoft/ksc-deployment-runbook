import os
import sys
import paramiko
from dotenv import load_dotenv

def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect(host, username=user, password=password)

    # Sed command to replace "displayName": "" with "displayName": "KSC Primary Server"
    # Note: Sed acts on the first occurrence or globally. The config.json has "displayName": "" in the servers array.
    sed_cmd = "sudo -S sed -i 's/\"displayName\": \"\"/\"displayName\": \"KSC Primary Server\"/g' /var/opt/kaspersky/ksc-web-console/server/config.json"
    print("Fixing config.json displayName...")
    stdin, stdout, stderr = client.exec_command(sed_cmd)
    stdin.write(password + "\n")
    stdin.flush()
    status = stdout.channel.recv_exit_status()
    if status != 0:
        print("Failed to run sed:", stderr.read().decode())
        sys.exit(1)

    print("Restarting ksc-web-console...")
    stdin, stdout, stderr = client.exec_command("sudo -S systemctl restart ksc-web-console")
    stdin.write(password + "\n")
    stdin.flush()
    status = stdout.channel.recv_exit_status()
    if status != 0:
        print("Failed to restart service:", stderr.read().decode())
        sys.exit(1)

    print("DONE! KSC Web Console has been restarted.")
    client.close()

if __name__ == "__main__":
    main()
