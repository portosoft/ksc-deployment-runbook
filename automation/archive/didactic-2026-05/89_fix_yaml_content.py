import paramiko
import os
from dotenv import load_dotenv

load_dotenv("configs/env/ksc_vars.env")
host = os.getenv("KSC_HOST")
user = os.getenv("KSC_USER")
password = os.getenv("KSC_PASS")
db_pass = os.getenv("KSC_DB_PASS")

client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.RejectPolicy())
client.connect(host, username=user, password=password)

print("=" * 60)
print("RECONSTRUINDO iam_config.yaml")
print("=" * 60)

# Estrutura YAML limpa
yaml_content = f"""dbms_iam:
    dbms_main:
        dbms_type: "POSTGRES"
        dbms_address: "127.0.0.1"
        dbms_port: "5432"
        dbms_db: "ksciam"
        dbms_user: "kluser"
        dbms_userpassword: "{db_pass}"
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

# Escapa aspas simples para o comando echo do shell
escaped_content = yaml_content.replace("'", "'\\''")

cmd = f"echo '{escaped_content}' | sudo -S tee /var/opt/kaspersky/klnagent_srv/iam/iam_config.yaml > /dev/null"
stdin, stdout, stderr = client.exec_command(cmd)
stdin.write(password + "\n")
stdin.flush()

print("Arquivo reconstruído com sucesso.")
client.close()
