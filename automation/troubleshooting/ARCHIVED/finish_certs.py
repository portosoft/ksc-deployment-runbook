import paramiko
import os
import sys


def finish_certs(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        target_dir = "/var/opt/kaspersky/ksc-web-console"
        print(f"--- Finishing cert generation in {target_dir} ---")

        # Step 3: Generate Server Key
        cmd = f'echo "{password}" | sudo -S openssl genrsa -out {target_dir}/web-server.key 2048'
        client.exec_command(cmd)

        # Step 4: Generate CSR
        cmd = f'echo "{password}" | sudo -S openssl req -new -key {target_dir}/web-server.key -out {target_dir}/web-server.csr -subj "/CN=kscserver.tail8b9ae.ts.net"'
        client.exec_command(cmd)

        # Step 5: Sign with Root CA
        cmd = f'echo "{password}" | sudo -S openssl x509 -req -in {target_dir}/web-server.csr -CA {target_dir}/KLRootCA.crt -CAkey {target_dir}/KLRootCA.key -CAcreateserial -out {target_dir}/web-server.crt -days 500 -sha256'
        client.exec_command(cmd)

        # Step 6: Cleanup and Permissions
        client.exec_command(
            f'echo "{password}" | sudo -S rm {target_dir}/web-server.csr {target_dir}/KLRootCA.srl'
        )
        client.exec_command(
            f'echo "{password}" | sudo -S chown root:root {target_dir}/web-server.* {target_dir}/KLRootCA.*'
        )
        client.exec_command(
            f'echo "{password}" | sudo -S chmod 644 {target_dir}/web-server.* {target_dir}/KLRootCA.*'
        )

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

    finish_certs(host, user, password)
