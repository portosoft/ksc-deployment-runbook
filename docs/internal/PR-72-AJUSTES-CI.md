# PR 72 - Ajustes Minimos para CI

## Objetivo
Registrar os ajustes aplicados na PR `Merge develop into main` para fazer os checks de CI voltarem a passar, com foco principal no job `CI Pipeline / Lint and Test`.

## Escopo executado
- Ajuste de tratador de excecao muito amplo em `automation/python/init_config.py`, restringindo o fallback para `FileNotFoundError` e preservando o primeiro uso quando o arquivo `.env` ainda nao existe.
- Remocao de imports nao utilizados em testes e no modulo ajustado para eliminar falhas de lint.
- Conversao de variavel local nao utilizada em `tests/test_init_config.py` para uma assercao util sobre o caminho gravado.
- Remocao de f-strings constantes em `tests/conftest.py` para atender verificacoes de estilo.
- Restricao dos mocks de `os.path.exists` em `tests/test_config.py` para evitar que testes sem foco em vault habilitem o fluxo de segredos por acidente.
- Alinhamento dos arquivos de exemplo `.env` com as chaves realmente lidas por `load_config()` e `init_config`.
- Normalizacao dos caminhos em `.secrets.baseline` para formato com `/`, compativel com runners Unix e com o hook de `detect-secrets`.

## Arquivos alterados
- `automation/python/init_config.py`
- `tests/test_init_config.py`
- `tests/conftest.py`
- `tests/test_config.py`
- `configs/env/ksc_vars.env.example`
- `configs/examples/ksc.env.example`
- `.secrets.baseline`

## Validacao executada
- `python -m pytest tests/`
- `python -m json.tool .secrets.baseline > $null`
- Diagnosticos do editor sem erros apos as alteracoes

## Resultado
- Suite de testes local: `61 passed, 4 skipped`
- Ajustes limitados ao necessario para restaurar conformidade de lint, testes e baseline de segredos, sem alterar a interface publica nem a logica de negocio.
