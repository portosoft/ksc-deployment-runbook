# Requirements Document

## Introduction

Esta feature elimina todas as credenciais fixas com aparência realista (senhas, hostnames,
usuários) do código-fonte e dos arquivos de exemplo do repositório
`ksc-deployment-runbook`, substituindo-as por dois mecanismos complementares:

1. **Deploy real**: preenchimento manual interativo e seguro via CLI (`init_config.py`),
   nunca persistido no repositório.
2. **Testes automatizados**: geração aleatória e sintética em tempo de execução via
   `credentials.py` + fixtures pytest, nunca armazenada no repositório.

O escopo é restrito aos arquivos listados na seção de cada requisito. Nenhum diretório
novo será criado além dos já existentes no projeto.

---

## Glossary

- **Credential_Generator**: Módulo `automation/python/credentials.py`; responsável por gerar
  credenciais sintéticas criptograficamente seguras em tempo de execução para uso exclusivo
  em testes automatizados.
- **Init_Config**: Script `automation/python/init_config.py`; entrypoint interativo de linha
  de comando para preenchimento seguro de variáveis de ambiente de produção pelo operador.
- **Conftest**: Arquivo `tests/conftest.py`; fornece fixtures pytest que consomem o
  Credential_Generator e nunca persistem credenciais em disco além de `tmp_path`.
- **Factories**: Arquivo `tests/factories.py`; funções auxiliares que constroem instâncias
  de `CheckResult`/`CheckItem` para uso nos testes sem strings hardcoded.
- **Config_Module**: Módulo `automation/python/config.py`; carrega e valida as configurações
  de ambiente via pydantic, podendo usar vault ou .env como fonte.
- **Vault**: Módulo `automation/lib/vault.py`; fornece cifragem/decifragem de segredos via
  chave Fernet em `configs/vault.key` e `configs/secrets.bin`.
- **Secure_File_Writer**: Função `write_secure_file` em
  `automation/python/utils/secure_file.py`; escreve arquivos com permissões POSIX
  estritas (padrão `0o600`) de forma atômica.
- **FQDN**: Fully Qualified Domain Name — nome de host completo incluindo todos os rótulos
  de domínio (ex.: `ksc01.empresa.local`).
- **RFC 2606/6761**: RFCs que reservam domínios de teste como `.test`, `.example`,
  `.invalid`, `.localhost`; usados como base para FQDNs sintéticos.
- **detect-secrets**: Ferramenta de análise estática que detecta segredos e credenciais em
  arquivos de código-fonte.
- **Hostile_Password**: Senha sintética que contém deliberadamente caracteres especiais
  problemáticos (aspas simples, espaço, `;`, `&`, `$`, `(`, `)`) para testar robustez
  de escapamento em shells e SQL.
- **Credencial com aparência realista**: Qualquer string literal que `detect-secrets scan
  --no-baseline` classificaria como segredo, incluindo mas não limitado a: strings que
  correspondam a padrões de senha (entropia alta, prefixo `*_pass*`/`*_password*`/
  `*_secret*`), hostnames com TLDs reais (`.com`, `.net`, `.br`, `.local`, `.ts.net`,
  `.portosoft.*`), e nomes de usuário de banco de dados não-sintéticos.

---

## Requirements

### Requirement 1: Módulo de Geração de Credenciais Sintéticas

**User Story:** Como desenvolvedor, quero um módulo stdlib-only que gere credenciais
aleatórias criptograficamente seguras em tempo de execução, para que os testes
automatizados nunca precisem de strings fixas com aparência de dados reais no repositório.

#### Acceptance Criteria

