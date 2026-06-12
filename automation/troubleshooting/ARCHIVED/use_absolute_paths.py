import paramiko
import os
import sys


def use_absolute_paths(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        target_dir = "/var/opt/kaspersky/ksc-web-console"
        print(f"--- Updating {target_dir}/pm.config.js with absolute paths ---")

        stdin, stdout, stderr = client.exec_command(f"cat {target_dir}/pm.config.js")
        pm_content = stdout.read().decode("utf-8")

        new_pm = (
            pm_content.replace("'./nats-server.key'", f"'{target_dir}/nats-server.key'")
            .replace("'./nats-server.crt'", f"'{target_dir}/nats-server.crt'")
            .replace("'./KLRootCA.crt'", f"'{target_dir}/KLRootCA.crt'")
        )

        sftp = client.open_sftp()
        with sftp.file("/tmp/pm.config.js", "w") as f:
            f.write(new_pm)
        sftp.close()

        client.exec_command(
            f'echo "{password}" | sudo -S mv /tmp/pm.config.js {target_dir}/pm.config.js'
        )

        # Restart all
        print("--- Restarting all services ---")
        client.exec_command(f'echo "{password}" | sudo -S pkill -9 -f node')
        client.exec_command(
            f'echo "{password}" | sudo -S systemctl restart ksc-web-console.service'
        )

        client.close()
        print("Paths updated and services restarted.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    use_absolute_paths(host, user, password)
