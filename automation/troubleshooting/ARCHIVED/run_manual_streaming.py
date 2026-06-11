import paramiko
import os
import sys
import time


def run_manual_streaming(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Stop everything first
        client.exec_command(
            f'echo "{password}" | sudo -S systemctl stop ksc-web-console.service'
        )
        client.exec_command(f'echo "{password}" | sudo -S pkill -9 -f node')

        target_dir = "/var/opt/kaspersky/ksc-web-console"
        env_vars = {
            "NODE_ENV": "production",
            "NATS_ADDRESS": "127.0.0.1",
            "NATS_PORT": "8222",
            "NATS_TLS_KEYFILE": f"{target_dir}/nats-server.key",
            "NATS_TLS_CERTFILE": f"{target_dir}/nats-server.crt",
            "NATS_TLS_CAFILE": f"{target_dir}/KLRootCA.crt",
            "logsDir": "logs",
            "verboseOutput": "true",
        }
        env_str = " ".join([f"{k}={v}" for k, v in env_vars.items()])

        cmd = f"cd {target_dir} && sudo -S {env_str} ./node ./index.js"
        print(f"Executing: {cmd}")

        transport = client.get_transport()
        channel = transport.open_session()
        channel.get_pty()
        channel.exec_command(cmd)

        # Send password for sudo
        time.sleep(1)
        if channel.send_ready():
            channel.send(password + "\n")

        # Read output for 60 seconds
        start_time = time.time()
        while time.time() - start_time < 60:
            if channel.recv_ready():
                data = channel.recv(1024).decode("utf-8", errors="ignore")
                sys.stdout.write(data)
                sys.stdout.flush()
            time.sleep(0.1)

        channel.close()
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    run_manual_streaming(host, user, password)
