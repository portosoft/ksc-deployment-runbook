#!/bin/bash
set -x

echo "=== PREPARANDO EVIDENCIAS ==="
mkdir -p /root/ksc_recovery_evidence/{logs,configs}

systemctl status klserver.service klnagent.service kliam_srv.service > /root/ksc_recovery_evidence/logs/systemd_status.txt || true
journalctl -u klserver.service -u klnagent.service -u kliam_srv.service -n 500 --no-pager > /root/ksc_recovery_evidence/logs/journal_ksc.txt || true

cp -a /etc/opt/kaspersky /root/ksc_recovery_evidence/configs/etc_opt_kaspersky 2>/dev/null || true
cp -a /var/opt/kaspersky /root/ksc_recovery_evidence/configs/var_opt_kaspersky 2>/dev/null || true

echo "=== DESINSTALANDO PACOTES ==="
systemctl stop klserver kliam_srv klnagent KSCWebConsole KSCSvcWebConsole || true

# Remover os pacotes rpm listados do kaspersky
rpm -qa | grep -i kaspersky | xargs -r yum remove -y

echo "=== LIMPEZA DE BANCO DE DADOS ==="
sudo -u postgres psql << 'SQL'
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname IN ('ksc', 'ksciam') AND pid <> pg_backend_pid();
DROP DATABASE IF EXISTS ksciam;
DROP DATABASE IF EXISTS ksc;
SQL

echo "=== LIMPEZA DE DIRETORIOS ==="
DATE_STR=$(date +%Y%m%d_%H%M)
mv /var/opt/kaspersky /var/opt/kaspersky.broken-"$DATE_STR" 2>/dev/null || true
mv /etc/opt/kaspersky /etc/opt/kaspersky.broken-"$DATE_STR" 2>/dev/null || true
rm -rf /opt/kaspersky 2>/dev/null || true

echo "DESINSTALACAO CONCLUIDA"
