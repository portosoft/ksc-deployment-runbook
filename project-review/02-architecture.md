# 2. Arquitetura da solução

## 2.1 Contexto

O `kscctl` é executado a partir de um host de administração (estação do
operador ou nó de automação). Ele lê a configuração de um arquivo `.env`
(opcionalmente com segredos cifrados por um vault local), valida essa
configuração com modelos `pydantic`, e atua sobre o servidor KSC alvo — seja
localmente, seja por SSH via `paramiko`. Cada ação escreve um log estruturado em
JSON sob `evidence/<operação>/<timestamp>/run.log`.

O KSC é sempre o sistema de destino, nunca um componente embutido: o projeto
executa o instalador oficial e os utilitários do produto, e nunca substitui sua
lógica.

## 2.2 Componentes

| Componente | Caminho | Responsabilidade |
|---|---|---|
| CLI | `automation/python/kscctl.py` | Ponto de entrada único; subcomandos `audit`, `setup`, `db`, `iam`, `web`, `packages` |
| Configuração | `automation/python/config.py` | Carga e validação de `.env` com `pydantic`; resolução de caminhos |
| Vault | `automation/lib/vault.py` | Cifra/decifra segredos; exige permissão `0600` na chave antes de lê-la |
| Pré-checagens | `automation/python/checks.py` | SO, DNS, portas, recursos, PostgreSQL |
| Pacotes | `automation/python/packages.py` | Catálogo oficial, download e verificação SHA-256 em blocos de 64 KB com comparação resistente a timing |
| Passos de setup | `automation/python/setup_steps.py` | Orquestra SO → PostgreSQL → KSC → hardening (**atualmente mock**) |
| Auditoria | `automation/python/ksc_audit.py` | Coleta de estado e geração de relatório |
| Transporte remoto | `automation/python/remote.py` | SSH/SFTP e `run_remote_sudo` centralizado |
| Operações pontuais | `automation/ops/*.py` | Reconfiguração de serviço, reset de bancos, correção do Web Console, purge de MFA do IAM, hardening do PostgreSQL |
| Observabilidade | `automation/python/logging_utils.py`, `report_utils.py` | Log JSON por evento; relatório Markdown/PDF |
| Infra de teste | `infra/proxmox/` | Laboratório Proxmox VE em Podman rootless para validação E2E |
| Documentação | `docs/00..14` | Trilha do operador |

## 2.3 Diagrama

```mermaid
flowchart LR
    OP[Operador] --> CLI[kscctl]
    ENV[(configs/env/ksc_vars.env)] --> CFG[config.py + pydantic]
    VK[(vault.key 0600)] --> VAULT[vault.py]
    VAULT --> CFG
    CFG --> CLI

    CLI --> CHK[checks.py<br/>pre-checagens]
    CLI --> PKG[packages.py<br/>SHA-256 gate]
    CLI --> STEP[setup_steps.py]
    CLI --> AUD[ksc_audit.py]
    CLI --> OPS[automation/ops/*]

    PKG --> REPO[(Portal oficial Kaspersky<br/>RPMs + checksums)]

    STEP --> RMT[remote.py<br/>SSH / sudo / SFTP]
    OPS --> RMT
    CHK --> RMT
    AUD --> RMT

    RMT --> KSC[Servidor alvo<br/>Rocky/Oracle Linux 9]

    subgraph KSC_HOST [Superfícies do KSC 16.x]
        SVC[systemd: kladminserver_srv<br/>klnagent_srv<br/>ksc-web-console<br/>kliam_srv]
        INST[postinstall.pl<br/>+ arquivo de respostas]
        BIN[/opt/kaspersky/ksc64/sbin]
        WCFG[ksc-web-console/server/config.json]
        PG[(PostgreSQL 16<br/>bases ksc e ksciam)]
    end

    KSC --> SVC
    KSC --> INST
    KSC --> BIN
    KSC --> WCFG
    KSC --> PG

    CLI --> EV[(evidence/*/run.log<br/>JSON estruturado)]
    AUD --> RPT[Relatório Markdown/PDF]
```

## 2.4 Fluxo de execução principal

1. `kscctl audit --check` — valida SO, DNS, portas, memória, disco e
   conectividade com o PostgreSQL. Interrompe em falha crítica.
2. `kscctl packages --list` / `--verify-dir` — confere a presença e o SHA-256
   de cada RPM oficial. Nenhuma instalação prossegue sem esse gate.
3. `kscctl setup --check` — simula a sequência completa sem alterar o alvo.
4. `kscctl setup --apply` — prepara o SO, configura o PostgreSQL 16, instala os
   pacotes do KSC em modo silencioso e aplica o hardening.
5. `kscctl audit --report` — gera o relatório de evidências do deploy.

## 2.5 Fluxos alternativos e de erro

| Situação | Comportamento atual |
|---|---|
| Pré-checagem crítica falha | Execução interrompida antes de qualquer alteração; evento `*_failed` no log JSON |
| SHA-256 divergente | Instalação bloqueada; o pacote é rejeitado |
| `postinstall.pl` retorna código diferente de zero | Evento `reconfigure_failed` com a mensagem de erro; sem rollback automático `[LIMITAÇÃO]` |
| Falha após instalação parcial | Rollback **manual**, conforme `docs/11-rollback.md` (parar serviços → encerrar conexões com `pg_terminate_backend` → `DROP DATABASE ... IF EXISTS` → remover usuário) `[LIMITAÇÃO]` |
| Perda de conectividade SSH | Erro propagado; a operação não é retomada automaticamente `[LIMITAÇÃO]` |

## 2.6 Decisões arquiteturais relevantes para a revisão

| # | Decisão | Motivo | Consequência |
|---|---|---|---|
| AD-1 | Python + `paramiko` como orquestrador, com Ansible em papel auxiliar | Controle fino sobre a sequência de instalação e sobre o formato das evidências | Uma segunda pilha de automação (Ansible) é mantida em paralelo — dívida técnica reconhecida |
| AD-2 | Contrato CLI `--check` / `--apply` / `--report` obrigatório | Permite dry-run auditável antes de qualquer alteração | Todo novo subcomando precisa de teste de contrato |
| AD-3 | Gate de integridade SHA-256 antes de qualquer instalação | Não confiar em artefatos locais não verificados | Depende de o catálogo de checksums acompanhar as publicações da Kaspersky |
| AD-4 | Configuração da instalação por arquivo de respostas, não por interação | Reprodutibilidade entre servidores | Depende da estabilidade do formato do arquivo de respostas — **ver pergunta Q3** |
| AD-5 | Configuração do Web Console por manipulação de JSON nativo, substituindo `sed` | Elimina injeção de comando e edição frágil por regex | Depende do esquema de `config.json` — **ver pergunta Q2** |
| AD-6 | Evidências como JSON linha-a-linha em `evidence/` | Auditabilidade e diff entre execuções | Requer disciplina de sanitização para não registrar segredos |

## 2.7 Pontos que pedem revisão da equipe Kaspersky

- AD-4 e AD-5 dependem de formatos de arquivo cuja estabilidade entre versões
  não conseguimos confirmar pela documentação pública.
- A reconfiguração de um servidor já instalado via `postinstall.pl` é o método
  que observamos funcionar, mas não sabemos se é o método suportado.
- A sequência de rollback que documentamos toca diretamente as bases `ksc` e
  `ksciam`; queremos confirmar se ela é segura e completa do ponto de vista do
  produto.
