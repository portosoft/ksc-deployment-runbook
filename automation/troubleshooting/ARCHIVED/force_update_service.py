import paramiko
import os
import sys


def force_update_service(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        remote_python_script = "/var/opt/kaspersky/ksc-web-console/start_console.py"
        unit_file = "/etc/systemd/system/ksc-web-console.service"

        print(f"--- Force updating {unit_file} ---")

        # We will use a heredoc to overwrite the file with the correct content
        content = f"""[Unit]
Description=Kaspersky Security Center Web Console
After=network.target klnagent.service

[Service]
Type=simple
User=root
WorkingDirectory=/var/opt/kaspersky/ksc-web-console
ExecStart=/usr/bin/python3 {remote_python_script}
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
        # Save to temp
        sftp = client.open_sftp()
        with sftp.file("/tmp/ksc-web-console.service", "w") as f:
            f.write(content)
        sftp.close()

        # Move to systemd and reload
        cmd = (
            f'echo "{password}" | sudo -S mv /tmp/ksc-web-console.service {unit_file} && '
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

    force_update_service(host, user, password)
