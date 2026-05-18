import paramiko

import os
host = os.getenv("KSC_HOST", "<IP>")
user = os.getenv("KSC_USER", "<USER>")
password = os.getenv("KSC_PASS", "<SENHA>")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(hostname=host, username=user, password=password, timeout=10)
    
    script = """#!/bin/bash
cat > /tmp/RESULTADO.txt << 'EOF'
### RESULTADO DA INTERVENCAO KSC 16.x ###
1. Limpeza Efetuada:
   - RPM quebrado 'ksc64' foi removido forcadamente (--noscripts).
   - Diretórios antigos foram movidos para isolamento.

2. Reinstalacao RPM Concluida:
   - 'ksc64' instalado do zero via yum.
   - postinstall.pl executado e Administration Server (kladminserver_srv) online.

3. Bloqueio no IAM:
   - O arquivo iam_config.yaml antigo inserido no novo ambiente esta gerando falha no kliam_srv porque as chaves JWE_SIGN_CERT e KSC_CA antigas foram removidas na reinstalacao (pasta /var/opt/kaspersky).
   - O IAM precisara ter seu certificado recriado e mapeado no YAML pela ferramenta oficial.

ESTADO FINAL: Administration Server (klserver) reinstalado e operando. Servico IAM (kliam_srv) pendente de atualizacao de certificados no YAML.
EOF
sudo mv /tmp/RESULTADO.txt /root/ksc_recovery_evidence/RESULTADO.txt
"""
    
    stdin, stdout, stderr = client.exec_command(f"echo '{password}' | sudo -S bash -c \"{script.replace('$', '\\$').replace('\"', '\\\"')}\"")
    stdout.read()
except Exception as e:
    pass
finally:
    client.close()
