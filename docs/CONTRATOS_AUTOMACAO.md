# Contratos de Automação (CLI)

Os scripts na pasta `automation/python/` são a interface de linha de comando oficial para operar o ambiente KSC. Eles são desenhados para serem idempotentes, seguros e fornecerem saídas consistentes.

## ksc_audit.py

Script para verificar a integridade e os pré/pós-requisitos do ambiente KSC.

### Argumentos

- `--check`: Verifica pré-requisitos antes da instalação (RAM, disco, OS suportado, SELinux, portas disponíveis).
- `--postcheck`: Verifica o estado do sistema após a instalação (PostgreSQL ativo, klnagent ativo, klserver ativo, e Web Console respondendo).
- `--report`: Gera relatórios Markdown e PDF na pasta de evidências baseando-se nos testes de auditoria.

### Códigos de Saída

- `0`: Sucesso total. Nenhuma falha crítica detectada.
- `1`: Falhas críticas detectadas. Operações que dependem do sucesso deste script devem ser bloqueadas.
- `2`: Erro de uso ou de configuração (ex: falta de arquivo de variáveis de ambiente, dependências faltando).

## ksc_setup.py

Script para efetuar a instalação e provisionamento do Kaspersky Security Center.

### Argumentos

- `--check`: Realiza um `precheck` do ambiente para garantir que a instalação não falhará no meio do processo.
- `--apply`: Executa as etapas de deploy completo: SO, PostgreSQL, KSC Server e Web Console, aplicando os hardenings necessários (ex: SELinux provisório).

### Códigos de Saída

- `0`: Sucesso total. Deploy efetuado.
- `1`: Falhas críticas detectadas durante o `--check`.
- `2`: Erro durante a instalação ou erro de uso/configuração.

## Idempotência

Nossos scripts são planejados para serem idempotentes. Rodar `--apply` em um ambiente que já possui o KSC não deve quebrar a instalação, mas sim validar ou pular etapas já concluídas de forma segura.
