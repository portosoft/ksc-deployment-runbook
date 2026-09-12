# Evidências da validação E2E — issue #209 (parcial)

Execuções **reais** em VM Rocky Linux 9.8 provisionada pelo laboratório
Proxmox local (`infra/proxmox/`). Substituem parcialmente os artefatos
simulados descritos em `project-review/05-testing-and-validation.md` §5.4.

| Arquivo | Conteúdo | Resultado |
|---|---|---|
| `00-ambiente.txt` | Versões do SO, kernel e Python da VM | — |
| `01-audit-check.log` | `kscctl audit --check` | exit 0, sem falhas críticas |
| `02-setup-check-dryrun.log` | `kscctl setup --check` (dry-run da sequência completa) | exit 0 |
| `03-packages-verify.log` | `kscctl packages --verify-dir` sobre os RPMs oficiais | 3 pacotes íntegros |
| `04-setup-apply.log` | **`kscctl setup --apply` — deploy real e limpo** | **exit 0** |
| `05-estado-final.log` | Serviços e portas após o deploy | 6 serviços `active` |

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
- O gate de integridade SHA-256 valida os RPMs oficiais baixados dos
  servidores da Kaspersky.
- **`setup --apply` executa um deploy real de ponta a ponta, a partir de uma VM
  restaurada ao snapshot limpo, e retorna 0.** PostgreSQL 16 instalado e
  configurado, bases `ksc` e `ksciam` criadas, os três RPMs do KSC 16.3
  instalados, `postinstall.pl` concluído e hardening aplicado com o SELinux
  restaurado a `enforcing`.
- O Administration Server 16.3.0.1207 entra em execução e seis serviços ficam
  `active`: `kladminserver_srv`, `klnagent_srv`, `kliam_srv`, `klwebsrv_srv`,
  `klactprx_srv` e `klcssnmp_srv`.

## O que estas evidências **não** comprovam

- **O Web Console não está acessível.** O RPM instala os arquivos, mas a
  configuração depende de uma etapa própria, parametrizada por
  `configs/ksc/ksc-web-console-setup.json.example`, que a automação ainda não
  executa. A porta 443 não está em escuta.
- O deploy não foi exercitado em Oracle Linux 9 nem em outra versão menor do
  KSC 16.x.
- O rollback não foi exercitado sobre uma instalação parcial.

## Divergências de porta observadas

| Porta | Documentação do projeto | Observado na instalação real |
|---|---|---|
| 13000 | Network Agent SSL | Em escuta (`klserver`) |
| 13291 | API do Administration Server | **Não está em escuta**; a porta OpenAPI ativa é a **13299** |
| 14000 | Network Agent plain | **Não está em escuta** |
| 443 | Web Console HTTPS | Não está em escuta (Web Console não configurado) |

`configs/ksc/ksc-web-console-setup.json.example` já referencia `openApiPort:
13299`, enquanto `automation/python/checks.py` e a documentação verificam a
13291 — as duas fontes do próprio repositório divergem entre si.

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
