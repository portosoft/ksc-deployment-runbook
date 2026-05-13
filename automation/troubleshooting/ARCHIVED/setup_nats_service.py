import paramiko
import os
import sys

def setup_nats_service(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        target_dir = '/var/opt/kaspersky/ksc-web-console'
        nats_bin = f'{target_dir}/vendor/nats-server'
        unit_file = '/etc/systemd/system/ksc-nats.service'

        print(f"--- Creating {unit_file} ---")

        unit_content = f"""[Unit]
Description=NATS Server for KSC Web Console
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={target_dir}
ExecStart={nats_bin} -p 8222 --tls --tlscert {target_dir}/nats-server.crt --tlskey {target_dir}/nats-server.key --tlsca {target_dir}/KLRootCA.crt
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
        sftp = client.open_sftp()
        with sftp.file('/tmp/ksc-nats.service', 'w') as f:
            f.write(unit_content)
        sftp.close()

        cmd = f'echo "{password}" | sudo -S mv /tmp/ksc-nats.service {unit_file} && ' \
              f'echo "{password}" | sudo -S systemctl daemon-reload && ' \
              f'echo "{password}" | sudo -S systemctl enable ksc-nats.service && ' \
              f'echo "{password}" | sudo -S systemctl restart ksc-nats.service'

        stdin, stdout, stderr = client.exec_command(cmd)
        print(f"STDOUT: {stdout.read().decode()}")
        print(f"STDERR: {stderr.read().decode()}")

        # Verify port
        client.exec_command(f'sudo -S ss -tulpn | grep 8222')
        # We'll check output in next step

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    setup_nats_service(host, user, password)
