#!/bin/bash
# Script de Coleta de Auditoria KSC (Somente Leitura)
# Portosoft DevOps Team

set -uo pipefail

echo "=== INICIANDO COLETA DE AUDITORIA KSC ==="
echo "Data: $(date)"
echo "Host: $(hostname)"

echo -e "\n[1] Verificando Pacotes RPM..."
rpm -qa | grep -Ei 'kaspersky|ksc|postgres'

echo -e "\n[2] Verificando Diretórios Críticos..."
ls -ld /opt/kaspersky /var/opt/kaspersky /etc/opt/kaspersky 2>/dev/null || echo "Diretórios base não encontrados."

echo -e "\n[3] Verificando Processos Ativos..."
pgrep -a -f 'kladminserver|klwebsrv|kliam|postgres'

echo -e "\n[4] Verificando Portas (ss)..."
ss -tlnp | grep -E '13000|13001|8443|5432|4222'

echo -e "\n[5] Verificando Firewall..."
firewall-cmd --list-ports

echo -e "\n[6] Verificando PostgreSQL (Strings)..."
sudo -u postgres psql -t -c "SHOW standard_conforming_strings;" || echo "Falha ao acessar PostgreSQL."

echo -e "\n[7] Verificando Bancos de Dados..."
sudo -u postgres psql -c "\l" | grep -E 'ksc|iam' || echo "Bancos KSC não encontrados."

echo -e "\n=== FIM DA COLETA ==="
