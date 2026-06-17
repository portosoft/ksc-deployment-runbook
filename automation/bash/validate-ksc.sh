#!/bin/bash
# shellcheck shell=bash
# Script de Validação do Kaspersky Security Center (KSC)
# Portosoft DevOps Team

set -euo pipefail

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "--- Iniciando Validação do KSC ---"

# 1. Verificar Serviços
echo -e "\n[1] Verificando status dos serviços..."
SERVICES=("kladminserver_srv" "klwebsrv_srv" "kliam_srv" "klnagent_srv")

for svc in "${SERVICES[@]}"; do
    if systemctl is-active --quiet "$svc"; then
        echo -e "${GREEN}OK${NC}: $svc está em execução."
    else
        echo -e "${RED}ERRO${NC}: $svc não está rodando."
    fi
done

# 2. Verificar Portas em Escuta
echo -e "\n[2] Verificando portas em escuta (ss)..."
PORTS=("8080" "8443" "13000" "13001")

for port in "${PORTS[@]}"; do
    if grep -q -- ":$port " < <(ss -tlnp); then
        echo -e "${GREEN}OK${NC}: Porta $port está aberta e escutando."
    else
        echo -e "${RED}ERRO${NC}: Porta $port não detectada no ss."
    fi
done

# 3. Verificar Firewall
echo -e "\n[3] Verificando regras de firewall..."
FW_PORTS=$(sudo firewall-cmd --list-ports)
for port in "${PORTS[@]}"; do
    if grep -Eq "(^|[[:space:]])${port}/tcp([[:space:]]|$)" <<<"$FW_PORTS"; then
        echo -e "${GREEN}OK${NC}: Porta $port/tcp liberada no firewalld."
    else
        echo -e "${RED}ERRO${NC}: Porta $port/tcp NÃO encontrada no firewalld."
    fi
done

# 4. Verificar PostgreSQL
echo -e "\n[4] Verificando PostgreSQL (standard_conforming_strings)..."
if command -v psql >/dev/null 2>&1; then
    PG_STATUS=$(sudo -u postgres psql -t -c "SHOW standard_conforming_strings;" | xargs)
    if [[ "$PG_STATUS" == "on" ]]; then
        echo -e "${GREEN}OK${NC}: standard_conforming_strings está ON."
    else
        echo -e "${RED}ERRO${NC}: standard_conforming_strings está $PG_STATUS (deveria ser ON)."
    fi
else
    echo -e "${RED}AVISO${NC}: psql não encontrado. Pulei validação de DB."
fi

echo -e "\n--- Validação Concluída ---"
