#!/bin/bash
set -x

echo "=== REMOVENDO PACOTES CORRETAMENTE ==="
systemctl stop klserver kliam_srv klnagent KSCWebConsole KSCSvcWebConsole || true

rpm -qa | grep -iE 'ksc64|klnagent|kaspersky' | xargs -r yum remove -y

echo "=== LIMPEZA DE DIRETORIOS ==="
DATE_STR=$(date +%Y%m%d_%H%M)
mv /var/opt/kaspersky /var/opt/kaspersky.broken-v2-"$DATE_STR" 2>/dev/null || true
mv /etc/opt/kaspersky /etc/opt/kaspersky.broken-v2-"$DATE_STR" 2>/dev/null || true
rm -rf /opt/kaspersky 2>/dev/null || true

echo "=== REINSTALANDO ==="
sudo yum install -y /home/suporte/ksc64-16.2.0-1023.x86_64.rpm

echo "=== SETUP POSTINSTALL ==="
# O KSC precisa ser inicializado via script de postinstall
# Verificando as configs que o postinstall exige usando a base oficial
cat > /tmp/ksc_response.txt << 'EOF'
# Respostas silenciosas para o KSC 16
KLSRV_ACCEPT_EULA=1
KLSRV_DB_TYPE=PostgreSQL
KLSRV_DB_HOST=127.0.0.1
KLSRV_DB_PORT=5432
KLSRV_DB_NAME=ksc
KLSRV_DB_USER=kluser
KLSRV_DB_PASSWORD=[REDACTED_DB_PASS]
KLSRV_ADMIN_PASSWORD=[REDACTED_ADMIN_PASS]
EOF

if [ -f /opt/kaspersky/ksc64/lib/bin/setup/postinstall.pl ]; then
    /opt/kaspersky/ksc64/lib/bin/setup/postinstall.pl --auto-install=/tmp/ksc_response.txt
fi

systemctl enable kladminserver_srv kliam_srv || true
systemctl start kladminserver_srv || true
sleep 30
systemctl start kliam_srv || true
sleep 10
