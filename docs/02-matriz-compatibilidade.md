# 02 - Matriz de Compatibilidade

## Objetivo
Garantir previsibilidade, estabilidade e conformidade arquitetural ao implantar o Kaspersky Security Center (KSC) 16.x no Linux.

O projeto adota o princípio de **honestidade técnica e separação categórica**: distinguimos claramente os ambientes **comprovados e homologados por execução real** daqueles **declarados compatíveis por documentação**, prevenindo surpresas em produção.

---

## 1. Ambientes Comprovados e Homologados em Execução Real

Os ambientes abaixo foram validados de ponta a ponta no laboratório Proxmox e homologados via compatibilidade binária estrita da família Enterprise Linux 9 (EL9).

| Componente | Especificação Homologada | Status & Evidência |
| :--- | :--- | :--- |
| **Rocky Linux 9.8** | Kernel 5.14.0-687.10.1.el9_8.0.1 x86_64 + KSC 16.3.0.1207 + PostgreSQL 16 | **Comprovado em Lab** (`evidence/e2e-209/`, `evidence/e2e-225/`) |
| **Oracle Linux 9.x** | Kernel UEK R7 (5.15+) ou RHCK (5.14) + KSC 16.3.0.1207 + PostgreSQL 16 | **Homologado EL9** (`infra/proxmox/`, [#227](https://github.com/portosoft/ksc-deployment-runbook/issues/227)) |
| **KSC 16.2.0.1023** | Rocky Linux 9.x / EL9 + KSC 16.2.0.1023 + PostgreSQL 16 | **Homologado** (`configs/ksc/packages.json`, [#227](https://github.com/portosoft/ksc-deployment-runbook/issues/227)) |
| **Ambiente Python** | Python 3.11 (pacote oficial do AppStream do EL9) | **Comprovado** (requisito obrigatório, ref #231) |
| **Segurança do Host** | SELinux em modo `Enforcing` durante e após o deploy | **Comprovado** (políticas carregadas sem quebra de serviço) |

---

## 2. Particularidades do Oracle Linux 9 (UEK vs RHCK)

O Oracle Linux 9 oferece duas opções de kernel:

1. **Unbreakable Enterprise Kernel (UEK R7 - Kernel 5.15 / 6.x)**: Kernel otimizado pela Oracle para cargas corporativas pesadas e banco de dados. Totalmente compatível com o binário `klserver` do KSC e com o driver PostgreSQL.
2. **Red Hat Compatible Kernel (RHCK - Kernel 5.14)**: Idêntico ao kernel do RHEL 9 e Rocky Linux 9.8.

Ambas as variantes compartilham a mesma base de pacotes ELF x86_64, módulos systemd e políticas SELinux. O repositório oficial PGDG do PostgreSQL 16 e o Python 3.11 do AppStream operam de forma idêntica em ambos os kernels.

---

## 3. Matriz Comparativa entre KSC 16.2 e KSC 16.3

A evolução da linha 16.2 para a 16.3 introduziu ajustes arquiteturais suportados pelo runbook:

| Item | KSC 16.2.0.1023 | KSC 16.3.0.1207 | Impacto Operacional |
| :--- | :--- | :--- | :--- |
| **Porta OpenAPI** | 13291 (SSL legada) | **13299** (OpenAPI ativa) | KSC 16.3 exige parametrização explícita de `openApiPort: 13299` |
| **Web Console** | `ksc-web-console-16.2.11309` | `ksc-web-console-16.3.12907` | Exige drop-in `CAP_NET_BIND_SERVICE` para escuta na porta 443 |
| **PostgreSQL** | Homologado nativamente para PG 15 | Homologado nativamente para **PG 16** | Ambos suportados com autenticação `scram-sha-256` |
| **RPM Network Agent** | `klnagent64-16.2.0-1023` | `klnagent64-16.3.0-1207` | Verificado via catálogo SHA-256 no Zero Trust Gate |

---

## 4. Ambientes Declarados em Documentação (Compatíveis)

Os sistemas abaixo são compatíveis segundo a documentação oficial da Kaspersky:

| SO / Distribuição | Versão | Status Arquitetural |
| :--- | :--- | :--- |
| **Rocky Linux** | 9.2, 9.3, 9.4 | Compatível (derivação direta da família EL9) |
| **AlmaLinux** | 9.x | Compatível (família EL9) |

---

## 5. Banco de Dados e Dimensionamento (Sizing)

- **Versão Homologada**: PostgreSQL 16.x (repositório oficial PGDG).
- **Topologias**:
  - *Instalação Local (Padrão)*: Ouvindo em `127.0.0.1` e socket Unix local com autenticação `scram-sha-256`.
  - *Instalação Dedicada (Remota)*: Suportada via host/porta e TLS obrigatório.

### Dimensionamento Recomendado

| Perfil de Carga | Quantidade de Endpoints | Configuração Mínima Recomendada | Armazenamento |
| :--- | :--- | :--- | :--- |
| **Pequeno Porte** | Até 1.000 hosts | 4 vCPUs, 8 GB RAM | 100 GB SSD NVMe/SAS |
| **Médio Porte** | De 1.000 a 5.000 hosts | 8 vCPUs, 16 GB RAM | 250 GB SSD NVMe |
| **Grande Porte** | De 5.000 a 20.000 hosts | 16 vCPUs, 32 GB RAM | 500 GB SSD NVMe (I/O intensivo) |

---
[Próximo Passo: Pré-requisitos >>](03-pre-requisitos.md)
