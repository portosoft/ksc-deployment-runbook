import paramiko
import os
import sys


def deploy_node_start(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        local_path = r"c:\Antigravity\ksc-deployment-runbook\scripts\start_console.js"
        remote_path = "/var/opt/kaspersky/ksc-web-console/start_console.js"
        unit_file = "/etc/systemd/system/ksc-web-console.service"

        print(f"--- Uploading {local_path} ---")
        sftp = client.open_sftp()
        sftp.put(local_path, "/tmp/start_console.js")
        sftp.close()

        print(f"--- Moving to {remote_path} ---")
        cmd = (
            f'echo "{password}" | sudo -S mv /tmp/start_console.js {remote_path} && '
            f'echo "{password}" | sudo -S chown root:root {remote_path} && '
            f'echo "{password}" | sudo -S chmod 755 {remote_path}'
        )
        stdin, stdout, stderr = client.exec_command(cmd)
        stdout.read()

        print(f"--- Updating {unit_file} ---")
        # Overwrite unit file to use Node
        unit_content = f"""[Unit]
Description=Kaspersky Security Center Web Console
After=network.target klnagent.service

[Service]
Type=simple
User=root
WorkingDirectory=/var/opt/kaspersky/ksc-web-console
ExecStart=/var/opt/kaspersky/ksc-web-console/node /var/opt/kaspersky/ksc-web-console/start_console.js
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
        with open("/tmp/ksc-web-console.service", "w") as f:
            f.write(unit_content)

        sftp = client.open_sftp()
        sftp.put("/tmp/ksc-web-console.service", "/tmp/ksc-web-console.service.remote")
        sftp.close()

        cmd = (
            f'echo "{password}" | sudo -S mv /tmp/ksc-web-console.service.remote {unit_file} && '
            f'echo "{password}" | sudo -S systemctl daemon-reload && '
            f'echo "{password}" | sudo -S systemctl restart ksc-web-console.service'
        )

        stdin, stdout, stderr = client.exec_command(cmd)
        print(f"STDOUT: {stdout.read().decode()}")
        print(f"STDERR: {stderr.read().decode()}")

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    deploy_node_start(host, user, password)
