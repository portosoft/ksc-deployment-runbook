#!/bin/bash
# shellcheck shell=bash
# Script de validação de hardening para Rocky Linux 9 / KSC 16.x
# Somente leitura: não altera configuração do host

set -euo pipefail

failures=0

ok() {
    echo "[OK] $1"
}

err() {
    echo "[ERRO] $1"
    failures=1
}

check_service_disabled() {
    local service=$1
    local enabled_state active_state

    enabled_state=$(systemctl is-enabled "$service" 2>/dev/null || true)
    active_state=$(systemctl is-active "$service" 2>/dev/null || true)

    if [[ "$enabled_state" == "disabled" || "$enabled_state" == "masked" || "$enabled_state" == "not-found" || "$enabled_state" == "static" ]]; then
        if [[ "$active_state" == "inactive" || "$active_state" == "failed" || "$active_state" == "unknown" || "$active_state" == "inactive (dead)" || "$active_state" == "" ]]; then
            ok "Servico $service desabilitado/inativo"
            return
        fi
    fi

    err "Servico $service ainda esta habilitado ou ativo (enabled=$enabled_state, active=$active_state)"
}

check_service_active() {
    local service=$1
    local state

    state=$(systemctl is-active "$service" 2>/dev/null || true)
    if [[ "$state" == "active" ]]; then
        ok "Servico $service ativo"
    else
        err "Servico $service nao esta ativo (state=$state)"
    fi
}

check_services_disabled_group() {
    local services=(avahi-daemon cups postfix rpcbind snmpd)
    for service in "${services[@]}"; do
        check_service_disabled "$service"
    done
}

check_fail2ban_ssh() {
    if fail2ban-client status sshd >/dev/null 2>&1 || fail2ban-client status ssh >/dev/null 2>&1; then
        ok "Fail2Ban ativo para SSH"
    else
        err "Fail2Ban nao possui jail ativa para SSH"
    fi
}

check_pwquality() {
    if grep -Eq '^minlen[[:space:]]*=[[:space:]]*14$' /etc/security/pwquality.conf 2>/dev/null; then
        ok "pwquality com minlen = 14"
    else
        err "pwquality sem minlen = 14 em /etc/security/pwquality.conf"
    fi
}

check_postgres_max_connections() {
    local result
    result=$(sudo -u postgres psql -t -c 'SHOW max_connections;' 2>/dev/null | xargs || true)
    if [[ "$result" == "1000" ]]; then
        ok "PostgreSQL com max_connections = 1000"
    else
        err "PostgreSQL com max_connections diferente de 1000 (valor=$result)"
    fi
}

check_kaspersky_permissions() {
    local mode
    mode=$(stat -c %a /opt/kaspersky 2>/dev/null || true)
    if [[ "$mode" == "750" ]]; then
        ok "/opt/kaspersky com permissao 750"
    else
        err "/opt/kaspersky com permissao inesperada (valor=$mode)"
    fi
}

echo "=== VALIDACAO DE HARDENING KSC ==="

echo "[1] Servicos desnecessarios"
check_services_disabled_group

echo "[2] Servicos de seguranca"
check_service_active nftables
check_service_active auditd
check_fail2ban_ssh

echo "[3] Politica de senhas"
check_pwquality

echo "[4] PostgreSQL hardening"
check_postgres_max_connections

echo "[5] Permissoes do KSC"
check_kaspersky_permissions

if [[ $failures -eq 0 ]]; then
    echo "=== RESULTADO FINAL: TODOS OS CONTROLES VALIDADOS ==="
    exit 0
fi

echo "=== RESULTADO FINAL: HA CONTROLES FALHANDO ==="
exit 1
