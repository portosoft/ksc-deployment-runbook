import paramiko
import os
import sys

def check_ksc_camel_units(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Check CamelCase units
        print("--- Checking KSC CamelCase Units Status ---")
        units = [
            "KSCWebConsole.service",
            "KSCSvcWebConsole.service",
            "KSCWebConsoleManagement.service",
            "KSCWebConsolePlugin.service",
            "KSCWebConsoleNATS.service"
        ]

        for unit in units:
            print(f"--- Status for {unit} ---")
            stdin, stdout, stderr = client.exec_command(f"sudo -S systemctl status {unit}")
            stdin.write(password + '\n')
            stdin.flush()
            print(stdout.read().decode('utf-8'))

        # Read KSCSvcWebConsole content
        print("--- Reading KSCSvcWebConsole.service ---")
        stdin, stdout, stderr = client.exec_command("sudo -S cat /etc/systemd/system/KSCSvcWebConsole.service")
        stdin.write(password + '\n')
        stdin.flush()
        print(stdout.read().decode('utf-8'))

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    check_ksc_camel_units(host, user, password)
