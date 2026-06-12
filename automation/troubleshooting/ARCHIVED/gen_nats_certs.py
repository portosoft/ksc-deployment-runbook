import paramiko
import os
import sys


def gen_nats_certs(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        target_dir = "/var/opt/kaspersky/ksc-web-console"
        print(f"--- Generating NATS certs in {target_dir} ---")

        # All in one command chain
        cmd = (
            f'echo "{password}" | sudo -S bash -c "'
            f"openssl genrsa -out {target_dir}/nats-server.key 2048 && "
            f'openssl req -new -key {target_dir}/nats-server.key -out {target_dir}/nats-server.csr -subj \\"/CN=127.0.0.1\\" && '
            f"openssl x509 -req -in {target_dir}/nats-server.csr -CA {target_dir}/KLRootCA.crt -CAkey {target_dir}/KLRootCA.key -CAcreateserial -out {target_dir}/nats-server.crt -days 1000 -sha256 && "
            f"chown root:root {target_dir}/nats-server.* && "
            f"chmod 644 {target_dir}/nats-server.* && "
            f'rm {target_dir}/nats-server.csr"'
        )

        stdin, stdout, stderr = client.exec_command(cmd)
        print(f"STDOUT: {stdout.read().decode()}")
        print(f"STDERR: {stderr.read().decode()}")

        # Verify
        stdin, stdout, stderr = client.exec_command(f"ls -l {target_dir}/nats-server.*")
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    gen_nats_certs(host, user, password)
