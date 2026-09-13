# 🛡️ Kaspersky Security Center 16.x Deployment Runbook

![Estágio: Beta](https://img.shields.io/badge/est%C3%A1gio-beta-yellow.svg)
![KSC: 16.3 validado](https://img.shields.io/badge/KSC-16.3.0.1207%20validado-green.svg)
![PostgreSQL: 16](https://img.shields.io/badge/PostgreSQL-16-blue.svg)
![OS: Rocky/Oracle Linux 9](https://img.shields.io/badge/OS-Rocky%2FOracle%209-orange.svg)
![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)

Automação e documentação para implantar o KSC Administration Server em Linux de
forma repetível e auditável.

---

## 📌 Estágio e o que está comprovado

**Beta.** Leia antes de usar em produção.

**Comprovado por execução real** — 12/09/2026, evidências em
[`evidence/e2e-209/`](evidence/e2e-209/README.md):

- Deploy completo de **KSC 16.3.0.1207** em Rocky Linux 9.8 com PostgreSQL 16:
  instalação, Web Console em HTTPS e relatório de auditoria sem falhas críticas.
- **Rollback** sobre instalação interrompida, seguido de reinstalação limpa
  ([`evidence/e2e-223/`](evidence/e2e-223/README.md)).
- **Idempotência**: três execuções consecutivas de `setup --apply` deixando
  idêntico todo o estado coberto pelo fingerprint — pacotes, serviços, portas,
  contas, permissões, hashes de configuração e o certificado do Web Console
  ([`evidence/e2e-228/`](evidence/e2e-228/README.md)). O conteúdo das bases de
  dados não é comparado.

**Não comprovado:**

- A validação cobre **uma combinação, em uma execução de laboratório**. Oracle
  Linux 9 e outras versões do KSC seguem declaradas, não testadas
  ([#227](https://github.com/portosoft/ksc-deployment-runbook/issues/227)).
- Nenhuma métrica de desempenho foi coletada
  ([#225](https://github.com/portosoft/ksc-deployment-runbook/issues/225)).
- `.env` em texto claro ainda é caminho suportado
  ([#237](https://github.com/portosoft/ksc-deployment-runbook/issues/237)).

Limitações completas em
[project-review/06-known-limitations.md](project-review/06-known-limitations.md).

---

## 📋 Quando usar e quando não usar

| ✅ Use quando | ❌ Não use quando |
| :--- | :--- |
| Implantação nova em **Rocky Linux 9** (validado) ou Oracle Linux 9 (suportado em tese, [não testado](https://github.com/portosoft/ksc-deployment-runbook/issues/227)) | Migração de KSC Windows para Linux (procedimento diferente) |
| PostgreSQL 16 local ou remoto | Versões de KSC anteriores à 15.0 |
| É preciso auditar e endurecer o servidor | Ambientes com MySQL ou MariaDB |

## 🏗️ Escopo

**Dentro:** preparação do SO, PostgreSQL 16, instalação do KSC Server e do Web
Console, hardening, auditoria com relatório e rollback.

**Fora:** firewalls de borda, licenciamento Kaspersky, políticas de endpoint
pós-deploy.

## 📊 Requisitos

| Item | Exigência |
| :--- | :--- |
| SO | Rocky Linux 9.x — **validado em 9.8**. Oracle Linux 9.x é suportado em tese, mas nunca foi exercitado ([#227](https://github.com/portosoft/ksc-deployment-runbook/issues/227)) |
| **Python** | **3.10 ou superior.** O `python3` do Rocky 9 é a versão 3.9 e **não** satisfaz o `requirements.txt` — instale `python3.11` do AppStream ([#231](https://github.com/portosoft/ksc-deployment-runbook/issues/231)) |
| SGBD | PostgreSQL 16.x |
| RAM | 8 GB mínimo; abaixo de 16 GB o pré-check emite aviso |
| Disco | 100 GB+ em `/opt/kaspersky` e `/var/opt/kaspersky` |
| Privilégio | `sudo` no servidor alvo |

---

## 🚀 Quick start

> [!WARNING]
> **`setup --apply` instala de verdade.** Até a versão 1.1.1 esses passos eram
> simulados; a partir da 2.0.0 eles alteram o servidor. Use `setup --check`
> para simular a sequência completa sem tocar no sistema.

> [!IMPORTANT]
> Use um **ambiente virtual**, e o mesmo interpretador com e sem `sudo`. Uma
> instalação com `pip install --user` fica no diretório do operador e não é
> visível para o `root`: os comandos que exigem privilégio falhariam com
> `ModuleNotFoundError` antes mesmo de começar.

```bash
# 1. Repositório e ambiente virtual (python3.11 no Rocky 9 — ver Requisitos)
git clone https://github.com/portosoft/ksc-deployment-runbook.git
cd ksc-deployment-runbook
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt

# 2. Variáveis de ambiente
cp configs/env/ksc_vars.env.example configs/env/ksc_vars.env
.venv/bin/python -m automation.python.init_config   # configuração interativa segura

# 3. Pré-check
.venv/bin/python -m automation.python.kscctl audit --check

# 4. Pacotes oficiais, com verificação SHA-256 obrigatória
.venv/bin/python -m automation.python.kscctl packages --list
.venv/bin/python -m automation.python.kscctl packages --download ksc-server-16.3-pt-BR \
  --output-dir /var/tmp/ksc_packages
.venv/bin/python -m automation.python.kscctl packages --verify-dir /var/tmp/ksc_packages

# 5. Simular a instalação completa, sem alterar nada
.venv/bin/python -m automation.python.kscctl setup --check

# 6. Instalar — mesmo interpretador, agora com privilégio
sudo .venv/bin/python -m automation.python.kscctl setup --apply

# 7. Verificar e gerar o relatório de evidências
sudo .venv/bin/python -m automation.python.kscctl audit --postcheck
sudo .venv/bin/python -m automation.python.kscctl audit --report
```

Para desfazer tudo e voltar ao estado anterior, veja
[docs/11-rollback.md](docs/11-rollback.md).

## 🧰 Comandos

| Comando | Função |
| :--- | :--- |
| `audit --check` | Pré-requisitos antes de instalar |
| `audit --postcheck` | Estado do servidor depois de instalado |
| `audit --report` | Relatório de evidências em Markdown e PDF |
| `packages --list` / `--download` / `--verify-dir` | Catálogo oficial e verificação de integridade |
| `setup --check` / `--apply` | Simulação e instalação |
| `db harden` / `db reset` | Tuning e recriação das bases |
| `web fix-config` | Ajustes no Web Console |
| `iam purge-mfa` | Remoção de fatores MFA do serviço IAM |
| `rollback --check` / `--apply --verify` | Remoção completa, com verificação de resíduos |

### Contrato da CLI

- `--check` — simula e não altera o sistema.
- `--apply` — executa as alterações.
- `--report` — gera as evidências da etapa.
- `--confirm-token` — exigido pelas operações destrutivas (`db reset`,
  `iam purge-mfa`, `rollback`).

## 🗺️ Estrutura

| Diretório | Conteúdo |
| :--- | :--- |
| `docs/` | Jornada do operador, em 15 etapas numeradas (00–14) |
| `automation/` | CLI Python, scripts Bash e playbooks Ansible |
| `configs/` | Templates de resposta, catálogo de pacotes e configuração |
| `infra/proxmox/` | Laboratório de testes containerizado e provisionamento da VM |
| `evidence/` | Saídas de validação; `e2e-*` contém as execuções reais |
| `project-review/` | Pacote técnico preparado para avaliação externa |

## 🛤️ Jornada do operador

[00-index](docs/00-index.md) ·
[01-visão geral](docs/01-visao-geral.md) ·
[02-compatibilidade](docs/02-matriz-compatibilidade.md) ·
[03-pré-requisitos](docs/03-pre-requisitos.md) ·
[04-precheck](docs/04-precheck.md) ·
[05-PostgreSQL](docs/05-instalacao-postgresql.md) ·
[06-instalação KSC](docs/06-instalacao-ksc.md) ·
[07-pós-instalação](docs/07-pos-instalacao-validacao.md) ·
[08-hardening](docs/08-hardening.md) ·
[09-operação](docs/09-operacao.md) ·
[10-troubleshooting](docs/10-troubleshooting.md) ·
[11-rollback](docs/11-rollback.md) ·
[12-FAQ](docs/12-faq.md) ·
[13-contrato operacional](docs/13-contrato-operacional.md) ·
[14-laboratório Proxmox](docs/14-ambiente-testes-proxmox.md)

## ✅ Critérios de sucesso

1. PostgreSQL 16 ativo, com as bases `ksc` e `ksciam` criadas.
2. Serviços do KSC ativos: `kladminserver_srv`, `klnagent_srv`, `kliam_srv`,
   `klwebsrv_srv`.
3. Web Console acessível por HTTPS.
4. `audit --report` gerado com zero falhas críticas.
5. SELinux em `enforcing` ao final.

## ⚠️ Riscos e particularidades conhecidos

- **SELinux.** A automação o coloca em permissivo durante a instalação e o
  restaura para `enforcing` ao final, inclusive em caso de erro. Não é preciso
  alterá-lo manualmente.
- **`LD_LIBRARY_PATH`.** Os binários do KSC dependem das bibliotecas em
  `/opt/kaspersky/ksc64/lib`. O caminho é aplicado como drop-in do systemd, e
  nunca em `/etc/profile` ou `/etc/environment`, para não vazar para o sistema.
- **Hardening e contas de serviço.** O KSC roda com contas próprias, algumas de
  nomes gerados aleatoriamente pelo instalador. Fechar permissões sem conceder
  acesso a elas derruba o produto — o hardening deste runbook leva isso em conta.
- **Portas.** A 13291 citada na documentação do produto não fica em escuta nesta
  versão; a porta OpenAPI ativa é a **13299**.

## 🧪 Testes

```bash
.venv/bin/python -m pytest -q
```

O laboratório de validação ponta a ponta está documentado em
[docs/14-ambiente-testes-proxmox.md](docs/14-ambiente-testes-proxmox.md).

## 🗺️ Planejamento

A fonte única do backlog é o GitHub:
[board](https://github.com/orgs/portosoft/projects/1) e
[issues](https://github.com/portosoft/ksc-deployment-runbook/issues), com o
épico corrente em
[#203](https://github.com/portosoft/ksc-deployment-runbook/issues/203).
[project-review/09-roadmap.md](project-review/09-roadmap.md) é uma visão desse
backlog para o leitor externo; se divergir, o board vence. Documentos em
`docs/internal/` são registro histórico e não definem trabalho pendente.

Fluxo de branches: `feature/*` → `develop` → `main`.

## 🧭 Pacote de revisão técnica

[`project-review/`](project-review/README.md) reúne o material preparado para
avaliação por desenvolvedores e mantenedores do Kaspersky Security Center:
arquitetura, mapa de integração, segurança, evidências, limitações e perguntas
técnicas.

## 🤝 Contribuindo

Issues, pull requests e discussões são bem-vindos — veja
[CONTRIBUTING.md](CONTRIBUTING.md). Para vulnerabilidades, siga
[SECURITY.md](SECURITY.md).

## ⚖️ Aviso de independência

Projeto independente sob Apache 2.0, **sem vínculo, patrocínio ou endosso da AO
Kaspersky Lab**. "Kaspersky" e "Kaspersky Security Center" são marcas de seus
respectivos titulares, citadas apenas para identificar a ferramenta com a qual o
projeto se integra. Nenhum artefato do produto é redistribuído aqui.

---

**Licença:** Apache 2.0 — veja [LICENSE](LICENSE).
