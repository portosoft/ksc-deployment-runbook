import paramiko
import os
import sys

def generate_dummy_certs(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        target_dir = '/var/opt/kaspersky/ksc-web-console'
        print(f"--- Generating dummy certs in {target_dir} ---")

        # Generate Root CA
        cmd = f'sudo openssl genrsa -out {target_dir}/KLRootCA.key 2048 && ' \
              f'sudo openssl req -x509 -new -nodes -key {target_dir}/KLRootCA.key -sha256 -days 1024 -out {target_dir}/KLRootCA.crt -subj "/CN=KSC-Root-CA"'
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + '\n')
        stdin.flush()
        stdout.read()

        # Generate Server Key and Cert
        cmd = f'sudo openssl genrsa -out {target_dir}/web-server.key 2048 && ' \
              f'sudo openssl req -new -key {target_dir}/web-server.key -out {target_dir}/web-server.csr -subj "/CN=kscserver.tail8b9ae.ts.net" && ' \
              f'sudo openssl x509 -req -in {target_dir}/web-server.csr -CA {target_dir}/KLRootCA.crt -CAkey {target_dir}/KLRootCA.key -CAcreateserial -out {target_dir}/web-server.crt -days 500 -sha256'
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + '\n')
        stdin.flush()
        stdout.read()

        # Permissions
        client.exec_command(f'sudo chown root:root {target_dir}/web-server.* {target_dir}/KLRootCA.*')
        client.exec_command(f'sudo chmod 644 {target_dir}/web-server.* {target_dir}/KLRootCA.*')

        # Verify
        stdin, stdout, stderr = client.exec_command(f'ls -l {target_dir}/*.crt {target_dir}/*.key')
        print(stdout.read().decode('utf-8'))

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    generate_dummy_certs(host, user, password)