1. THE Credential_Generator SHALL expor a função `generate_password(length=24, *, include_symbols=True)` que retorna uma string de exatamente `length` caracteres, usando exclusivamente `secrets.choice`, `string` e `uuid` da stdlib Python; o comprimento padrão é 24 e o máximo aceito é 256.
2. WHEN `generate_hostile_password(length=24)` é chamada, THE Credential_Generator SHALL retornar uma senha que contém pelo menos um caractere de cada um dos seguintes cinco conjuntos: aspas simples (`'`), espaço (` `), ponto-e-vírgula (`;`), ampersand (`&`), e a sequência literal `$(`).
3. THE Credential_Generator SHALL expor `generate_synthetic_fqdn()` que retorna um FQDN no formato `ksc-{hex8}.test`, onde `{hex8}` são exatamente 8 caracteres hexadecimais minúsculos derivados de `uuid.uuid4().hex[:8]`.
4. THE Credential_Generator SHALL expor `generate_username(prefix="testuser")` que retorna uma string no formato `{prefix}_{hex6}`, onde `{hex6}` são exatamente 6 caracteres hexadecimais minúsculos derivados de `uuid.uuid4().hex[:6]`.
5. THE Credential_Generator SHALL expor `generate_test_db_name(prefix="ksctest")` que retorna uma string no formato `{prefix}_{hex6}`, onde `{hex6}` são exatamente 6 caracteres hexadecimais minúsculos derivados de `uuid.uuid4().hex[:6]`.
6. WHEN qualquer função do Credential_Generator é chamada 1000 vezes consecutivas, THE Credential_Generator SHALL retornar pelo menos 999 valores distintos (propriedade de unicidade probabilística; aplica-se individualmente a cada função).
7. THE Credential_Generator SHALL importar exclusivamente módulos da biblioteca padrão Python (`secrets`, `string`, `uuid`); nenhuma dependência externa será introduzida.
8. WHEN `generate_password` é chamada com `include_symbols=False`, THE Credential_Generator SHALL retornar uma senha composta exclusivamente de caracteres presentes em `string.ascii_letters + string.digits`, sem nenhum símbolo ou espaço.
9. WHEN `generate_password` é chamada com `length` menor que 8 ou maior que 256, THE Credential_Generator SHALL lançar `ValueError` com mensagem no formato `"length deve estar entre 8 e 256, recebido: {length}"`.

---

### Requirement 2: Fixtures Pytest para Testes com Credenciais Sintéticas

**User Story:** Como desenvolvedor, quero fixtures pytest de escopo `function` que
forneçam credenciais sintéticas e ambientes de arquivo temporário, para que cada teste
receba valores únicos e isolados sem dependências de estado global.

#### Acceptance Criteria

1. THE Conftest SHALL definir a fixture `random_password` com escopo `function` que retorna o resultado de `generate_password()`.
2. THE Conftest SHALL definir a fixture `hostile_password` com escopo `function` que retorna o resultado de `generate_hostile_password()`.
3. THE Conftest SHALL definir a fixture `ksc_test_config` com escopo `function` que retorna uma instância de `KscConfig` onde os campos `db_password` e `ksc_admin_password` são preenchidos via `generate_password()`, e os campos `db_name`, `db_user` são preenchidos via `generate_test_db_name()` e `generate_username()` respectivamente; o campo `db_host` usa `"127.0.0.1"` e `db_port` usa `5432` como valores fixos permitidos para testes unitários.
4. WHEN a fixture `ksc_test_env_file(tmp_path)` é solicitada, THE Conftest SHALL criar um arquivo `.env` sintético em `tmp_path` usando `write_secure_file` com permissão `0o600`, contendo no mínimo as chaves `KSC_DB_HOST`, `KSC_DB_PORT`, `KSC_IAM_NAME`, `KSC_DB_USER`, `KSC_DB_PASS`, `KSC_ADMIN_PASS` e `KSC_WEB_PORT` em formato `KEY=value`, e retornar o caminho do arquivo criado como `pathlib.Path`.
5. WHEN dois testes distintos usam a fixture `random_password`, THE Conftest SHALL fornecer valores distintos para cada um em pelo menos 999 de 1000 pares de execuções (isolamento por escopo `function`, garantido pela unicidade probabilística do Credential_Generator).
6. THE Conftest SHALL importar exclusivamente o Credential_Generator, `KscConfig` e `write_secure_file`; nenhuma credencial literal será inserida no arquivo.

