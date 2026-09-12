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
| `/opt/kaspersky/ksc-web-console/server/config.json` | Ajuste de parâmetros do Web Console (JSON nativo) | Interna | Esquema do arquivo | Implementado · **alto risco de quebra** (Q2) |
| `/opt/kaspersky/ksc-web-console/server/core/env-local/web-server.js` | Inspeção/ajuste de binding do servidor web | Interna | Arquivo de implementação | Implementado · **alto risco de quebra** (Q2) |
| Bancos `ksc` e `ksciam` no PostgreSQL 16 | Tuning, reset controlado em laboratório, purge de MFA do IAM | Observada | Nomes e esquema das bases | Implementado · **não confirmado** (Q4) |
| Portas 443, 8080, 13000, 13291, 14000 | Pré-checagem de disponibilidade e regras nftables de hardening | Oficial | Documentação de portas do produto | Implementado |
| `LD_LIBRARY_PATH` para `/opt/kaspersky/ksc64/lib` | Pré-condição verificada antes de executar utilitários | Observada | Layout de diretórios | Implementado |
| Contextos SELinux sobre `/opt/kaspersky` e `/var/opt/kaspersky` | Verificação e ajuste no hardening | Observada | Política do SO e do produto | Implementado · não validado |
| API do Administration Server (porta 13291) | Apenas verificação de alcançabilidade; **não consumimos a API** | Não utilizada | — | Fora de escopo atual |
| Klakaut / SDK de automação | **Não utilizado** | — | — | Ver Q5 |

## 3.3 Uso declarado de superfícies frágeis

Registramos abertamente os três pontos em que dependemos de detalhe interno:

1. **`config.json` e `web-server.js` do Web Console.** São arquivos de
   implementação do produto. Nossa manipulação é feita por parsing JSON nativo
   (não por `sed`/regex, corrigido em revisão anterior), mas o esquema pode
   mudar entre versões sem aviso. Se a Kaspersky indicar um método suportado de
   configuração do Web Console, migraremos e removeremos esse acesso.
2. **`postinstall.pl` em modo silencioso para reconfiguração.** Usamos como
   caminho de reconfiguração de um servidor já instalado. Não sabemos se esse é
   o uso previsto do script.
3. **Manipulação direta das bases `ksc`/`ksciam`.** Restrita a operações de
   laboratório (reset) e a uma operação de suporte (purge de MFA no IAM). Não
   lemos nem gravamos tabelas de negócio do produto em operação normal.

## 3.4 Configuração exigida no alvo

- Rocky Linux 9.x ou Oracle Linux 9.x, com acesso `sudo` para a conta usada.
- PostgreSQL 16 local ou remoto, alcançável a partir do servidor KSC.
- FQDN do servidor resolvível — pré-condição verificada antes da instalação.
- Portas 443, 8080, 13000, 13291 e 14000 livres no momento da instalação.
- RPMs oficiais presentes no diretório informado a `packages --verify-dir`.

## 3.5 Compatibilidade

| Versão KSC | Ambiente | Resultado | Limitações | Evidência |
|---|---|---|---|---|
| 16.x | Rocky Linux 9 + PostgreSQL 16 | **Alvo declarado** | Nenhum deploy end-to-end registrado | Declaração de escopo em `README.md` e `docs/02-matriz-compatibilidade.md` |
| 16.x | Oracle Linux 9 + PostgreSQL 16 | **Alvo declarado** | Idem | Idem |
| 15.x | — | Inferido como possivelmente compatível | Nunca exercitado | Nenhuma |
| < 15.0 | — | Fora de escopo | — | — |
| Qualquer versão com MySQL/MariaDB | — | Não suportado | — | — |

Estado da compatibilidade: **declarada e inferida, não testada e não confirmada
pelos mantenedores.** Esta é a afirmação mais importante deste pacote e não a
apresentamos de outra forma. Nenhuma célula da tabela acima deve ser lida como
"validado".

Estratégia de versionamento pretendida: SemVer, com a versão menor do KSC
suportada declarada explicitamente em cada release e um teste de fumaça por
versão do produto. Hoje o projeto não possui tag de release. `[FATO]`

## 3.6 Risco de quebra entre versões

| Superfície | Probabilidade de quebra em atualização menor do KSC | Impacto | Detecção atual |
|---|---|---|---|
| `config.json` / `web-server.js` do Web Console | Média a alta `[HIPÓTESE]` | Web Console mal configurado após deploy | Nenhuma automática `[LIMITAÇÃO]` |
| Arquivo de respostas do instalador | Média `[HIPÓTESE]` | Instalação falha ou usa padrões indesejados | Código de retorno do instalador |
| Nomes das unidades systemd | Baixa `[HIPÓTESE]` | Comandos de serviço falham | Código de retorno |
| Caminhos sob `/opt/kaspersky/ksc64` | Baixa `[HIPÓTESE]` | Utilitários não encontrados | Pré-checagem |
| Checksums dos RPMs | Alta por design (cada publicação) | Gate bloqueia instalação | Comparação SHA-256 — falha explícita e segura |
