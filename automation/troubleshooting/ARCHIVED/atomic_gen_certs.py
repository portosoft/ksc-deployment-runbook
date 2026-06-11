import paramiko
import os
import sys


def atomic_gen_certs(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        target_dir = "/var/opt/kaspersky/ksc-web-console"
        print(f"--- Atomic cert generation in {target_dir} ---")

        # All in one command chain to ensure consistency
        cmd = (
            f'echo "{password}" | sudo -S bash -c "'
            f"openssl genrsa -out {target_dir}/web-server.key 2048 && "
            f'openssl req -new -key {target_dir}/web-server.key -out {target_dir}/web-server.csr -subj \\"/CN=kscserver.tail8b9ae.ts.net\\" && '
            f"openssl x509 -req -in {target_dir}/web-server.csr -CA {target_dir}/KLRootCA.crt -CAkey {target_dir}/KLRootCA.key -CAcreateserial -out {target_dir}/web-server.crt -days 500 -sha256 && "
            f"chown root:root {target_dir}/web-server.* && "
            f'chmod 644 {target_dir}/web-server.*"'
        )

        stdin, stdout, stderr = client.exec_command(cmd)
        print(f"STDOUT: {stdout.read().decode()}")
        print(f"STDERR: {stderr.read().decode()}")

        # Verify modulus match
        print("--- Verifying modulus match ---")
        cmd_key = (
            f"openssl rsa -noout -modulus -in {target_dir}/web-server.key | openssl md5"
        )
        cmd_crt = f"openssl x509 -noout -modulus -in {target_dir}/web-server.crt | openssl md5"

        _, out1, _ = client.exec_command(cmd_key)
        _, out2, _ = client.exec_command(cmd_crt)

        mod1 = out1.read().decode().strip()
        mod2 = out2.read().decode().strip()

        print(f"Key Modulus: {mod1}")
        print(f"Crt Modulus: {mod2}")

        if mod1 == mod2:
            print("MATCH SUCCESSFUL!")
        else:
            print("MATCH FAILED!")

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    atomic_gen_certs(host, user, password)