---

### Requirement 3: Factory de Objetos de Teste

**User Story:** Como desenvolvedor, quero funções factory para construir `CheckResult` e
`CheckItem` nos testes, para que não existam strings hardcoded de status ou mensagem
espalhadas pelos arquivos de teste.

#### Acceptance Criteria

1. THE Factories SHALL expor `make_check_item(name, status="ok", message="")` que retorna uma instância de `CheckItem` com os parâmetros fornecidos; o parâmetro `status` aceita qualquer string, mas os valores convencionais são `"ok"`, `"warning"` e `"critical"`, conforme definido em `checks.py`.
2. THE Factories SHALL expor `make_check_result(items=None)` que retorna uma instância de `CheckResult` com a lista de itens fornecida (padrão: lista vazia `[]`); IF `items` for `None`, THEN a instância retornada SHALL ter `items == []`.
3. THE Factories SHALL expor `make_critical_result(name="test_crit", message="Falha de teste")` que retorna um `CheckResult` contendo exatamente um `CheckItem` onde `CheckItem.name == name`, `CheckItem.status == "critical"` e `CheckItem.message == message`.
4. THE Factories SHALL importar apenas `CheckResult` e `CheckItem` de `automation.python.checks`; nenhuma outra dependência será introduzida.

---

### Requirement 4: Migração dos Testes Existentes

**User Story:** Como engenheiro de segurança, quero que todos os arquivos de teste sejam
livres de credenciais com aparência realista, para que `detect-secrets scan tests/` retorne
zero achados não autorizados.

#### Acceptance Criteria

1. WHEN `detect-secrets scan --no-baseline tests/` é executado após a migração, THE Test_Suite SHALL produzir zero achados de segredos nos arquivos `test_config.py`, `test_checks.py`, `test_ksc_audit.py` e `test_secure_file.py`; comentários do tipo `# pragma: allowlist secret` também deverão ser removidos dos arquivos migrados.
2. THE `test_config.py` SHALL substituir as strings com aparência de senha (conforme classificação do `detect-secrets`) por valores gerados em tempo de execução via `generate_password()` ou via fixture `random_password`, injetados no escopo do teste usando `monkeypatch.setenv` ou `unittest.mock.patch.dict(os.environ, {...})` como gerenciador de contexto.
3. THE `test_checks.py` SHALL substituir qualquer fixture ou variável local que contenha valores classificáveis como credencial pelo `detect-secrets` por valores gerados via Credential_Generator ou pela fixture `ksc_test_config` do Conftest.
4. WHEN qualquer teste em `test_checks.py`, `test_ksc_audit.py` ou `test_secure_file.py` precisar de um host, usuário ou senha, THE Test_Suite SHALL obtê-los exclusivamente do Credential_Generator ou das fixtures do Conftest.
5. THE Test_Suite SHALL manter o mesmo número de funções de teste existentes antes da migração; nenhuma função de teste existente será removida sem um substituto com nome equivalente e cobertura do mesmo comportamento.
6. WHEN a suíte completa de testes é executada via `pytest`, THE Test_Suite SHALL passar sem erros de importação e sem falhas de asserção; o resultado do `detect-secrets scan --no-baseline tests/` deverá ser zero achados.

---

### Requirement 5: Entrypoint Interativo de Configuração (`init_config.py`)

**User Story:** Como operador de implantação, quero um script interativo de linha de
comando que me guie no preenchimento seguro das variáveis de ambiente de produção, para
que eu nunca precise editar manualmente arquivos `.env` com risco de vazar credenciais no
histórico do shell ou em logs.

#### Acceptance Criteria

