import paramiko
import os
import sys


def enable_nats_tls(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        target_dir = "/var/opt/kaspersky/ksc-web-console"
        print(f"--- Re-enabling TLS in {target_dir}/nats.conf ---")

        conf_content = """port: 8222
tls {
  cert_file: "./nats-server.crt"
  key_file: "./nats-server.key"
  ca_file: "./KLRootCA.crt"
  verify: false
  timeout: 2
}
"""
        sftp = client.open_sftp()
        with sftp.file("/tmp/nats.conf", "w") as f:
            f.write(conf_content)
        sftp.close()

        client.exec_command(
            f'echo "{password}" | sudo -S mv /tmp/nats.conf {target_dir}/nats.conf'
        )

        # Restore pm.config.js TLS lines
        print(f"--- Re-enabling NATS TLS in pm.config.js ---")
        stdin, stdout, stderr = client.exec_command(f"cat {target_dir}/pm.config.js")
        pm_content = stdout.read().decode("utf-8")

        new_pm = (
            pm_content.replace("// NATS_TLS_KEYFILE:", "NATS_TLS_KEYFILE:")
            .replace("// NATS_TLS_CERTFILE:", "NATS_TLS_CERTFILE:")
            .replace("// NATS_TLS_CAFILE:", "NATS_TLS_CAFILE:")
        )

        sftp = client.open_sftp()
        with sftp.file("/tmp/pm.config.js", "w") as f:
            f.write(new_pm)
        sftp.close()

        client.exec_command(
            f'echo "{password}" | sudo -S mv /tmp/pm.config.js {target_dir}/pm.config.js'
        )

        # Force kill everything and restart
        print("--- Restarting all services ---")
        client.exec_command(
            f'echo "{password}" | sudo -S systemctl restart ksc-nats.service'
        )
        client.exec_command(f'echo "{password}" | sudo -S pkill -9 -f node')
        client.exec_command(
            f'echo "{password}" | sudo -S systemctl restart ksc-web-console.service'
        )

        print("NATS TLS re-enabled and services restarted.")
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    enable_nats_tls(host, user, password)
