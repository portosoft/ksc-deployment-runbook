#!/bin/bash
set -x

echo "=== LIMPEZA DE RPM QUEBRADOS ==="
# Remove os pacotes ignorando os scripts
rpm -e --noscripts ksc64 klnagent64 ksc-web-console 2>/dev/null || true

echo "=== INSTALACAO DO PACOTE ==="
yum install -y /home/suporte/ksc64-16.2.0-1023.x86_64.rpm

echo "=== PREPARANDO POSTINSTALL ==="
cat > /tmp/ksc_response.txt << 'EOF'
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
    echo "Executando postinstall..."
    /opt/kaspersky/ksc64/lib/bin/setup/postinstall.pl --auto-install=/tmp/ksc_response.txt
else
    echo "ERRO: postinstall.pl nao encontrado!"
fi

echo "=== ATIVANDO SERVICOS ==="
systemctl daemon-reload
systemctl enable kladminserver_srv kliam_srv
systemctl restart kladminserver_srv
sleep 30
systemctl restart kliam_srv
sleep 15
systemctl status kliam_srv --no-pager

echo "=== VERIFICANDO IAM ==="
ls -la /var/opt/kaspersky/klnagent_srv/iam || true
