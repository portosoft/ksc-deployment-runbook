import paramiko
import os
import sys


def disable_nats_tls(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        target_dir = "/var/opt/kaspersky/ksc-web-console"
        print(f"--- Disabling TLS in {target_dir}/nats.conf ---")

        # Simple nats.conf without TLS
        conf_content = "port: 8222\n"
        sftp = client.open_sftp()
        with sftp.file("/tmp/nats.conf", "w") as f:
            f.write(conf_content)
        sftp.close()

        client.exec_command(
            f'echo "{password}" | sudo -S mv /tmp/nats.conf {target_dir}/nats.conf'
        )
        client.exec_command(
            f'echo "{password}" | sudo -S systemctl restart ksc-nats.service'
        )

        # Update pm.config.js to NOT use TLS for NATS
        print(f"--- Disabling NATS TLS in pm.config.js ---")
        stdin, stdout, stderr = client.exec_command(f"cat {target_dir}/pm.config.js")
        pm_content = stdout.read().decode("utf-8")

        # We'll just comment out or remove TLS lines in the env block
        new_pm = (
            pm_content.replace("NATS_TLS_KEYFILE:", "// NATS_TLS_KEYFILE:")
            .replace("NATS_TLS_CERTFILE:", "// NATS_TLS_CERTFILE:")
            .replace("NATS_TLS_CAFILE:", "// NATS_TLS_CAFILE:")
        )

        sftp = client.open_sftp()
        with sftp.file("/tmp/pm.config.js", "w") as f:
            f.write(new_pm)
        sftp.close()

        client.exec_command(
            f'echo "{password}" | sudo -S mv /tmp/pm.config.js {target_dir}/pm.config.js'
        )

        # Restart Web Console
        client.exec_command(
            f'echo "{password}" | sudo -S systemctl restart ksc-web-console.service'
        )

        print("NATS TLS disabled and services restarted.")
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    disable_nats_tls(host, user, password)
