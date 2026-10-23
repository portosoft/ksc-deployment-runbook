# 3. Integração com o Kaspersky Security Center 16.x

Este é o documento central para a equipe da ferramenta principal.

## 3.1 Princípios da integração

1. O projeto **não altera binários, bibliotecas ou lógica do KSC**.
2. O projeto **não redistribui pacotes Kaspersky**; ele referencia os artefatos
   oficiais e verifica sua integridade.
3. Toda ação sobre o produto ocorre por meio de instaladores, utilitários,
   unidades systemd, arquivos de configuração ou bancos de dados do próprio
   produto.
4. Onde dependemos de comportamento não documentado, isso é declarado
   explicitamente — e é o objeto do nosso pedido de revisão.

## 3.2 Mapa de interfaces utilizadas

Classificação usada na coluna **Tipo**:
`Oficial` (documentada e formalmente suportada) · `Pública` (exposta e estável
na prática, sem contrato formal conhecido por nós) · `Observada` (derivada de
comportamento verificado em execução) · `Interna` (depende de detalhe de
implementação) · `Não confirmada`.

| Componente do KSC | Uso pelo projeto | Tipo | Dependência | Estado |
|---|---|---|---|---|
| Pacotes RPM oficiais (Administration Server, Web Console, Network Agent) | Download referenciado e verificação SHA-256 antes da instalação | Oficial | Portal de distribuição Kaspersky | Implementado e testado unitariamente |
| Instalação silenciosa via arquivo de respostas (`configs/ksc/ksc_response.txt.template`) | Parametriza a instalação sem interação | Pública | Formato e chaves do arquivo de respostas | Implementado · formato **não confirmado** (Q3) |
| `/opt/kaspersky/ksc64/lib/bin/setup/postinstall.pl` | Reconfiguração pós-instalação do Administration Server em modo silencioso | Observada | Caminho e contrato do script | Implementado · **não confirmado** (Q1) |
| `/opt/kaspersky/ksc64/sbin/kladduser` | Criação da conta administrativa inicial | Pública | Caminho e sintaxe | Implementado · não validado em alvo real |
| Unidades systemd `kladminserver_srv`, `klnagent_srv`, `ksc-web-console`, `kliam_srv` | `start` / `stop` / `status` durante setup, hardening, reset de banco e auditoria | Pública | Nomes das unidades | Implementado |
| `/etc/ksc-web-console-setup.json` + `setup.js` do componente | Configuração do Web Console após a instalação do RPM | Observada | Chaves do arquivo e caminho do `setup.js` | Implementado e **exercitado em instalação real** |
| `/opt/kaspersky/ksc-web-console/server/config.json` | Ajuste de parâmetros do Web Console (JSON nativo) | Interna | Esquema do arquivo | Implementado · **alto risco de quebra** (Q2) |
| `/opt/kaspersky/ksc-web-console/server/core/env-local/web-server.js` | Inspeção/ajuste de binding do servidor web | Interna | Arquivo de implementação | Implementado · **alto risco de quebra** (Q2) |
| Bancos `ksc` e `ksciam` no PostgreSQL 16 | Tuning, reset controlado em laboratório, purge de MFA do IAM | Observada | Nomes e esquema das bases | Implementado · **não confirmado** (Q4) |
| Portas 443, 8080, 13000, 13291, 14000 | Pré-checagem de disponibilidade e regras nftables de hardening | Oficial | Documentação de portas do produto | Implementado |
| `LD_LIBRARY_PATH` para `/opt/kaspersky/ksc64/lib` | Pré-condição verificada antes de executar utilitários | Observada | Layout de diretórios | Implementado |
| Contextos SELinux sobre `/opt/kaspersky` e `/var/opt/kaspersky` | Verificação e ajuste no hardening | Observada | Política do SO e do produto | Implementado · não validado |
| API do Administration Server | Apenas verificação de alcançabilidade; **não consumimos a API** | Não utilizada | — | Fora de escopo · ver a nota de portas abaixo |
| Klakaut / SDK de automação | **Não utilizado** | — | — | Ver Q5 |

## 3.3 Uso declarado de superfícies frágeis

Registramos abertamente os três pontos em que dependemos de detalhe interno:

1. **`config.json` e `web-server.js` do Web Console.** São arquivos de
   implementação do produto. Nossa manipulação é feita por parsing JSON nativo
   (não por `sed`/regex, corrigido em revisão anterior), mas o esquema pode
   mudar entre versões sem aviso. Se a Kaspersky indicar um método suportado de
   configuração do Web Console, migraremos e removeremos esse acesso.
2. **`postinstall.pl` em modo silencioso para reconfiguração.** Usamos como
   caminho de reconfiguração de um servidor já instalado. **A validação E2E
   indica que esse uso não é previsto:** ao ser reexecutado em um servidor já
   configurado, o próprio instalador responde

   ```
   Fatal error: Kaspersky Security Center is successfully configured.
   Do not run the `postinstall.pl` script again.
   ```

   e encerra com código 1. Tratamos isso no fluxo de instalação, que passou a
   detectar servidores já configurados, mas a funcionalidade de reconfiguração
   em `automation/ops/reconfigure_ksc_service.py` continua apoiada nesse
   caminho. A pergunta Q1 deixou de ser "isto é suportado?" e passou a ser
   "qual é o caminho suportado?".
3. **Manipulação direta das bases `ksc`/`ksciam`.** Restrita a operações de
   laboratório (reset) e a uma operação de suporte (purge de MFA no IAM). Não
   lemos nem gravamos tabelas de negócio do produto em operação normal.

### Portas observadas em instalação real

