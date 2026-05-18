#!/bin/bash
set -x
sudo yum reinstall -y /home/suporte/ksc64-16.2.0-1023.x86_64.rpm

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
    sudo /opt/kaspersky/ksc64/lib/bin/setup/postinstall.pl --auto-install=/tmp/ksc_response.txt
    sudo systemctl daemon-reload
    sudo systemctl enable kladminserver_srv kliam_srv
    sudo systemctl restart kladminserver_srv
    sleep 30
    sudo systemctl restart kliam_srv
    sleep 15
    sudo systemctl status kliam_srv --no-pager
    sudo ls -la /var/opt/kaspersky/klnagent_srv/iam
else
    echo "ERRO: postinstall.pl nao encontrado apos reinstall!"
fi
