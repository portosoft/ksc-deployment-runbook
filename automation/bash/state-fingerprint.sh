#!/bin/bash
# shellcheck shell=bash
# =============================================================================
# Impressão determinística do estado do host (somente leitura)
#
# Produz uma saída estável e ordenada, própria para `diff` entre execuções.
# Serve para verificar idempotência: rodar `setup --apply` duas vezes deve
# deixar a mesma impressão, exceto pelos campos declarados como voláteis.
#
# Uso:
#   sudo automation/bash/state-fingerprint.sh > antes.txt
#   sudo kscctl setup --apply
#   sudo automation/bash/state-fingerprint.sh > depois.txt
#   diff antes.txt depois.txt
# =============================================================================
set -uo pipefail

echo "## pacotes"
rpm -qa --qf '%{NAME} %{VERSION}-%{RELEASE}\n' 2>/dev/null \
  | grep -Ei 'ksc|klnagent|postgresql' | sort

echo
echo "## unidades systemd"
for unit in $(systemctl list-unit-files --no-legend 2>/dev/null \
                | grep -iE '^(kl|ksc|postgresql)' | awk '{print $1}' | sort); do
  printf '%s enabled=%s active=%s\n' \
    "$unit" \
    "$(systemctl is-enabled "$unit" 2>/dev/null)" \
    "$(systemctl is-active "$unit" 2>/dev/null)"
done

echo
echo "## portas em escuta"
ss -tlnH 2>/dev/null | awk '{print $4}' | sed 's/.*://' | sort -n -u

echo
echo "## contas de sistema"
getent passwd ksc 2>/dev/null | cut -d: -f1,3,4
getent group kladmins 2>/dev/null | cut -d: -f1,3

echo
echo "## bases e roles"
runuser -u postgres -- psql -tAc \
  "SELECT datname FROM pg_database WHERE datname NOT LIKE 'template%' ORDER BY 1" 2>/dev/null
runuser -u postgres -- psql -tAc \
  "SELECT rolname FROM pg_roles WHERE rolname NOT LIKE 'pg_%' ORDER BY 1" 2>/dev/null

echo
echo "## permissões dos diretórios do produto"
for path in /opt/kaspersky /opt/kaspersky/ksc64 /opt/kaspersky/ksc64/sbin \
            /var/opt/kaspersky /var/opt/kaspersky/ksc-web-console; do
  [ -e "$path" ] && stat -c '%n %a %U:%G' "$path" 2>/dev/null
done

echo
echo "## arquivos de configuração (hash do conteúdo)"
for file in /etc/ksc-web-console-setup.json \
            /etc/systemd/system/kladminserver_srv.service.d/10-ld-library-path.conf \
            /etc/systemd/system/KSCWebConsole.service.d/10-bind-privileged-port.conf; do
  [ -f "$file" ] && printf '%s %s\n' "$file" "$(sha256sum "$file" | cut -c1-16)"
done

echo
echo "## certificado do Web Console"
# A regeneração do certificado a cada execução é o sintoma mais visível de
# falta de idempotência: invalida a confiança de qualquer cliente que já o
# tenha aceitado.
if [ -f /var/opt/kaspersky/ksc-web-console/server/certificate.crt ]; then
  openssl x509 -in /var/opt/kaspersky/ksc-web-console/server/certificate.crt \
    -noout -fingerprint -sha256 2>/dev/null | cut -d= -f2
else
  cert="$(find /var/opt/kaspersky/ksc-web-console -maxdepth 3 -name '*.crt' 2>/dev/null | sort | head -1)"
  if [ -n "$cert" ]; then
    printf '%s ' "$cert"
    openssl x509 -in "$cert" -noout -fingerprint -sha256 2>/dev/null | cut -d= -f2
  else
    echo "(certificado não localizado)"
  fi
fi
