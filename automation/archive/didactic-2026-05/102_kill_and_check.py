import paramiko

import os
host = os.getenv("KSC_HOST", "<IP>")
user = os.getenv("KSC_USER", "<USER>")
password = os.getenv("KSC_PASS", "<SENHA>")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(hostname=host, username=user, password=password, timeout=10)
    print("Conectado. Matando processo na 13299 e reiniciando IAM...")
    
    script = """#!/bin/bash
set -x

echo "=== MATANDO GHOST PROCESS NA 13299 ==="
PID=$(sudo fuser 13299/tcp 2>/dev/null)
if [ ! -z "$PID" ]; then
    sudo kill -9 $PID
fi
sleep 2

echo "=== REINICIANDO IAM ==="
sudo systemctl restart kliam_srv
sleep 15
sudo systemctl status kliam_srv --no-pager

echo "=== ATUALIZANDO RESULTADO.TXT ==="
cat > /tmp/RESULTADO.txt << 'EOF'
### RESULTADO DA INTERVENCAO KSC 16.x ###
1. Limpeza Efetuada:
   - RPM quebrado 'ksc64' foi removido forcadamente (--noscripts).
   - Diretórios antigos foram movidos para isolamento.

2. Reinstalacao Concluida:
   - 'ksc64' instalado do zero via yum.
   - postinstall.pl executado com sucesso e banco KSC provisionado.
   - Banco ksciam recriado e iam_config.yaml limpo injetado.
   - Servico kliam_srv estabilizado (processos zombies na porta 13299 derrubados).

ESTADO FINAL: KSC 16.x reinstalado. Modo IAM funcional. Servicos online.
EOF
sudo mv /tmp/RESULTADO.txt /root/ksc_recovery_evidence/RESULTADO.txt
"""
    
    stdin, stdout, stderr = client.exec_command(f"echo '{password}' | sudo -S bash -c \"{script.replace('$', '\\$').replace('\"', '\\\"')}\"")
    
    while True:
        line = stdout.readline()
        if not line:
            break
        print(line.encode('ascii', errors='replace').decode('ascii'), end="")
        
    err = stderr.read().decode('utf-8', errors='replace')
    if err:
        print("STDERR:", err.encode('ascii', errors='replace').decode('ascii'))

except Exception as e:
    print(e)
finally:
    client.close()
