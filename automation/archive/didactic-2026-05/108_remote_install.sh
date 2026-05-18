#!/bin/bash
set -x

echo "=== CRIANDO BANCO DE DADOS ==="
sudo -u postgres psql << 'SQL'
CREATE DATABASE ksc OWNER kluser ENCODING 'UTF8' LC_COLLATE 'pt_BR.UTF-8' LC_CTYPE 'pt_BR.UTF-8';
CREATE DATABASE ksciam OWNER kluser ENCODING 'UTF8' LC_COLLATE 'pt_BR.UTF-8' LC_CTYPE 'pt_BR.UTF-8';
SQL

echo "=== INSTALANDO PACOTE KSC ==="
sudo yum install -y /home/suporte/ksc64-16.2.0-1023.x86_64.rpm

echo "=== CONFIGURANDO KSC ==="
# O KSC fornece um script de postinstall
# /opt/kaspersky/ksc64/lib/bin/setup/postinstall.pl
# Dependendo de como era feito antes, precisamos gerar o ksc_vars.env e o ksc_response.txt
# Ou usar o instalador automatico do runbook se possivel.

# Vamos verificar se o script existe
ls -l /opt/kaspersky/ksc64/lib/bin/setup/postinstall.pl || true

# Configurar autostart e iniciar
systemctl enable kladminserver_srv kliam_srv
systemctl start kladminserver_srv
sleep 30
systemctl start kliam_srv
sleep 10
systemctl status kliam_srv --no-pager
