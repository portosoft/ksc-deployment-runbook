import paramiko
import os
import sys
import time
import re


def run_manual_streaming_safe(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        target_dir = "/var/opt/kaspersky/ksc-web-console"
        env_vars = {
            "NODE_ENV": "production",
            "NATS_ADDRESS": "127.0.0.1",
            "NATS_PORT": "8222",
            "FEATURE_MESSAGE_BROKER_TYPE": "nats",
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

        time.sleep(1)
        if channel.send_ready():
            channel.send(password + "\n")

        start_time = time.time()
        while time.time() - start_time < 60:
            if channel.recv_ready():
                raw_data = channel.recv(4096)
                # Decode and strip non-ascii
                text = raw_data.decode("utf-8", errors="ignore")
                safe_text = "".join([c if ord(c) < 128 else "?" for c in text])
                sys.stdout.write(safe_text)
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

    run_manual_streaming_safe(host, user, password)
