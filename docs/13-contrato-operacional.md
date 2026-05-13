# 13 - Contrato Operacional

Este documento define a relação técnica entre os diferentes componentes do repositório, garantindo que a automação e a documentação falem a mesma língua.

## Fluxo de Configuração
1. O Operador preenche o `.env`.
2. O script Python lê o `.env`.
3. O script injeta os valores nos templates `.template`.
4. Os arquivos finais são gerados e aplicados no sistema.

## Tabela de Mapeamento

| Nome da Variável | Origem (.env) | Destino (Template) | Consumido por | Efeito | Validação |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DB_NAME` | `KSC_DB_NAME` | `ksc_response.txt` | `ksc_setup.py` | Define o nome da base no Postgres. | `psql -l` |
| `DB_USER` | `KSC_DB_USER` | `ksc_response.txt` | `ksc_setup.py` | Usuário de conexão do KSC. | `psql -U` |
| `DB_PASS` | `KSC_DB_PASS` | `ksc_response.txt` | `ksc_setup.py` | Senha de conexão. | Tentativa de login. |
| `WEB_PORT` | `KSC_WEB_PORT` | `setup.json` | `ksc_setup.py` | Porta HTTPS do Console. | `netstat -tulpn` |

## Convenções de Saída
- **Logs**: Todos os scripts devem escrever em `/var/log/kaspersky/automation/`.
- **Relatórios**: Gerados em `./evidence/`.
- **Exit Codes**:
  - `0`: Sucesso total.
  - `1`: Erro genérico/pré-requisito falhou.
  - `2`: Erro de configuração (variável ausente).
  - `3`: Erro de execução (comando falhou).

## Padrão de Argumentos CLI
Todos os scripts em `automation/python/` devem seguir este padrão:
- `--config <path>`: Caminho para o arquivo `.env`.
- `--check`: Valida o estado atual sem alterar nada.
- `--apply`: Executa as alterações.
- `--dry-run`: Mostra o que seria feito.
- `--verbose`: Ativa logs de debug.

---
[Voltar ao Índice](00-index.md)
