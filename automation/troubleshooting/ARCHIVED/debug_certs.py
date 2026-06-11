import paramiko
import os
import sys


def debug_generate_certs(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        target_dir = "/var/opt/kaspersky/ksc-web-console"
        print(f"--- Debugging cert generation in {target_dir} ---")

        # Step 1: Generate Root Key
        cmd = f'echo "{password}" | sudo -S openssl genrsa -out {target_dir}/KLRootCA.key 2048'
        stdin, stdout, stderr = client.exec_command(cmd)
        print(f"Step 1 STDOUT: {stdout.read().decode()}")
        print(f"Step 1 STDERR: {stderr.read().decode()}")

        # Step 2: Generate Root Cert
        cmd = f'echo "{password}" | sudo -S openssl req -x509 -new -nodes -key {target_dir}/KLRootCA.key -sha256 -days 1024 -out {target_dir}/KLRootCA.crt -subj "/CN=KSC-Root-CA"'
        stdin, stdout, stderr = client.exec_command(cmd)
        print(f"Step 2 STDOUT: {stdout.read().decode()}")
        print(f"Step 2 STDERR: {stderr.read().decode()}")

        # Check files
        stdin, stdout, stderr = client.exec_command(f"ls -l {target_dir}/KLRootCA.*")
        print(f"Files after step 2: {stdout.read().decode()}")

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    debug_generate_certs(host, user, password)
