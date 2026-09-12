# 8. Perguntas técnicas aos mantenedores

Sete perguntas. Cada uma existe porque uma decisão concreta do projeto depende
da resposta.

---

### Q1 — Reconfiguração de um Administration Server já instalado

**Pergunta.** Qual é o método suportado para reconfigurar um KSC 16.x
Administration Server já instalado em Linux sem reinstalá-lo? A execução de
`/opt/kaspersky/ksc64/lib/bin/setup/postinstall.pl` em modo silencioso com um
arquivo de respostas é um uso previsto?

**Contexto.** É o caminho que utilizamos em `automation/ops/reconfigure_ksc_service.py`. Foi derivado de comportamento observado, não de documentação.

**Por que importa.** Se não for suportado, estamos expondo usuários a um estado não previsto pelo produto.

**Decisão que depende.** Manter, substituir ou remover completamente a funcionalidade de reconfiguração.

---

### Q2 — Configuração do Web Console

**Pergunta.** Existe uma forma suportada de configurar o KSC Web Console em
Linux (porta, binding, parâmetros de servidor) que não envolva editar
`/opt/kaspersky/ksc-web-console/server/config.json` ou
`server/core/env-local/web-server.js`? Esses arquivos devem ser considerados
internos e sujeitos a mudança sem aviso?

**Contexto.** Editamos `config.json` por parsing JSON nativo. É a dependência mais frágil do projeto (L-04).

**Por que importa.** Uma mudança de esquema em atualização menor quebraria o deploy silenciosamente, sem detecção.

**Decisão que depende.** Migrar para o método indicado, ou manter e adicionar verificação de esquema com falha explícita por versão.

---

### Q3 — Arquivo de respostas da instalação silenciosa

**Pergunta.** Qual é o conjunto canônico de chaves do arquivo de respostas da
instalação silenciosa do KSC 16.x em Linux, quais são obrigatórias, e esse
formato tem garantia de estabilidade dentro da linha 16.x?

**Contexto.** Nosso template é `configs/ksc/ksc_response.txt.template` (AD-4).

**Por que importa.** A reprodutibilidade entre servidores depende inteiramente da estabilidade desse formato.

**Decisão que depende.** Geração estática do arquivo de respostas versus geração dinâmica por versão detectada do produto.

---

### Q4 — Manipulação das bases `ksc` e `ksciam`

**Pergunta.** A sequência de rollback que documentamos — parar
`kladminserver_srv`, `klnagent_srv`, `ksc-web-console` e `kliam_srv`, encerrar
conexões com `pg_terminate_backend`, executar `DROP DATABASE ... IF EXISTS` e
remover o usuário de aplicação — é segura e completa do ponto de vista do
produto? Há algum estado fora do PostgreSQL (arquivos, certificados, chaves em
`/var/opt/kaspersky`) que precise ser removido na mesma operação?

**Contexto.** `docs/11-rollback.md` e `automation/ops/reset_ksc_databases.py`.

**Por que importa.** Um rollback incompleto deixa o servidor em estado que impede reinstalação limpa.

**Decisão que depende.** Escopo do procedimento de rollback e se ele pode ser automatizado com segurança (R-06).

---

### Q5 — Interface programática de automação

**Pergunta.** Para automação de configuração pós-instalação em Linux, a
recomendação é utilizar a API do Administration Server (porta 13291), o SDK
Klakaut, ou nenhuma das duas? Há paridade de funcionalidade entre a
distribuição Linux e a Windows nesse aspecto?

**Contexto.** Hoje apenas verificamos alcançabilidade da porta 13291; não consumimos API alguma.

**Por que importa.** Substituir manipulação de arquivos por chamadas de API eliminaria a maior parte das dependências frágeis do projeto.

**Decisão que depende.** Se a automação pós-instalação evolui por API ou permanece por arquivos e utilitários de linha de comando.

---

### Q6 — Privilégios mínimos

**Pergunta.** Qual é o conjunto mínimo de privilégios necessário para instalar,
reconfigurar e auditar o KSC 16.x em Linux? As operações exigem `root` pleno ou
podem ser delegadas por regras `sudo` específicas?

**Contexto.** Hoje assumimos `sudo` amplo, o que torna o host de administração um host privilegiado (§4.3).

**Por que importa.** É a principal recomendação de segurança pendente do projeto.

**Decisão que depende.** Documentar e restringir o modelo de privilégio exigido do operador (R-04).

---

### Q7 — Marca, nomenclatura e conformidade

**Pergunta.** Qual é a forma aceitável de um projeto independente sob Apache
2.0 referenciar o Kaspersky Security Center no nome do repositório, na
documentação e em material público? Há restrição quanto a referenciar as URLs
oficiais de download dos pacotes e a publicar seus hashes SHA-256?

**Contexto.** O nome do projeto contém "KSC"; publicamos um catálogo de checksums em `configs/ksc/checksums.sha256`. Não redistribuímos nenhum artefato.

**Por que importa.** Queremos estar em conformidade antes de qualquer divulgação.

**Decisão que depende.** Nome do projeto, conteúdo do aviso de não afiliação, e manutenção ou remoção do catálogo público de checksums.
