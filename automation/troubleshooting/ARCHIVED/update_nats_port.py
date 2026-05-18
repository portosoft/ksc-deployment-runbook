import paramiko
import os
import sys
import re


def update_ports_and_deploy(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # 1. Update start_console.js on server
        local_js = r"c:\Antigravity\ksc-deployment-runbook\scripts\start_console.js"
        remote_js = "/var/opt/kaspersky/ksc-web-console/start_console.js"
        sftp = client.open_sftp()
        sftp.put(local_js, "/tmp/start_console.js")
        client.exec_command(
            f'echo "{password}" | sudo -S mv /tmp/start_console.js {remote_js} && echo "{password}" | sudo -S chown root:root {remote_js}'
        )

        # 2. Update pm.config.js
        target_pm = "/var/opt/kaspersky/ksc-web-console/pm.config.js"
        stdin, stdout, stderr = client.exec_command(f"cat {target_pm}")
        pm_content = stdout.read().decode("utf-8")

        # Replace ports 4222 with 8222
        new_pm = pm_content.replace("'4222'", "'8222'").replace("4222", "8222")

        with sftp.file("/tmp/pm.config.js", "w") as f:
            f.write(new_pm)
        client.exec_command(
            f'echo "{password}" | sudo -S mv /tmp/pm.config.js {target_pm} && echo "{password}" | sudo -S chown root:root {target_pm}'
        )

        sftp.close()

        # 3. Restart Service
        client.exec_command(
            f'echo "{password}" | sudo -S systemctl restart ksc-web-console.service'
        )

        print("Ports updated to 8222 and service restarted.")
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    update_ports_and_deploy(host, user, password)
