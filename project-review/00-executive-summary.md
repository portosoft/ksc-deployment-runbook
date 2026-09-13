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

Maturidade classificada como **Beta**: 144 testes unitários passam localmente,
11 workflows de CI (incluindo CodeQL, Semgrep e verificação de baseline de
segredos) estão ativos, e a documentação operacional está completa. Em
2026-09-12 o ciclo completo foi executado contra um **KSC 16.3.0.1207 real**,
instalado a partir dos RPMs oficiais em Rocky Linux 9.8 com PostgreSQL 16:
`setup --apply` concluiu com código 0, o Web Console respondeu em HTTPS e o
relatório de auditoria foi gerado sem falhas críticas. `[OBSERVADO]`

Essa execução revelou **dez defeitos** que nenhum teste unitário detectaria —
entre eles o fato de que o hardening proposto pelo próprio runbook deixava o
Administration Server inoperante. Todos foram corrigidos e cobertos por testes
de regressão. A validação cobre **uma combinação**; Oracle Linux 9 e outras
versões do KSC seguem apenas declaradas. `[LIMITAÇÃO]`

## O que pedimos à equipe Kaspersky

Não pedimos endosso nem apoio genérico. Pedimos cinco itens objetivos,
detalhados em [07-collaboration-proposal.md](07-collaboration-proposal.md):

1. Confirmação de quais interfaces que utilizamos são **contratos estáveis** e
   quais podem mudar sem aviso entre versões menores do KSC 16.x.
2. Orientação sobre o método suportado para **reconfigurar** um Administration
   Server já instalado — o `postinstall.pl` recusa reexecução com
   *"Do not run the postinstall.pl script again"*, de modo que a pergunta não
   é mais se o caminho que usávamos é suportado, mas qual é o suportado.
3. Confirmação do **formato canônico do arquivo de respostas** da instalação
   silenciosa e de suas chaves obrigatórias.
4. Revisão do nosso manuseio de segredos e do **modelo de privilégio** exigido
   pelos comandos que executamos.
5. Definição da forma de referência ao produto aceitável do ponto de vista de
   **marca e licenciamento** para um projeto de terceiros.

## Prontidão

**Pronto para revisão técnica; não pronto para piloto, submissão formal ou
upstream.** A ausência de validação end-to-end, que antes bloqueava qualquer
avanço, foi resolvida pela issue [#209](https://github.com/portosoft/ksc-deployment-runbook/issues/209). O que separa o projeto de um
piloto agora é menor e está enumerado: rollback nunca exercitado
([#223](https://github.com/portosoft/ksc-deployment-runbook/issues/223)), idempotência não medida ([#228](https://github.com/portosoft/ksc-deployment-runbook/issues/228)), matriz de
compatibilidade com uma única combinação testada ([#227](https://github.com/portosoft/ksc-deployment-runbook/issues/227)) e o
manuseio de segredos ([#101](https://github.com/portosoft/ksc-deployment-runbook/issues/101)).
O backlog completo está no [board do projeto](https://github.com/orgs/portosoft/projects/1);
[09-roadmap.md](09-roadmap.md) apresenta a visão dele para o leitor externo.
