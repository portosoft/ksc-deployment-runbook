# Evidências da validação E2E — issue #209 (parcial)

Execuções **reais** em VM Rocky Linux 9.8 provisionada pelo laboratório
Proxmox local (`infra/proxmox/`). Substituem parcialmente os artefatos
simulados descritos em `project-review/05-testing-and-validation.md` §5.4.

| Arquivo | Conteúdo | Resultado |
|---|---|---|
| `00-ambiente.txt` | Versões do SO, kernel e Python da VM | — |
| `01-audit-check.log` | `kscctl audit --check` | exit 0, sem falhas críticas |
| `02-setup-check-dryrun.log` | `kscctl setup --check` (dry-run da sequência completa) | exit 0 |

## Ambiente

| Item | Valor |
|---|---|
| Data | 2026-09-12 |
| Host | Podman rootless 5.7.0, `/dev/kvm` via ACL |
| Hypervisor | Proxmox VE 9.2.11 (`dockurr/proxmox:9.2.10`) |
| VM | `ksc-rocky9` (VMID 100), 4 vCPU, 16 GB RAM, 120 GB, NIC e1000 |
| SO | Rocky Linux 9.8 (Blue Onyx), kernel 5.14.0-687.10.1.el9_8.0.1 |
| Python | 3.11.13 (AppStream) — **não** o 3.9 padrão do SO, ver abaixo |
| SELinux | `Enforcing` |
| Snapshot | `clean-baseline` criado antes de qualquer execução |
| Commit | `8af2d21` (develop) |

## O que estas evidências comprovam

- As pré-checagens funcionam contra um Rocky Linux 9 real, com SELinux em
  modo `enforcing`, e retornam código 0.
- O dry-run da sequência completa executa os quatro passos desmockados e
  imprime cada comando que seria executado, sem alterar o sistema.
- O aviso de pacotes ausentes em modo `--check` se comporta como projetado:
  registra a indisponibilidade e não aborta.

## O que estas evidências **não** comprovam

- Nenhuma instalação real do KSC foi executada: `setup --apply` ainda não
  rodou, porque depende dos RPMs oficiais da Kaspersky.
- Portanto **nada aqui valida compatibilidade com o KSC 16.x**. As limitações
  L-02 e L-03 permanecem abertas.

## Achado: Python do sistema no SO alvo

O `requirements.txt` fixa `md2pdf==3.1.1`, que exige Python >= 3.10. O Rocky
Linux 9 entrega Python 3.9 como `python3` do sistema, então
`pip3 install -r requirements.txt` **falha no sistema operacional alvo
primário do projeto**:

```
ERROR: Ignored the following versions that require a different python version:
  ... 3.1.1 Requires-Python >=3.10
ERROR: No matching distribution found for md2pdf==3.1.1
```

Contornado nestas execuções instalando `python3.11` do AppStream. A correção
definitiva — declarar a versão mínima de Python e alinhar a documentação, que
hoje instrui `python3 -m automation.python.kscctl` — está registrada na
issue #231.
