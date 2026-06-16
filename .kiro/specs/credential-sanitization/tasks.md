# Implementation Plan: credential-sanitization

## Overview

Eliminar todas as credenciais fixas com aparência realista do repositório substituindo-as
por geração sintética em testes (via `credentials.py` + fixtures pytest) e configuração
interativa segura para produção (via `init_config.py`). Os módulos existentes
(`config.py`, `checks.py`, `secure_file.py`, arquivos de teste) serão ajustados para
não conter nenhuma string classificável como segredo.

## Tasks

- [x] 1. Criar o módulo `credentials.py` com todas as funções geradoras
  - [x] 1.1 Implementar `generate_password`, `generate_hostile_password`, `generate_synthetic_fqdn`, `generate_username` e `generate_test_db_name` em `automation/python/credentials.py`
    - Criar o arquivo `automation/python/credentials.py` usando exclusivamente stdlib (`secrets`, `string`, `uuid`)
    - Implementar `generate_password(length=24, *, include_symbols=True)` retornando string de comprimento exato; lançar `ValueError` para `length < 8` ou `> 256`
    - Implementar `generate_hostile_password(length=24)` garantindo por construção que a string contém `'`, ` `, `;`, `&` e `$(`
    - Implementar `generate_synthetic_fqdn()` retornando string no formato `ksc-{hex8}.test`
    - Implementar `generate_username(prefix="testuser")` e `generate_test_db_name(prefix="ksctest")` no formato `{prefix}_{hex6}`
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.7, 1.8, 1.9_

  - [x] 1.2 Escrever testes de propriedade para `generate_password` (Properties 1, 2, 3)
    - Criar `tests/test_credentials.py`
    - **Property 1: `generate_password` retorna string de comprimento exato**
    - **Property 2: `include_symbols=False` retorna apenas alfanuméricos**
    - **Property 3: comprimento inválido lança `ValueError`**
    - **Validates: Requirements 1.1, 1.8, 1.9**

  - [x] 1.3 Escrever testes de propriedade para `generate_hostile_password`, `generate_synthetic_fqdn`, `generate_username` e `generate_test_db_name` (Properties 4, 5, 6, 7)
    - Adicionar ao `tests/test_credentials.py`
    - **Property 4: `generate_hostile_password` sempre contém todos os cinco conjuntos obrigatórios**
    - **Property 5: `generate_synthetic_fqdn` sempre respeita o formato `ksc-{hex8}.test`**
    - **Property 6: `generate_username` e `generate_test_db_name` respeitam seus formatos**
    - **Property 7: unicidade probabilística das funções geradoras**
    - **Validates: Requirements 1.2, 1.3, 1.4, 1.5, 1.6**

  - [x] 1.4 Escrever testes de exemplo para `credentials.py`
    - Testar comprimento padrão, prefixos padrão e casos de borda (length=8, length=256)
    - _Requirements: 1.1, 1.3, 1.4, 1.5_

- [x] 2. Criar `tests/factories.py` e `tests/conftest.py`
  - [x] 2.1 Implementar `tests/factories.py` com as funções factory de objetos de teste
    - Criar `tests/factories.py` importando apenas `CheckResult` e `CheckItem` de `automation.python.checks`
    - Implementar `make_check_item(name, status="ok", message="")`, `make_check_result(items=None)` e `make_critical_result(name="test_crit", message="Falha de teste")`
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [x] 2.2 Escrever testes de propriedade para `make_check_item` e `make_critical_result` (Property 10)
    - Adicionar ao `tests/test_credentials_properties.py` (arquivo novo)
    - **Property 10: `make_check_item` e `make_critical_result` preservam os parâmetros fornecidos**
    - **Validates: Requirements 3.1, 3.3**

  - [x] 2.3 Implementar `tests/conftest.py` com as fixtures pytest
    - Criar `tests/conftest.py` importando `credentials`, `KscConfig` e `write_secure_file`
    - Definir `random_password`, `hostile_password`, `ksc_test_config` e `ksc_test_env_file` com escopo `function`
    - `ksc_test_config` usa `db_host="127.0.0.1"`, `db_port=5432` e campos sensíveis via `generate_password()`
    - `ksc_test_env_file(tmp_path)` cria arquivo `.env` em `tmp_path` com `write_secure_file` (permissão `0o600`)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

