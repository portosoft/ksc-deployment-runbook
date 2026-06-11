import paramiko
import os
import sys


def upload_and_update_service(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        local_path = r"c:\Antigravity\ksc-deployment-runbook\scripts\start_console.py"
        remote_path = "/var/opt/kaspersky/ksc-web-console/start_console.py"

        # Upload
        sftp = client.open_sftp()
        sftp.put(local_path, "/tmp/start_console.py")
        sftp.close()

        # Move to correct location and set permissions
        print(f"--- Moving script to {remote_path} ---")
        client.exec_command(f"sudo -S mv /tmp/start_console.py {remote_path}")
        client.exec_command(f"sudo chown root:root {remote_path}")
        client.exec_command(f"sudo chmod 755 {remote_path}")

        # Update systemd unit
        print("--- Updating systemd unit ---")
        unit_file = "/etc/systemd/system/ksc-web-console.service"
        # Replace ExecStart line
        cmd = f"sudo sed -i 's|ExecStart=.*|ExecStart=/usr/bin/python3 {remote_path}|' {unit_file}"
        client.exec_command(cmd)

        # Reload systemd
        print("--- systemctl daemon-reload ---")
        client.exec_command("sudo systemctl daemon-reload")

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    upload_and_update_service(host, user, password)
