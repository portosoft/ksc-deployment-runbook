import paramiko
import os
import sys


def set_nats_broker(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        target_dir = "/var/opt/kaspersky/ksc-web-console"
        print(f"--- Updating {target_dir}/pm.config.js to use NATS ---")

        stdin, stdout, stderr = client.exec_command(f"cat {target_dir}/pm.config.js")
        pm_content = stdout.read().decode("utf-8")

        # Add FEATURE_MESSAGE_BROKER_TYPE: 'nats' to env
        if "'FEATURE_MESSAGE_BROKER_TYPE': 'nats'" not in pm_content:
            # Find the last env variable and add it
            new_pm = pm_content.replace(
                "'verboseOutput': true",
                "'verboseOutput': true,\n          'FEATURE_MESSAGE_BROKER_TYPE': 'nats'",
            )
        else:
            new_pm = pm_content

        sftp = client.open_sftp()
        with sftp.file("/tmp/pm.config.js", "w") as f:
            f.write(new_pm)
        sftp.close()

        client.exec_command(
            f'echo "{password}" | sudo -S mv /tmp/pm.config.js {target_dir}/pm.config.js'
        )

        # Force kill and restart
        print("--- Restarting all Node processes ---")
        client.exec_command(f'echo "{password}" | sudo -S pkill -9 -f node')
        client.exec_command(
            f'echo "{password}" | sudo -S systemctl restart ksc-web-console.service'
        )

        client.close()
        print("Broker type set to nats and services restarted.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    set_nats_broker(host, user, password)