- [x] 3. Checkpoint — Verificar módulos base
  - Garantir que `pytest tests/test_credentials.py tests/test_credentials_properties.py` passa sem erros. Perguntar ao usuário se houver dúvidas antes de prosseguir.

- [x] 4. Ajustar `config.py` para suporte a vault e default de FQDN seguro
  - [x] 4.1 Atualizar `automation/python/config.py` com suporte a vault e default não-realista
    - Substituir o default `ksc_fqdn="kscserver.exemplo.ts.net"` por `ksc_fqdn="ksc-placeholder.test"`
    - Atualizar `load_config()` para carregar `configs/secrets.bin` via `vault.decrypt_secrets()` quando existir, mesclando sobre os valores do `.env` (vault tem precedência)
    - Em caso de falha na decifragem, registrar `logging.warning(...)` e continuar com valores do `.env`
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

  - [x] 4.2 Escrever testes de propriedade para validação de `ksc_fqdn` e `db_sslmode` (Properties 8, 9)
    - Adicionar ao `tests/test_credentials_properties.py`
    - **Property 8: FQDN inválido é sempre rejeitado**
    - **Property 9: `db_sslmode` fora do conjunto válido é sempre rejeitado**
    - **Validates: Requirements 6.1, 6.2**

  - [x] 4.3 Escrever testes de exemplo para `load_config()` com vault
    - Atualizar `tests/test_config.py` para cobrir o caminho de merge vault → `.env`
    - Cobrir o caso em que `vault.decrypt_secrets()` lança exceção (deve logar WARNING e continuar)
    - _Requirements: 6.3, 6.4_

- [x] 5. Migrar os testes existentes para usar credenciais sintéticas
  - [x] 5.1 Migrar `tests/test_config.py`
    - Remover todas as strings com aparência de credencial e todos os comentários `# pragma: allowlist secret`
    - Substituir senhas hardcoded por `generate_password()` injetado via `monkeypatch.setenv` ou `patch.dict(os.environ, ...)`
    - Manter todos os nomes de função de teste existentes e a cobertura atual
    - _Requirements: 4.1, 4.2, 4.5, 4.6_

  - [x] 5.2 Migrar `tests/test_checks.py`
    - Substituir a fixture/variável `dummy_config` pela fixture `ksc_test_config` do conftest
    - Remover `db_password="123"`, `ksc_admin_password="123"` e equivalentes
    - Remover todos os comentários `# pragma: allowlist secret`
    - _Requirements: 4.1, 4.3, 4.5, 4.6_

  - [x] 5.3 Migrar `tests/test_ksc_audit.py` e `tests/test_secure_file.py`
    - Revisar `test_ksc_audit.py` para confirmar ausência de credenciais diretas (atualizar se necessário)
    - Em `test_secure_file.py`, substituir `"my secret content"`, `"temporary secret"` e equivalentes por strings neutras ou por valores de `generate_password()`
    - Remover todos os comentários `# pragma: allowlist secret`
    - _Requirements: 4.1, 4.4, 4.5, 4.6_

- [x] 6. Checkpoint — Verificar suíte de testes migrada
  - Executar `pytest` completo para garantir zero falhas e zero erros de importação. Executar `detect-secrets scan --no-baseline tests/` e confirmar zero achados. Perguntar ao usuário se houver dúvidas antes de prosseguir.

