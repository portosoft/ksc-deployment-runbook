import paramiko
import os
import sys


def fix_iam_yaml(host, user, password, iam_pass):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        iam_config = "/var/opt/kaspersky/klnagent_srv/iam/iam_config.yaml"
        print(f"--- Fixing {iam_config} ---")

        # Define the CORRECT content
        content = f"""version: 1
metadata:
  name: "iam settings"
server_iam:
    iam_address: "kscserver.tail8b9ae.ts.net"
    server_display_name: "kscserver.tail8b9ae.ts.net"
    ksc_address: "127.0.0.1"
    ksc_ca: "/var/opt/kaspersky/klnagent_srv/1093/cert/klserver.cer"
dbms_iam:
    dbms_main:
        dbms_type: "POSTGRES"
        dbms_address: "127.0.0.1"
        dbms_port: "5432"
        dbms_db: "ksciam"
        dbms_user: "kluser"
        dbms_userpassword: "{iam_pass}"
        dbms_schema: ""
    dbms_tls:
        dbms_tl_opt_ssl_ca: ""
        dbms_tl_opt_ssl_verify_server_cn: ""
        dbms_tl_opt_ssl_cert: ""
        dbms_tl_opt_ssl_key: ""
        dbms_tl_opt_tls_pasphrase: ""
        dbms_tl_opt_ssl_cipher: ""
        dbms_tl_opt_ssl_tlsver_min: ""
        dbms_tl_opt_ssl_tlsver_max: ""
certificates_iam:
      jwe_sign_privkey: "/var/opt/kaspersky/klnagent_srv/1093/iam/klsrvJWEsign.prk"
      jwe_sign_cert: "/var/opt/kaspersky/klnagent_srv/1093/cert/klsrvJWEsign.cer"
      jwe_encrypt_cert:  "/var/opt/kaspersky/klnagent_srv/1093/iam/klsrvJWEencrypt.cer"
"""

        sftp = client.open_sftp()
        with sftp.file("/tmp/iam_config.yaml", "w") as f:
            f.write(content)
        sftp.close()

        client.exec_command(
            f'echo "{password}" | sudo -S mv /tmp/iam_config.yaml {iam_config}'
        )

        print("--- Restarting kliam_srv.service ---")
        client.exec_command(
            f'echo "{password}" | sudo -S systemctl restart kliam_srv.service'
        )

        print("--- Restarting ksc-web-console.service ---")
        client.exec_command(
            f'echo "{password}" | sudo -S systemctl restart ksc-web-console.service'
        )

        client.close()
        print("IAM YAML fixed and services restarted.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")
    iam_pass = "SENHA_AQUI"

    fix_iam_yaml(host, user, password, iam_pass)