1. THE Init_Config SHALL solicitar via `input()` os campos não-sensíveis (`KSC_DB_HOST`, `KSC_DB_PORT`, `KSC_DB_USER`, `KSC_FQDN`, `KSC_HOST`, `KSC_USER`, `KSC_WEB_PORT`, `KSC_SELINUX_MODE`) exibindo o valor padrão sugerido entre colchetes no prompt, no formato `"Nome do campo [valor_padrão]: "`.
2. THE Init_Config SHALL solicitar via `getpass.getpass()` os campos sensíveis (`KSC_DB_PASS`, `KSC_ADMIN_PASS`, `KSC_PASS`) com um prompt que não inclui o valor atual ou padrão, garantindo que o valor digitado não seja exibido no terminal em nenhum sistema operacional suportado.
3. WHEN um valor fornecido pelo operador falha na validação do Config_Module, THE Init_Config SHALL exibir a mensagem de erro do validador prefixada por `"Valor inválido: "` e solicitar o mesmo campo novamente em loop, sem encerrar o programa.
4. WHEN o arquivo `configs/env/ksc_vars.env` já existir, THE Init_Config SHALL exibir a lista de chaves que seriam adicionadas, removidas ou alteradas (sem exibir os valores atuais ou novos de campos sensíveis `*_PASS`/`*_PASSWORD`) e solicitar confirmação com `[s/N]` antes de prosseguir.
5. WHEN confirmado pelo operador (resposta `"s"` ou `"S"`), THE Init_Config SHALL escrever `configs/env/ksc_vars.env` usando o Secure_File_Writer com permissão `0o600`; IF o operador responder qualquer outra coisa, THEN o script SHALL encerrar sem escrever o arquivo.
6. THE Init_Config SHALL ser executável via `python3 -m automation.python.init_config` a partir da raiz do repositório, sem necessidade de configuração adicional de `PYTHONPATH`.
7. WHERE a flag `--vault` é fornecida na linha de comando, THE Init_Config SHALL, após escrever o arquivo `.env`, chamar `vault.encrypt_secrets()` com um dicionário contendo exclusivamente os campos sensíveis coletados (`KSC_DB_PASS`, `KSC_ADMIN_PASS`, `KSC_PASS`) e gravar o resultado em `configs/secrets.bin` com permissão `0o600`.
8. THE Init_Config SHALL importar exclusivamente módulos da stdlib Python (`argparse`, `getpass`, `sys`, `os`, `pathlib`, `difflib`) e módulos internos do projeto (`config.py`, `secure_file.py`, `vault.py`); nenhuma dependência externa será introduzida.
9. IF ocorrer um erro de I/O ao escrever `configs/env/ksc_vars.env`, THEN THE Init_Config SHALL exibir a mensagem de erro do sistema operacional, encerrar com código de saída `1` e garantir que nenhum arquivo parcial permaneça em disco (usar escrita atômica via arquivo temporário + rename).

---

### Requirement 6: Ajustes de Validação no Config_Module

**User Story:** Como desenvolvedor, quero que o `config.py` valide o FQDN e o `db_sslmode`
explicitamente e suporte decifragem via vault, para que configurações inválidas sejam
rejeitadas na inicialização e o fluxo de secrets seja unificado.

#### Acceptance Criteria

1. IF o campo `ksc_fqdn` (ou equivalente de hostname) receber um valor que não satisfaça pelo menos uma das seguintes condições: (a) hostname simples de até 63 caracteres alfanuméricos e hífens sem iniciar/terminar com hífen, (b) FQDN com cada rótulo ≤ 63 caracteres, total ≤ 253 caracteres, ou (c) endereço IPv4 com cada octeto entre 0 e 255, THEN THE Config_Module SHALL lançar `ConfigError`.
2. IF o campo `db_sslmode` receber qualquer valor não pertencente ao conjunto `{"disable", "prefer", "require", "verify-ca", "verify-full"}`, THEN THE Config_Module SHALL lançar `ConfigError`.
3. WHEN `load_config()` é chamada e `configs/secrets.bin` existe no sistema de arquivos, THE Config_Module SHALL tentar decifrar os segredos via `vault.decrypt_secrets()` e mesclar os valores decifrados sobre os valores carregados do arquivo `.env` (os valores do vault têm precedência para chaves coincidentes); IF a decifragem falhar por qualquer razão, THEN THE Config_Module SHALL registrar um aviso em nível `WARNING` via `logging` e usar exclusivamente os valores do arquivo `.env`.
4. IF o arquivo `.env` configurado não existir no momento de `load_config()`, THEN THE Config_Module SHALL lançar `ConfigError` com mensagem descritiva, independentemente de `configs/secrets.bin` existir ou não.