- [x] 7. Implementar `init_config.py`
  - [x] 7.1 Criar `automation/python/init_config.py` com fluxo interativo completo
    - Criar o arquivo `automation/python/init_config.py` com bloco `if __name__ == "__main__"` e suporte a `python3 -m automation.python.init_config`
    - Coletar campos não-sensíveis via `input()` com formato `"Nome do campo [valor_padrão]: "`
    - Coletar campos sensíveis (`KSC_DB_PASS`, `KSC_ADMIN_PASS`, `KSC_PASS`) via `getpass.getpass()`
    - Implementar loop de re-prompt quando validação do Config_Module falhar, exibindo `"Valor inválido: {msg}"`
    - Detectar existência de `configs/env/ksc_vars.env` e exibir diff de chaves (sem mostrar valores sensíveis) com confirmação `[s/N]`
    - Escrever o arquivo via `write_secure_file` com permissão `0o600` usando escrita atômica (temp + rename)
    - Implementar flag `--vault` que chama `vault.encrypt_secrets()` com os campos sensíveis e grava `configs/secrets.bin`
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9_

  - [x] 7.2 Escrever testes de exemplo para `init_config.py`
    - Criar `tests/test_init_config.py` com mock de `stdin`, `getpass` e `write_secure_file`
    - Cobrir: fluxo feliz, confirmação de sobrescrita, rejeição de confirmação, loop de re-prompt por validação inválida, erro de I/O ao escrever
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.9_

- [x] 8. Sanitizar arquivos `.example`
  - [x] 8.1 Atualizar `configs/examples/ksc.env.example` e criar `configs/env/ksc_vars.env.example`
    - Em `configs/examples/ksc.env.example`: substituir `KSC_HOSTNAME=kscserver.portosoft.local` e qualquer valor classificável pelo `detect-secrets` por `<PREENCHER: instrução específica>`; garantir que `KSC_DB_PASS=<PREENCHER: gerar com openssl rand -base64 24>` esteja presente
    - Criar `configs/env/ksc_vars.env.example` com todas as variáveis listadas no requisito 7.5, cada uma com marcador `<PREENCHER: ...>` adequado
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 9. Atualizar documentação operacional
  - [x] 9.1 Atualizar `docs/03-pre-requisitos.md`, `CHECKLIST.md` e `CHANGELOG.md`
    - Em `docs/03-pre-requisitos.md`: inserir passo numerado "2.5" imediatamente antes do passo do `ksc_audit.py --check`, com o comando `python3 -m automation.python.init_config`, a nota de não commitar e a descrição da flag `--vault`
    - Em `CHECKLIST.md`: adicionar `- [ ] \`init_config.py\` executado interativamente pelo operador (sem .env copiado de outro host)` como primeiro item da seção "📂 5. Execução do Runbook (Pre-check)"
    - Em `CHANGELOG.md`: adicionar bloco `[Unreleased]` (ou inserir no topo se não existir) com as três entradas de `Added`/`Changed` especificadas
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 10. Checkpoint final — Validação end-to-end
  - Executar `pytest` completo e garantir que todos os testes passam. Verificar zero achados em `detect-secrets scan --no-baseline tests/` e `detect-secrets scan --no-baseline configs/`. Perguntar ao usuário se houver dúvidas.

## Notes

- Tarefas marcadas com `*` são opcionais e podem ser omitidas para um MVP mais rápido
- Cada tarefa referencia os requisitos correspondentes para rastreabilidade
- Os testes de propriedade usam a biblioteca **Hypothesis** (`pip install hypothesis`), que deve ser adicionada ao `requirements.txt` na tarefa 1.2
- Os checkpoints garantem validação incremental a cada etapa crítica
- Nenhum diretório novo será criado — todos os arquivos vão em diretórios já existentes

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["1.2", "1.3", "1.4", "2.1"] },
    { "id": 2, "tasks": ["2.2", "2.3"] },
    { "id": 3, "tasks": ["4.1", "5.1", "5.2", "5.3"] },
    { "id": 4, "tasks": ["4.2", "4.3", "7.1"] },
    { "id": 5, "tasks": ["7.2", "8.1"] },
    { "id": 6, "tasks": ["9.1"] }
  ]
}
```
