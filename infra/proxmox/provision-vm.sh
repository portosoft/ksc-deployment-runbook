#!/usr/bin/env bash
# shellcheck shell=bash
# =============================================================================
# Provisionamento automatizado da VM Rocky Linux 9 de testes (issue #209)
#
# Substitui os passos manuais da interface web descritos em
# docs/14-ambiente-testes-proxmox.md: usa a imagem genericcloud do Rocky 9 e
# cloud-init, de modo que o laboratório possa ser recriado de forma idêntica.
#
# Uso:
#   infra/proxmox/provision-vm.sh [--recreate]
#
# Pré-requisitos:
#   - stack do compose no ar (container ksc-proxmox)
#   - ~/.secrets/ksc-proxmox.env com PROXMOX_PASSWORD e KSC_VM_IP
# =============================================================================
set -euo pipefail

CONTAINER="${KSC_PVE_CONTAINER:-ksc-proxmox}"
VMID="${KSC_VMID:-100}"
VM_NAME="${KSC_VM_NAME:-ksc-rocky9}"
VM_CORES="${KSC_VM_CORES:-4}"
VM_MEMORY_MB="${KSC_VM_MEMORY_MB:-16384}"
VM_DISK_GB="${KSC_VM_DISK_GB:-120}"
VM_USER="${KSC_VM_USER:-suporte}"
# e1000 em vez de virtio: o modelo virtio faz o QEMU abrir /dev/vhost-net, que
# sob Podman rootless chega ao container sem ACL e resulta em "Permission
# denied". Para o laboratório a diferença de desempenho é irrelevante.
VM_NET_MODEL="${KSC_VM_NET_MODEL:-e1000}"
STORAGE="${KSC_PVE_STORAGE:-local}"
SNAPSHOT="${KSC_BASELINE_SNAPSHOT:-clean-baseline}"
SECRETS_FILE="${KSC_SECRETS_FILE:-$HOME/.secrets/ksc-proxmox.env}"
SSH_KEY="${KSC_VM_SSH_KEY:-$HOME/.ssh/ksc-lab}"

ROCKY_IMAGE_URL="${KSC_ROCKY_IMAGE_URL:-https://dl.rockylinux.org/pub/rocky/9/images/x86_64/Rocky-9-GenericCloud.latest.x86_64.qcow2}"
IMAGE_PATH="/var/lib/vz/template/iso/rocky9-genericcloud.qcow2"

RECREATE=0
[[ "${1:-}" == "--recreate" ]] && RECREATE=1

log() { printf '[provision-vm] %s\n' "$*"; }
die() { printf '[provision-vm][ERRO] %s\n' "$*" >&2; exit 1; }

pve() { podman exec "$CONTAINER" "$@"; }

# --- Pré-condições -----------------------------------------------------------

[[ -f "$SECRETS_FILE" ]] || die "arquivo de segredos ausente: $SECRETS_FILE"
# shellcheck disable=SC1090
source "$SECRETS_FILE"
: "${KSC_VM_IP:?KSC_VM_IP não definido em $SECRETS_FILE}"

podman ps --format '{{.Names}}' | grep -qx "$CONTAINER" \
  || die "container '$CONTAINER' não está em execução. Suba a stack com podman compose."

pve pvesh get /version >/dev/null 2>&1 \
  || die "API do Proxmox não respondeu dentro do container '$CONTAINER'."

# --- Chave SSH do laboratório ------------------------------------------------

if [[ ! -f "$SSH_KEY" ]]; then
  log "gerando par de chaves SSH do laboratório em $SSH_KEY"
  ssh-keygen -t ed25519 -N '' -C "ksc-lab" -f "$SSH_KEY" >/dev/null
fi

# --- Rede: descobre o gateway da bridge vmbr0 --------------------------------

BRIDGE_CIDR="$(pve ip -4 -o addr show vmbr0 | awk '{print $4}' | head -1)"
[[ -n "$BRIDGE_CIDR" ]] || die "não foi possível ler o endereço da bridge vmbr0."
BRIDGE_GW="${BRIDGE_CIDR%/*}"
BRIDGE_PREFIX="${BRIDGE_CIDR#*/}"
log "bridge vmbr0 em $BRIDGE_CIDR (gateway $BRIDGE_GW)"

if [[ "${KSC_VM_IP%.*}" != "${BRIDGE_GW%.*}" ]]; then
  die "KSC_VM_IP ($KSC_VM_IP) está fora da sub-rede da vmbr0 ($BRIDGE_CIDR).
Ajuste KSC_VM_IP em $SECRETS_FILE e reinicie os sidecars da stack."
fi

# --- VM existente ------------------------------------------------------------

