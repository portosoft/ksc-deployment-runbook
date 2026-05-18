#!/bin/bash
set -x

echo "=== CRIANDO BANCO KSCIAM ==="
sudo -u postgres psql << 'SQL'
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'ksciam' AND pid <> pg_backend_pid();
DROP DATABASE IF EXISTS ksciam;
CREATE DATABASE ksciam OWNER kluser ENCODING 'UTF8' LC_COLLATE 'pt_BR.UTF-8' LC_CTYPE 'pt_BR.UTF-8';
SQL

echo "=== INJETANDO IAM YAML ==="
sudo mkdir -p /var/opt/kaspersky/klnagent_srv/iam
sudo mv /tmp/iam_config.yaml /var/opt/kaspersky/klnagent_srv/iam/iam_config.yaml
sudo chown ksc:kladmins /var/opt/kaspersky/klnagent_srv/iam/iam_config.yaml
sudo chmod 640 /var/opt/kaspersky/klnagent_srv/iam/iam_config.yaml

echo "=== REINICIANDO IAM ==="
sudo systemctl restart kliam_srv
sleep 15
sudo systemctl status kliam_srv --no-pager
sudo journalctl -u kliam_srv -n 50 --no-pager
