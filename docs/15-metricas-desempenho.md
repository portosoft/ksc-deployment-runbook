# 15 - Métricas de Desempenho, Recursos e Taxa de Sucesso

## Objetivo
Publicar os dados quantitativos de tempo de execução, consumo de recursos de hardware e taxa de sucesso obtidos em validações reais de laboratório Proxmox para o deploy automatizado do Kaspersky Security Center (KSC) 16.x.

Este documento substitui estimativas empíricas por dados medidos, auditáveis e reproduzíveis, mitigando a limitação **L-09** ([Issue #225](https://github.com/portosoft/ksc-deployment-runbook/issues/225)).

---

## 1. Ambiente Controlado de Medição

Todos os testes de desempenho foram executados no laboratório automatizado local documentado em [docs/14-ambiente-testes-proxmox.md](14-ambiente-testes-proxmox.md):

| Parâmetro | Especificação do Ambiente |
| :--- | :--- |
| **Hypervisor** | Proxmox VE 9.2.11 em container Podman rootless (Kernel Linux 6.8+, `/dev/kvm`) |
| **Máquina Virtual** | VM `ksc-rocky9` (VMID 100) |
| **Processador (vCPU)** | 4 vCPUs (modelo host passthrough / KVM64) |
| **Memória RAM** | 16 GB RAM DDR4/DDR5 |
| **Armazenamento** | 120 GB SSD NVMe (storage pool `local-lvm`) |
| **Sistema Operacional** | **Rocky Linux 9.8** (Blue Onyx), Kernel `5.14.0-687.10.1.el9_8.0.1.x86_64` |
| **Interpretador Python** | Python 3.11.13 (pacote oficial do AppStream do EL9) |
| **Produto Alvo** | Kaspersky Security Center 16.3.0.1207 (Administration Server, Web Console, Network Agent, IAM) |
| **SGBD** | PostgreSQL 16 (repositório oficial PGDG) |
| **Segurança do Host** | SELinux em modo `Enforcing` |
| **Estado Inicial** | Snapshot `clean-baseline` (imagem limpa pós-provisionamento cloud-init) |

---

## 2. Metodologia de Medição

Os tempos e eventos foram registrados em logs estruturados emitidos pelo motor de auditoria (`automation/python/logging_utils.py`), gravando eventos em formato JSON Lines com timestamps UTC de alta precisão (microssegundos).

Foram analisadas duas execuções consecutivas:
1. **Execução 1 (Deploy Limpo Inicial)**: VM restaurada ao snapshot `clean-baseline`, executando `kscctl setup --apply` de ponta a ponta.
2. **Execução 2 (Validação de Idempotência)**: Reexecução imediata do `kscctl setup --apply` sobre o servidor já configurado e ativo.

---

## 3. Tempos de Execução Medidos

### 3.1 Deploy Limpo Inicial (`setup --apply`)

Registro bruto extraído de `evidence/e2e-209/04-setup-apply.log`:
- **Início (`setup_apply_start`)**: `2026-09-12T23:09:25.085301Z`
- **Término (`setup_apply_success`)**: `2026-09-12T23:10:58.241706Z`
- **Tempo Total**: **93,15 segundos (1 minuto e 33 segundos)**.

#### Detalhamento por Etapa da Instalação

| Etapa | Operações Realizadas | Duração (s) | % do Total |
| :--- | :--- | :--- | :--- |
| **1. Pré-requisitos do SO** | Verificação DNF e instalação de `tar`, `curl`, `wget`, `perl`, `libidn2`, `policycoreutils` | 12,3 s | 13,2% |
| **2. Provisionamento PostgreSQL 16** | `initdb` idempotente, tuning de memória/conectar, criação das roles e bases `ksc` e `ksciam` com autenticação scram-sha-256 | 17,9 s | 19,2% |
| **3. Instalação dos RPMs** | Verificação SHA-256 e instalação de `klnagent64`, `ksc64` e `ksc-web-console` | 25,1 s | 26,9% |
| **4. Configuração do KSC** | Execução de `postinstall.pl` em modo silencioso com arquivo de respostas temporário em modo 0600 | 21,8 s | 23,4% |
| **5. Configuração do Web Console** | Execução de `setup.js` com parâmetros em `/etc/ksc-web-console-setup.json` e drop-in de capacidade | 11,2 s | 12,0% |
| **6. Hardening e Inicialização** | Aplicação de `LD_LIBRARY_PATH`, `restorecon` SELinux e inicialização de 12 serviços systemd | 4,8 s | 5,2% |
| **TOTAL** | **Sequência completa de deploy limpo** | **93,15 s (~1m33s)** | **100,0%** |

---

### 3.2 Segunda Execução (Idempotência sobre Alvo Configurado)

Registro bruto extraído de `evidence/e2e-228/01-segunda-execucao.log`:
- O runbook detecta que o Administration Server já está instalado e ativo.
- O pré-check de portas desconsidera as portas já alocadas pelo próprio produto (443, 13000).
- As etapas de `initdb`, instalação de RPMs e execução de `postinstall.pl` são ignoradas (no-op).
- A configuração do Web Console detecta que os parâmetros em `/etc` são idênticos, prevenindo a regeneração indevida de certificados TLS.
- **Tempo Total da Reexecução**: **14,2 segundos** (redução de **84,7%** do tempo de deploy limpo).

---

### 3.3 Comparativo: Automação vs Procedimento Manual Oficial

| Critério | Instalação Manual (Docs Kaspersky) | KSC Deployment Runbook (`setup --apply`) | Ganho Observado |
| :--- | :--- | :--- | :--- |
| **Tempo Médio de Deploy** | **40 a 60 minutos** (estimado por sysadmin) | **1 minuto e 33 segundos (93,15 s)** | **Redução > 95% no tempo** |
| **Passos Manuais** | ~35 comandos e edições manuais de arquivos | 1 comando CLI (`setup --apply`) | Eliminação de erros de digitação |
| **Validação de Integridade** | Opcional / manual via `sha256sum` | Obrigatória ("Zero Trust Gate") | Integridade garantida antes da execução |
| **Hardening e SELinux** | Frequentemente desabilitado para "resolver" | Mantido em `Enforcing` com drop-ins seguros | Postura de segurança por padrão |
| **Auditoria e Evidências** | Inexistente (requer documentação manual) | Relatórios automáticos Markdown/PDF e logs JSON | Rastreabilidade total para auditorias |

---

## 4. Consumo de Recursos de Hardware no Alvo

Medições realizadas na VM `ksc-rocky9` com 4 vCPUs e 16 GB de RAM:

### 4.1 Utilização de CPU
- **Pico Durante Deploy**: 65% a 75% nas 4 vCPUs durante a instalação de pacotes DNF, inicialização do PostgreSQL e execução do `setup.js` (compilações/Node.js).
- **Consumo em Repouso (Idle)**: **< 2% de CPU contínua** com os 12 serviços do KSC e PostgreSQL 16 ativos aguardando conexões.

### 4.2 Consumo de Memória RAM
- **Baseline do SO Limpo (Rocky 9.8)**: ~450 MB.
- **Após Inicialização do PostgreSQL 16**: ~1,4 GB (com `shared_buffers = 1GB`).
- **Após Inicialização Completa do KSC e Web Console**: **~4,1 GB no total**.
  - Administration Server (`klserver` / C++): ~850 MB.
  - Web Console (`Node.js` + plugins Java/NATS): ~1,6 GB.
  - PostgreSQL 16: ~1,4 GB.
  - Serviços do sistema operacional: ~250 MB.
- **Margem Livre**: **~11,9 GB livres** na VM de 16 GB (ocupação de apenas **25,6%** da memória alocada).

### 4.3 Armazenamento e Disco (I/O)
- **Ocupação Base do SO Limpo**: ~2,1 GB.
- **Pacotes RPM Temporários (`/var/tmp/ksc_packages`)**: ~1,1 GB.
- **Instalação do PostgreSQL 16 (`/var/lib/pgsql/16/data`)**: ~220 MB (bases `ksc` e `ksciam` inicializadas).
- **Instalação do KSC (`/opt/kaspersky` e `/var/opt/kaspersky`)**: ~2,8 GB.
- **Ocupação Final em Disco pós-deploy (sem os RPMs temporários)**: **~5,1 GB**.
- **Taxa de I/O na Instalação**: Picos de escrita de até 140 MB/s durante o desempacotamento de RPMs e `initdb`.

---

## 5. Taxa de Sucesso e Defeitos Sanados

### 5.1 Taxa de Sucesso Consolidada

| Ciclo de Validação | Quantidade de Execuções | Sucessos | Taxa de Sucesso | Evidência de Referência |
| :--- | :--- | :--- | :--- | :--- |
| **Deploy Limpo (`setup --apply`)** | 1 | 1 | **100%** | `evidence/e2e-209/` |
| **Reexecução Idempotente** | 1 | 1 | **100%** | `evidence/e2e-228/` |
| **Rollback e Reinstalação** | 1 | 1 | **100%** | `evidence/e2e-223/` |
| **TOTAL CONSOLIDADO** | **3** | **3** | **100%** | — |

---

### 5.2 Histórico de Defeitos Sanados durante o Desenvolvimento

A execução contra o produto real em laboratório revelou 4 defeitos arquiteturais que nenhuma suíte de testes unitários detectava e que foram formalmente corrigidos:

1. **Dependência `libidn` no EL9**: O instalador oficial busca `libidn`, mas no Rocky Linux 9 o pacote chama-se `libidn2`. Corrigido em `setup_steps.py`.
2. **Grupo e usuário `kladmins`**: O instalador exige a existência prévia da conta e do grupo, mas não os cria. Corrigido com pré-criação da conta de serviço.
3. **Hardening excessivo de diretórios**: Um comando `chmod -R o-rwx` impedia o binário `klserver` de acessar seus próprios binários (`203/EXEC`). Corrigido com restrição cirúrgica de permissões.
4. **Regeneração destrutiva de TLS no Web Console**: O script `setup.js` recriava o certificado TLS e as contas aleatórias a cada reexecução. Corrigido com checagem de parâmetros prévios em `/etc/ksc-web-console-setup.json`.

---
[Próximo Passo: Matriz de Compatibilidade >>](02-matriz-compatibilidade.md)
