#!/bin/bash
# shellcheck shell=bash
# Script de Coleta de Auditoria KSC (Somente Leitura)
# KSC Runbook Community

set -euo pipefail

echo "=== INICIANDO COLETA DE AUDITORIA KSC ==="
echo "Data: $(date)"
echo "Host: $(hostname)"

echo -e "\n[1] Verificando Pacotes RPM..."
if ! grep -Ei 'kaspersky|ksc|postgres' < <(rpm -qa); then
    echo "Pacotes KSC/PostgreSQL nao encontrados."
fi

echo -e "\n[2] Verificando Diretórios Críticos..."
ls -ld /opt/kaspersky /var/opt/kaspersky /etc/opt/kaspersky 2>/dev/null || echo "Diretórios base não encontrados."

echo -e "\n[3] Verificando Processos Ativos..."
pgrep -a -f 'kladminserver|klwebsrv|kliam|postgres'

echo -e "\n[4] Verificando Portas (ss)..."
if ! grep -Eq ':(13000|13001|8443|5432|4222)\b' < <(ss -tlnp); then
    echo "Portas esperadas nao encontradas."
fi

echo -e "\n[5] Verificando Firewall..."
firewall-cmd --list-ports

echo -e "\n[6] Verificando PostgreSQL (Strings)..."
sudo -u postgres psql -t -c "SHOW standard_conforming_strings;" || echo "Falha ao acessar PostgreSQL."

echo -e "\n[7] Verificando Bancos de Dados..."
if ! grep -E 'ksc|iam' < <(sudo -u postgres psql -c "\l"); then
    echo "Bancos KSC nao encontrados."
fi

echo -e "\n=== FIM DA COLETA ==="