if pve qm status "$VMID" >/dev/null 2>&1; then
  if [[ "$RECREATE" -eq 1 ]]; then
    log "removendo VM $VMID existente (--recreate)"
    pve qm stop "$VMID" >/dev/null 2>&1 || true
    pve qm destroy "$VMID" --purge
  else
    log "VM $VMID já existe. Use --recreate para recriá-la do zero."
    exit 0
  fi
fi

# --- Imagem base -------------------------------------------------------------

if pve test -f "$IMAGE_PATH"; then
  log "imagem genericcloud do Rocky 9 já presente no nó"
else
  log "baixando a imagem genericcloud do Rocky Linux 9 (aprox. 600 MB)"
  pve curl -fsSL --retry 3 -o "$IMAGE_PATH" "$ROCKY_IMAGE_URL"
fi

# --- Criação da VM -----------------------------------------------------------

log "criando a VM $VMID ($VM_NAME): ${VM_CORES} vCPU, ${VM_MEMORY_MB} MB RAM, ${VM_DISK_GB} GB"
pve qm create "$VMID" \
  --name "$VM_NAME" \
  --cores "$VM_CORES" \
  --memory "$VM_MEMORY_MB" \
  --cpu host \
  --net0 "${VM_NET_MODEL},bridge=vmbr0" \
  --scsihw virtio-scsi-pci \
  --ostype l26 \
  --agent enabled=1 \
  --serial0 socket \
  --vga serial0

log "importando o disco para o storage '$STORAGE'"
# O volid é lido da saída do importdisk: storages de diretório produzem
# "local:100/vm-100-disk-0.qcow2", diferente do formato de storages LVM.
# --format qcow2: em storage de diretório o padrão é raw, que não suporta
# snapshot — e o snapshot de linha de base é requisito da issue #209.
IMPORT_OUT="$(pve qm importdisk "$VMID" "$IMAGE_PATH" "$STORAGE" --format qcow2)"
VOLID="$(printf '%s\n' "$IMPORT_OUT" | sed -n "s/.*successfully imported disk '\\([^']*\\)'.*/\\1/p")"
[[ -n "$VOLID" ]] || die "não foi possível determinar o volid importado. Saída: $IMPORT_OUT"
log "disco importado como $VOLID"
pve qm set "$VMID" --scsi0 "$VOLID" >/dev/null
pve qm resize "$VMID" scsi0 "${VM_DISK_GB}G" >/dev/null
pve qm set "$VMID" --boot order=scsi0 >/dev/null

# --- cloud-init --------------------------------------------------------------

log "configurando cloud-init (usuário '$VM_USER', IP ${KSC_VM_IP}/${BRIDGE_PREFIX})"
pve qm set "$VMID" --ide2 "${STORAGE}:cloudinit" >/dev/null
pve qm set "$VMID" \
  --ciuser "$VM_USER" \
  --ipconfig0 "ip=${KSC_VM_IP}/${BRIDGE_PREFIX},gw=${BRIDGE_GW}" \
  --nameserver "1.1.1.1" >/dev/null

# A chave pública entra por arquivo para não passar pela linha de comando.
pve mkdir -p /tmp/ksc-lab
podman cp "${SSH_KEY}.pub" "${CONTAINER}:/tmp/ksc-lab/authorized_key.pub"
pve qm set "$VMID" --sshkeys /tmp/ksc-lab/authorized_key.pub >/dev/null

log "iniciando a VM"
pve qm start "$VMID"

# --- Espera o SSH responder --------------------------------------------------

log "aguardando o SSH da VM responder em 127.0.0.1:2222 (até 5 min)"
for _ in $(seq 1 60); do
  if ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
         -o ConnectTimeout=5 -i "$SSH_KEY" -p 2222 \
         "${VM_USER}@127.0.0.1" true 2>/dev/null; then
    log "SSH disponível."
    break
  fi
  sleep 5
done

ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    -i "$SSH_KEY" -p 2222 "${VM_USER}@127.0.0.1" \
    'cat /etc/os-release | head -2' \
  || die "a VM subiu, mas o SSH não respondeu. Verifique os sidecars socat e o KSC_VM_IP."

# --- Snapshot de linha de base ----------------------------------------------

if pve qm listsnapshot "$VMID" | grep -q "$SNAPSHOT"; then
  log "snapshot '$SNAPSHOT' já existe"
else
  log "criando o snapshot de linha de base '$SNAPSHOT'"
  pve qm snapshot "$VMID" "$SNAPSHOT" --description "VM limpa, antes de qualquer deploy do KSC"
fi

log "VM $VMID pronta. Acesso: ssh -i $SSH_KEY -p 2222 ${VM_USER}@127.0.0.1"
