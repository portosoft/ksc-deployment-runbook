import paramiko
import os
import sys


def force_sign_cert(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        target_dir = "/var/opt/kaspersky/ksc-web-console"
        print(f"--- Force signing cert in {target_dir} ---")

        # Ensure Key
        client.exec_command(
            f'echo "{password}" | sudo -S openssl genrsa -out {target_dir}/web-server.key 2048'
        )

        # Ensure CSR
        cmd = f'echo "{password}" | sudo -S openssl req -new -key {target_dir}/web-server.key -out {target_dir}/web-server.csr -subj "/CN=kscserver.tail8b9ae.ts.net"'
        stdin, stdout, stderr = client.exec_command(cmd)
        print(f"CSR stderr: {stderr.read().decode()}")

        # Sign
        cmd = f'echo "{password}" | sudo -S openssl x509 -req -in {target_dir}/web-server.csr -CA {target_dir}/KLRootCA.crt -CAkey {target_dir}/KLRootCA.key -CAcreateserial -out {target_dir}/web-server.crt -days 500 -sha256'
        stdin, stdout, stderr = client.exec_command(cmd)
        print(f"Sign stderr: {stderr.read().decode()}")

        # Verify
        stdin, stdout, stderr = client.exec_command(
            f"ls -l {target_dir}/*.crt {target_dir}/*.key"
        )
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    force_sign_cert(host, user, password)
