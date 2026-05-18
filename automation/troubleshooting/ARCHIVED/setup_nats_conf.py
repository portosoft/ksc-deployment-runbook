import paramiko
import os
import sys


def setup_nats_conf(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        target_dir = "/var/opt/kaspersky/ksc-web-console"
        print(f"--- Creating {target_dir}/nats.conf ---")

        conf_content = f"""port: 8222
tls {{
    cert_file: "{target_dir}/nats-server.crt"
    key_file:  "{target_dir}/nats-server.key"
    ca_file:   "{target_dir}/KLRootCA.crt"
    verify:    false
}}
"""
        sftp = client.open_sftp()
        with sftp.file("/tmp/nats.conf", "w") as f:
            f.write(conf_content)
        sftp.close()

        # Move and update service
        cmd = (
            f'echo "{password}" | sudo -S mv /tmp/nats.conf {target_dir}/nats.conf && '
            f'echo "{password}" | sudo -S chown root:root {target_dir}/nats.conf'
        )
        client.exec_command(cmd)

        # Update Service unit to use -c
        unit_file = "/etc/systemd/system/ksc-nats.service"
        nats_bin = f"{target_dir}/vendor/nats-server"
        new_unit = f"""[Unit]
Description=NATS Server for KSC Web Console
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={target_dir}
ExecStart={nats_bin} -c {target_dir}/nats.conf
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
        with open("/tmp/ksc-nats.service", "w") as f:
            f.write(new_unit)

        sftp = client.open_sftp()
        sftp.put("/tmp/ksc-nats.service", "/tmp/ksc-nats.service.remote")
        sftp.close()

        cmd = (
            f'echo "{password}" | sudo -S mv /tmp/ksc-nats.service.remote {unit_file} && '
            f'echo "{password}" | sudo -S systemctl daemon-reload && '
            f'echo "{password}" | sudo -S systemctl restart ksc-nats.service'
        )

        stdin, stdout, stderr = client.exec_command(cmd)
        stdout.read()

        print("NATS configured with nats.conf and restarted.")
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    setup_nats_conf(host, user, password)