> **Nota:** Os validadores de `ksc_fqdn` e `db_sslmode` já existem parcialmente em
> `config.py`; este requisito formaliza e documenta o contrato esperado. A adição do
> suporte a vault é o delta principal.

---

### Requirement 7: Sanitização dos Arquivos `.example`

**User Story:** Como engenheiro de segurança, quero que todos os arquivos `.example` de
configuração usem marcadores de placeholder ao invés de valores com aparência de dados
reais, para que nenhuma credencial ou hostname real seja acidentalmente copiado para
produção a partir de um template.

#### Acceptance Criteria

1. THE `configs/examples/ksc.env.example` SHALL substituir todo valor que `detect-secrets scan --no-baseline` classificaria como segredo, e todo hostname com TLD real (`.com`, `.net`, `.br`, `.local`, `.portosoft.*`, `.ts.net`), pelo marcador `<PREENCHER: instrução específica>` onde a instrução descreve como obter o valor correto.
2. THE `configs/env/ksc_vars.env.example` SHALL substituir todo valor que `detect-secrets scan --no-baseline` classificaria como segredo, e todo hostname com TLD real, pelo marcador `<PREENCHER: instrução específica>`.
3. WHEN `detect-secrets scan --no-baseline configs/` é executado, THE Example_Files SHALL produzir zero achados de segredos em ambos os arquivos `.example`.
4. THE `ksc.env.example` SHALL incluir a variável `KSC_DB_PASS` com o valor exato `<PREENCHER: gerar com openssl rand -base64 24>`.
5. THE `ksc_vars.env.example` SHALL incluir todas as seguintes variáveis, cada uma com marcador `<PREENCHER: ...>`: `KSC_DB_HOST`, `KSC_DB_PORT`, `KSC_DB_USER`, `KSC_DB_PASS`, `KSC_ADMIN_PASS`, `KSC_FQDN`, `KSC_HOST`, `KSC_USER`, `KSC_PASS`, `KSC_WEB_PORT`, `KSC_SELINUX_MODE`.

---

### Requirement 8: Atualização da Documentação Operacional

**User Story:** Como operador de implantação, quero que a documentação e o checklist
reflitam o novo fluxo de configuração via `init_config.py`, para que eu saiba exatamente
quando e como executar o script antes do pre-check.

#### Acceptance Criteria

1. THE `docs/03-pre-requisitos.md` SHALL incluir um passo numerado "2.5" posicionado imediatamente antes do passo que descreve a execução do `ksc_audit.py --check`, contendo: (a) o comando exato `python3 -m automation.python.init_config`, (b) a instrução de que o resultado não deve ser commitado, e (c) uma nota sobre a flag `--vault` informando que ela grava credenciais cifradas em `configs/secrets.bin`.
2. THE `CHECKLIST.md` SHALL incluir o item `- [ ] \`init_config.py\` executado interativamente pelo operador (sem .env copiado de outro host)` na seção "📂 5. Execução do Runbook (Pre-check)", como primeiro item desta seção.
3. THE `CHANGELOG.md` SHALL incluir uma nova entrada no bloco `[Unreleased]` (ou criar tal bloco no topo se não existir) com exatamente: `Added: geração sintética de credenciais para testes (credentials.py + fixtures); Added: init_config.py para configuração interativa segura; Changed: arquivos .example agora usam marcadores <PREENCHER>`.
4. WHEN um operador lê `docs/03-pre-requisitos.md`, THE Documentation SHALL fornecer: (a) o comando exato para executar o Init_Config, (b) a lista de variáveis que serão solicitadas interativamente, (c) instrução explícita de não commitar o arquivo gerado, e (d) referência à flag `--vault` e seu efeito.
