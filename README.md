# 🛡️ Kaspersky Security Center 16.x Deployment Runbook

![Stability: Stable](https://img.shields.io/badge/stability-stable-green.svg)
![PostgreSQL: 16](https://img.shields.io/badge/PostgreSQL-16-blue.svg)
![OS: Rocky/Oracle Linux 9](https://img.shields.io/badge/OS-Rocky%2FOracle%209-orange.svg)

Guia operacional definitivo e automação para implantação do KSC Administration Server em ambientes Linux de alta disponibilidade.

---

## 🎯 Proposta do Projeto
Garantir deploys de KSC 16.x repetíveis, seguros e auditáveis através de automação padronizada e documentação orientada à jornada do operador.

## 📋 Quando Usar vs. Quando Não Usar
| ✅ Use quando: | ❌ NÃO use quando: |
| :--- | :--- |
| Implantação nova em Rocky/Oracle Linux 9. | Migrações de KSC Windows para Linux (procedimento diferente). |
| Uso de PostgreSQL 16 local ou remoto. | Versões de KSC anteriores à 15.0. |
| Necessidade de auditoria e hardening automático. | Ambientes com MySQL/MariaDB. |

## 🏗️ Escopo
- **In-Scope**: Setup do SO, Preparação do Postgres 16, Instalação do KSC Server, Web Console, Hardening de Segurança.
- **Out-of-Scope**: Configuração de firewalls de borda, licenciamento do Kaspersky, configuração de políticas de endpoint (pós-deploy).

## 📊 Matriz de Compatibilidade
- **SO**: Rocky Linux 9.x, Oracle Linux 9.x (RHEL Core).
- **DBMS**: PostgreSQL 16.x (Suporte oficial Kaspersky).
- **RAM**: Mínimo 8GB (Recomendado 16GB).
- **Disk**: 100GB+ para `/opt/kaspersky` e `/var/opt/kaspersky`.

## 🚀 Quick Start (Sequência Mínima)
```bash
# 1. Clone o repositório
git clone https://github.com/portosoft/ksc-deployment-runbook.git
cd ksc-deployment-runbook

# 2. Prepare suas variáveis
cp configs/env/ksc_vars.env.example configs/env/.ksc_vars.env
vi configs/env/.ksc_vars.env

# 3. Execute o Pre-check
python3 automation/python/ksc_audit.py --check

# 4. Inicie a Instalação
python3 automation/python/ksc_setup.py --apply
```

## 🗺️ Estrutura do Repositório
- `docs/`: A jornada completa do operador, dividida em 12 etapas numeradas.
- `automation/`: Scripts Python, Bash e Playbooks Ansible para execução.
- `configs/`: Templates de arquivos de resposta e configurações de banco de dados.
- `evidence/`: Local para armazenar logs e outputs de validação para auditoria interna.

## 🤝 Contratos de Automação
Este projeto utiliza uma convenção rigorosa de argumentos CLI:
- `--check`: Apenas valida pré-requisitos (Dry-run).
- `--apply`: Executa as alterações no sistema.
- `--report`: Gera um PDF/Markdown com as evidências da etapa.

## ✅ Critérios de Sucesso (Definition of Done)
1. PostgreSQL operacional com parâmetros de performance aplicados.
2. KSC Administration Server rodando (`klnagent` e `klserver` ativos).
3. Web Console acessível via HTTPS na porta 443.
4. Relatório de auditoria gerado pelo `ksc_audit.py` com 0 falhas críticas.

## ⚠️ Riscos Conhecidos
- **SELinux**: Deve estar em `permissive` durante a instalação para que o instalador crie os contextos corretamente.
- **LD_LIBRARY_PATH**: Binários do KSC em Linux podem falhar sem o path correto para bibliotecas internas.

---
**Status do Projeto:** `Produção`
**Roadmap:** Implementação de suporte a PostgreSQL Externo (RDS/Cloud SQL) e Integração com Vault.
**Governança:** Mantido pelo time de DevOps Portosoft.
