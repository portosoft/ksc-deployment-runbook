# 11. Mensagem de encaminhamento

Texto pronto para envio. Preencher os campos entre colchetes e anexar ou
referenciar o pacote em `project-review/`. Enviar somente após concluir o
checklist de [10 §10.2](10-submission-checklist.md).

---

Assunto: **KSC Deployment Runbook — pedido de revisão técnica de integração (projeto independente, Apache 2.0)**

Olá,

Apresentamos o **KSC Deployment Runbook**, um projeto open-source independente
sob licença Apache 2.0 que automatiza e audita a implantação do **Kaspersky
Security Center 16.x Administration Server e Web Console** em Rocky Linux 9 e
Oracle Linux 9 com PostgreSQL 16. O projeto não tem vínculo com a AO Kaspersky
Lab e não redistribui nenhum artefato do produto.

O projeto nasceu da dificuldade de executar a instalação do KSC em Linux de
forma repetível entre servidores e de produzir trilha de auditoria do que foi
configurado. Ele oferece pré-checagens automatizadas de SO, DNS, portas e
PostgreSQL; verificação obrigatória de SHA-256 dos pacotes oficiais antes de
qualquer instalação; instalação silenciosa parametrizada por arquivo de
respostas; hardening documentado; e registro estruturado em JSON de cada
comando executado.

A integração usa apenas superfícies do produto: pacotes RPM oficiais,
`postinstall.pl` em modo silencioso, utilitários em `/opt/kaspersky/ksc64/sbin`,
as unidades systemd `kladminserver_srv`, `klnagent_srv`, `ksc-web-console` e
`kliam_srv`, o `config.json` do Web Console e as bases `ksc` e `ksciam` no
PostgreSQL. O mapa completo, com cada interface classificada como documentada,
pública ou baseada em comportamento observado, está em
`03-integration-with-main-tool.md`.

Sobre o estado atual, queremos ser precisos: o projeto está em estágio de
**Beta**. Em 12/09/2026 executamos o ciclo completo contra um **KSC
16.3.0.1207 real**, instalado a partir dos RPMs oficiais em Rocky Linux 9.8 com
PostgreSQL 16: a instalação concluiu com sucesso, o Web Console respondeu em
HTTPS e o relatório de auditoria foi gerado sem falhas críticas. Essa execução
revelou dez defeitos no nosso próprio código, todos corrigidos.

Ainda assim, **não afirmamos compatibilidade comprovada com o KSC 16.x em
geral**: validamos **uma combinação**, em **uma execução de laboratório**.
Oracle Linux 9 e outras versões seguem apenas declaradas, o rollback nunca foi
exercitado e não coletamos nenhuma métrica de desempenho. As limitações estão
listadas integralmente em `06-known-limitations.md`.

Neste momento buscamos uma revisão técnica focada em três pontos em que
dependemos de comportamento observado e não de documentação:

1. Qual é o caminho suportado para reconfigurar um Administration Server já
   instalado? Verificamos que o `postinstall.pl` recusa reexecução
   ("Do not run the `postinstall.pl` script again"), então o caminho que
   usávamos não serve.
2. Existe forma suportada de configurar o KSC Web Console em Linux sem editar
   `config.json` e `web-server.js`? Esses arquivos devem ser considerados
   internos?
3. Qual é o conjunto canônico de chaves do arquivo de respostas da instalação
   silenciosa, e esse formato é estável dentro da linha 16.x?

Além dessas, temos quatro perguntas sobre interface programática, privilégios
mínimos e uso de marca, todas em `08-maintainer-questions.md`.

Não estamos pedindo endosso, inclusão em ecossistema oficial, alteração no
produto nem suporte aos nossos usuários. Se qualquer uso que fazemos for
considerado impróprio, nos comprometemos a ajustá-lo ou removê-lo.

Podemos disponibilizar: o repositório completo, o ambiente de laboratório
reproduzível (Proxmox em container, provisionado por script), os logs
estruturados do deploy real, os resultados de testes e de CI, os diagramas de
arquitetura e um conjunto de casos concretos de falha de instalação em Linux —
incluindo comportamentos do instalador e nomes de unidades systemd que
divergem da documentação pública e que talvez sejam úteis como insumo para a
documentação do produto.

Agradecemos qualquer orientação que torne esta integração mais compatível,
segura e sustentável.

Atenciosamente,

[NOME]
KSC Deployment Runbook — https://github.com/portosoft/ksc-deployment-runbook
[CONTATO]
