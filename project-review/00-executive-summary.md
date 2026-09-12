# KSC Deployment Runbook: arquitetura, integração e proposta de colaboração técnica com o Kaspersky Security Center 16.x para Linux

**Resumo executivo** — versão 2026-09-12 · branch `develop` · commit `704a9bd`

---

## O que é

O **KSC Deployment Runbook** é um projeto open-source (Apache 2.0) que
padroniza, automatiza e audita a implantação do **Kaspersky Security Center
16.x Administration Server** e do **KSC Web Console** em Rocky Linux 9 e Oracle
Linux 9 com PostgreSQL 16. Ele combina uma trilha documental de 14 etapas
numeradas com uma CLI Python (`kscctl`) que executa pré-checagens, verificação
de integridade de pacotes, instalação, hardening e coleta de evidências
auditáveis. `[FATO]`

## Problema que resolve

A instalação do KSC em Linux é um procedimento com muitas variáveis de
ambiente sensíveis — SELinux, `LD_LIBRARY_PATH`, permissões de
`/opt/kaspersky`, parâmetros do PostgreSQL, portas 443/8080/13000/13291/14000,
configuração do Web Console e do serviço IAM. Executado manualmente, o
procedimento é difícil de repetir de forma idêntica entre servidores e não
produz trilha de auditoria. O projeto transforma esse procedimento em um fluxo
executável, idempotente no modo de verificação, e com registro estruturado em
JSON de cada comando executado. `[FATO]` quanto à existência do fluxo;
`[HIPÓTESE]` quanto à redução mensurada de tempo ou de erro humano, pois não há
medição comparativa.

## Como usa a ferramenta principal

O projeto **não modifica e não reimplementa** nenhum componente do KSC. Ele
opera exclusivamente nas superfícies de instalação e operação já expostas pela
distribuição Linux do produto: pacotes RPM oficiais verificados por SHA-256,
instalação silenciosa via `postinstall.pl` com arquivo de respostas, unidades
systemd (`kladminserver_srv`, `klnagent_srv`, `ksc-web-console`, `kliam_srv`),
utilitários em `/opt/kaspersky/ksc64/sbin`, o arquivo
`/opt/kaspersky/ksc-web-console/server/config.json` e os bancos `ksc` e `ksciam`
no PostgreSQL. `[FATO]` — detalhamento e classificação de cada interface em
[03-integration-with-main-tool.md](03-integration-with-main-tool.md).

Parte dessas superfícies é documentada pela Kaspersky; outra parte é **baseada
em comportamento observado** e constitui o principal ponto de fragilidade da
integração — é exatamente sobre ela que buscamos orientação.

## Estado atual

Maturidade classificada como **MVP / Beta inicial**: 108 testes unitários
passam localmente, 11 workflows de CI (incluindo CodeQL, Semgrep e verificação
de baseline de segredos) estão ativos, e a documentação operacional está
completa. Contudo, quatro funções centrais de `setup_steps.py` ainda são mocks
declarados no código, não existe validação end-to-end em servidor real
registrada, e os artefatos em `evidence/` são saídas de execução de testes com
transporte SSH simulado — **não são evidências de deploy real**. `[FATO]`

## O que pedimos à equipe Kaspersky

Não pedimos endosso nem apoio genérico. Pedimos cinco itens objetivos,
detalhados em [07-collaboration-proposal.md](07-collaboration-proposal.md):

1. Confirmação de quais interfaces que utilizamos são **contratos estáveis** e
   quais podem mudar sem aviso entre versões menores do KSC 16.x.
2. Orientação sobre o método suportado para **reconfigurar** um Administration
   Server já instalado sem reinstalação.
3. Confirmação do **formato canônico do arquivo de respostas** da instalação
   silenciosa e de suas chaves obrigatórias.
4. Revisão do nosso manuseio de segredos e do **modelo de privilégio** exigido
   pelos comandos que executamos.
5. Definição da forma de referência ao produto aceitável do ponto de vista de
   **marca e licenciamento** para um projeto de terceiros.

## Prontidão

**Pronto para discussão inicial e revisão técnica de arquitetura; não pronto
para piloto, submissão formal ou upstream.** A lacuna que impede os estágios
seguintes é única e conhecida: ausência de validação end-to-end em ambiente
real. O plano para fechá-la está em [09-roadmap.md](09-roadmap.md), que passa a
ser o **único backlog válido do projeto**.
