import paramiko
import os
from dotenv import load_dotenv

load_dotenv("configs/env/ksc_vars.env")
host = os.getenv("KSC_HOST")
user = os.getenv("KSC_USER")
password = os.getenv("KSC_PASS")
db_pass = os.getenv("KSC_DB_PASS")

# 1. Gerar arquivo localmente
local_path = "scratch/iam_config.yaml"
yaml_content = f"""ksc_iam:
    ksc_address: "127.0.0.1"
    ksc_ca: "/var/opt/kaspersky/klnagent_srv/1093/cert/klserver.cer"
dbms_iam:
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

with open(local_path, "w") as f:
    f.write(yaml_content)

# 2. Conectar e Upload
transport = paramiko.Transport((host, 22))
transport.connect(username=user, password=password)
sftp = paramiko.SFTPClient.from_transport(transport)

# Sobe para um local temporário
remote_tmp = "/tmp/iam_config.yaml"
sftp.put(local_path, remote_tmp)
sftp.close()
transport.close()

# 3. Mover para o local definitivo via sudo
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
client.connect(host, username=user, password=password)

print("Movendo arquivo para /var/opt/kaspersky/klnagent_srv/iam/...")
cmd = "sudo -S mv /tmp/iam_config.yaml /var/opt/kaspersky/klnagent_srv/iam/iam_config.yaml"
stdin, stdout, stderr = client.exec_command(cmd)
stdin.write(password + "\n")
stdin.flush()

print("Processo concluído.")
client.close()
