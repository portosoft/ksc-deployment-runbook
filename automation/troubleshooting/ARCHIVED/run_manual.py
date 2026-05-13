import paramiko
import os
import sys

def run_manual(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Stop the service first
        client.exec_command(f'echo "{password}" | sudo -S systemctl stop ksc-web-console.service')
        client.exec_command(f'echo "{password}" | sudo -S pkill -9 -f node')

        target_dir = '/var/opt/kaspersky/ksc-web-console'

        # Build the command with ENV vars
        env_vars = {
            "NODE_ENV": "production",
            "NATS_ADDRESS": "127.0.0.1",
            "NATS_PORT": "8222",
            "NATS_TLS_KEYFILE": f"{target_dir}/nats-server.key",
            "NATS_TLS_CERTFILE": f"{target_dir}/nats-server.crt",
            "NATS_TLS_CAFILE": f"{target_dir}/KLRootCA.crt",
            "logsDir": "logs",
            "verboseOutput": "true"
        }

        env_str = " ".join([f"{k}={v}" for k, v in env_vars.items()])

        # Run node index.js manually for 30 seconds and capture everything
        cmd = f'cd {target_dir} && sudo -S {env_str} ./node ./index.js'
        print(f"Running manual command: {cmd}")

        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + '\n')
        stdin.flush()

        # Wait and read
        import time
        time.sleep(20)

        # Check if still running
        out = stdout.read().decode('utf-8', errors='ignore')
        err = stderr.read().decode('utf-8', errors='ignore')

        print("--- STDOUT ---")
        print(out)
        print("--- STDERR ---")
        print(err)

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    run_manual(host, user, password)
