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

## 🏗️ Sobre este Projeto

### O que é este Runbook?
Um runbook open-source para automatizar e auditar implantações do KSC 16.x no Linux.
Desenvolvido colaborativamente para ser repetível, seguro e auditável — adequado tanto
para ambientes de laboratório quanto para produção corporativa.

### Contribuindo
Issues, pull requests e discussões são bem-vindos. Veja [CONTRIBUTING.md](CONTRIBUTING.md)
para diretrizes. Para reportar vulnerabilidades de segurança, veja [SECURITY.md](SECURITY.md).

---

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
cp configs/env/ksc_vars.env.example configs/env/ksc_vars.env
vi configs/env/ksc_vars.env

# 3. Execute o Pre-check
python3 -m automation.python.kscctl audit --check

# 4. Inicie a Instalação
python3 -m automation.python.kscctl setup --apply
```

## 🗺️ Estrutura do Repositório
- `docs/`: A jornada completa do operador, dividida em 12 etapas numeradas.
- `automation/`: Scripts Python, Bash e Playbooks Ansible para execução.
- `configs/`: Templates de arquivos de resposta e configurações de banco de dados.
- `evidence/`: Local para armazenar logs e outputs de validação para auditoria interna.

## 🛤️ A Jornada do Operador
Siga esta trilha para um deploy seguro e auditável:
- [00-index.md](docs/00-index.md)
- [01-visao-geral.md](docs/01-visao-geral.md)
- [02-matriz-compatibilidade.md](docs/02-matriz-compatibilidade.md)
- [03-pre-requisitos.md](docs/03-pre-requisitos.md)
- [04-precheck.md](docs/04-precheck.md)
- [05-instalacao-postgresql.md](docs/05-instalacao-postgresql.md)
- [06-instalacao-ksc.md](docs/06-instalacao-ksc.md)
- [07-pos-instalacao-validacao.md](docs/07-pos-instalacao-validacao.md)
- [08-hardening.md](docs/08-hardening.md)
- [09-operacao.md](docs/09-operacao.md)
- [10-troubleshooting.md](docs/10-troubleshooting.md)
- [11-rollback.md](docs/11-rollback.md)
- [12-faq.md](docs/12-faq.md)
- [13-contrato-operacional.md](docs/13-contrato-operacional.md)

## 🤝 Contratos de Automação
Este projeto utiliza uma convenção rigorosa de argumentos CLI:
- `--check`: Apenas valida pré-requisitos ou simula operações (Dry-run).
- `--apply`: Executa as alterações no sistema local ou remoto.
- `--report`: Gera um PDF/Markdown com as evidências da etapa.

## ✅ Critérios de Sucesso (Definition of Done)
1. PostgreSQL operacional com parâmetros de performance aplicados.
2. KSC Administration Server rodando (`klnagent` e `klserver` ativos).
3. Web Console acessível via HTTPS na porta 443.
4. Relatório de auditoria gerado pelo `kscctl audit --report` com 0 falhas críticas.

## 📏 Service Level Indicators (SLIs) Internos
Como um produto interno, visamos as seguintes métricas operacionais:
- **Deploy Time**: O comando `kscctl setup --apply` deve finalizar em menos de 10 minutos (assumindo rede estável).
- **Audit Time**: O comando `kscctl audit --check` deve executar em menos de 15 segundos.
- **Fail Rate**: Zero falhas silenciosas. O script deve quebrar barulhentamente em qualquer desvio de pré-requisito (*Fail Fast, Fail Loud*).

## ⚠️ Riscos Conhecidos
- **SELinux**: Deve estar em `permissive` durante a instalação para que o instalador crie os contextos corretamente.
- **LD_LIBRARY_PATH**: Binários do KSC em Linux podem falhar sem o path correto para bibliotecas internas.

---
**Status do Projeto:** `Estável`
**Roadmap:** Suporte a PostgreSQL Externo (RDS/Cloud SQL) e integração com HashiCorp Vault.
**Licença:** Apache 2.0 — veja [LICENSE](LICENSE).