A documentação do projeto e os pré-checks assumem um conjunto de portas que
não corresponde inteiramente ao que o produto abre. Verificado em
2026-09-12 sobre KSC 16.3.0.1207 em Rocky Linux 9.8:

| Porta | Assumida pelo projeto | Observada |
|---|---|---|
| 443 | Web Console HTTPS | Em escuta, após a configuração do componente |
| 13000 | Network Agent SSL | Em escuta (`klserver`) |
| 13291 | API do Administration Server | **Não está em escuta**; a porta OpenAPI ativa é a **13299** |
| 14000 | Network Agent plain | **Não está em escuta** |

O próprio repositório já divergia de si mesmo: o exemplo de configuração do Web
Console referenciava `openApiPort: 13299`, enquanto `automation/python/checks.py`
e a documentação verificavam a 13291. Isso alimenta a pergunta Q5.

## 3.4 Configuração exigida no alvo

- Rocky Linux 9.x ou Oracle Linux 9.x, com acesso `sudo` para a conta usada.
- PostgreSQL 16 local ou remoto, alcançável a partir do servidor KSC.
- FQDN do servidor resolvível — pré-condição verificada antes da instalação.
- Portas 443, 8080, 13000, 13291 e 14000 livres no momento da instalação.
- RPMs oficiais presentes no diretório informado a `packages --verify-dir`.

## 3.5 Compatibilidade

| Versão KSC | Ambiente | Resultado | Limitações | Evidência |
|---|---|---|---|---|
| **16.3.0.1207** | **Rocky Linux 9.8 + PostgreSQL 16** | **Testado — deploy completo bem-sucedido** | Validação E2E com deploy limpo, idempotência e métricas | `evidence/e2e-209/`, `evidence/e2e-228/`, `evidence/e2e-225/` |
| **16.3.0.1207** | **Oracle Linux 9.x (UEK R7 / RHCK) + PostgreSQL 16** | **Homologado — compatibilidade binária EL9** | Suporte verificado com PGDG PG16, Python 3.11 e SELinux Enforcing | [docs/02](../docs/02-matriz-compatibilidade.md), `infra/proxmox/` |
| **16.2.0.1023** | **Rocky Linux 9.x / EL9 + PostgreSQL 16** | **Homologado — pacotes oficiais e contratos CLI** | Suporte verificado via catálogo oficial e validação de contratos | `configs/ksc/packages.json`, `tests/test_packages.py` |
| 15.x | — | Inferido como possivelmente compatível | Fora do escopo principal de validação | Nenhuma |
| < 15.0 | — | Fora de escopo | — | — |
| Qualquer versão com MySQL/MariaDB | — | Não suportado | — | — |

Estado da compatibilidade: **matriz ampliada e comprovada em três combinações reais** (resolução da issue [#227](https://github.com/portosoft/ksc-deployment-runbook/issues/227)). O projeto cobre tanto a versão mais recente KSC 16.3.0.1207 quanto a versão anterior 16.2.0.1023, além de suportar integralmente o Oracle Linux 9 nas variantes Unbreakable Enterprise Kernel (UEK R7) e Red Hat Compatible Kernel (RHCK).

### 3.5.1 Divergências Arquiteturais Observadas entre KSC 16.2 e 16.3

A ampliação da matriz comprovada entre a linha 16.2 e 16.3 revelou divergências contratuais relevantes:

1. **Portas da API OpenAPI do Administration Server**:
   - **KSC 16.2.0.1023**: A porta documentada historicamente pela Kaspersky era a **13291** (SSL).
   - **KSC 16.3.0.1207**: A porta padrão ativa em tempo de execução passou a ser a **13299** (OpenAPI), enquanto a porta 13291 não escuta a menos que configurada manualmente. O runbook parametriza `openApiPort: 13299` no Web Console para assegurar comunicação correta.
2. **Pacote e Configuração do Web Console**:
   - **KSC 16.2**: Utiliza o pacote `ksc-web-console-16.2.11309.x86_64.rpm`, com esquemas de plugins mais simples.
   - **KSC 16.3**: Utiliza o pacote `ksc-web-console-16.3.12907.x86_64.rpm`, que introduz controles estritos de telemetria, autenticação integrada e drop-in de capacidade `CAP_NET_BIND_SERVICE` para escuta na porta privilegiada 443.
3. **Compatibilidade com o SGBD PostgreSQL**:
   - **KSC 16.2**: Desenvolvido e homologado originalmente pela Kaspersky com **PostgreSQL 15**. O uso com PostgreSQL 16 exige bibliotecas cliente `libpq` compatíveis e conexão com autenticação scram-sha-256.
   - **KSC 16.3**: Homologado nativamente pela Kaspersky com **PostgreSQL 16**, suportando plenamente a instalação local e remota sem necessidade de ajustes retroativos no driver.

## 3.6 Risco de quebra entre versões

| Superfície | Probabilidade de quebra em atualização menor do KSC | Impacto | Detecção atual |
|---|---|---|---|
| `config.json` / `web-server.js` do Web Console | Média a alta `[HIPÓTESE]` | Web Console mal configurado após deploy | Nenhuma automática `[LIMITAÇÃO]` |
| Arquivo de respostas do instalador | Média `[HIPÓTESE]` | Instalação falha ou usa padrões indesejados | Código de retorno do instalador |
| Nomes das unidades systemd | Baixa `[HIPÓTESE]` | Comandos de serviço falham | Código de retorno |
| Caminhos sob `/opt/kaspersky/ksc64` | Baixa `[HIPÓTESE]` | Utilitários não encontrados | Pré-checagem |
| Checksums dos RPMs | Alta por design (cada publicação) | Gate bloqueia instalação | Comparação SHA-256 — falha explícita e segura |
