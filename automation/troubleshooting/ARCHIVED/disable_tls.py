import paramiko
import os
import sys


def disable_tls_everywhere(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        target_dir = "/var/opt/kaspersky/ksc-web-console"
        print("--- Disabling TLS in nats.conf ---")

        # New nats.conf without TLS
        nats_conf = """
port: 8222
host: 0.0.0.0
"""
        sftp = client.open_sftp()
        with sftp.file("/tmp/nats.conf", "w") as f:
            f.write(nats_conf)
        sftp.close()
        client.exec_command(
            f'echo "{password}" | sudo -S mv /tmp/nats.conf {target_dir}/nats.conf'
        )

        print("--- Removing TLS from pm.config.js ---")
        stdin, stdout, stderr = client.exec_command(f"cat {target_dir}/pm.config.js")
        pm_content = stdout.read().decode("utf-8")

        # Remove TLS lines
        lines = pm_content.split("\n")
        new_lines = [line for line in lines if "NATS_TLS_" not in line]
        new_pm = "\n".join(new_lines)

        sftp = client.open_sftp()
        with sftp.file("/tmp/pm.config.js", "w") as f:
            f.write(new_pm)
        sftp.close()
        client.exec_command(
            f'echo "{password}" | sudo -S mv /tmp/pm.config.js {target_dir}/pm.config.js'
        )

        # Restart all
        print("--- Force restarting everything ---")
        client.exec_command(
            f'echo "{password}" | sudo -S systemctl stop ksc-web-console.service'
        )
        client.exec_command(f'echo "{password}" | sudo -S pkill -9 -f nats-server')
        client.exec_command(f'echo "{password}" | sudo -S pkill -9 -f node')
        client.exec_command(
            f'echo "{password}" | sudo -S systemctl start ksc-nats.service'
        )
        client.exec_command(
            f'echo "{password}" | sudo -S systemctl start ksc-web-console.service'
        )

        client.close()
        print("TLS disabled and services restarted.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    disable_tls_everywhere(host, user, password)
