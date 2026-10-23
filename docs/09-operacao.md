# 09 - Operação

## Objetivo
Manter a saúde do KSC após o deploy.

## Backup
O backup do KSC deve ser feito via utilitário `klbackup`.
```bash
/opt/kaspersky/ksc64/sbin/klbackup -path /backup/ksc -password <senha>
```
**Nota**: Configure um cronjob para realizar este backup diariamente.

## Atualização de Patches
1. Pare os serviços: `systemctl stop klserver klwebsrv`.
2. Instale o novo RPM.
3. Inicie os serviços.

## Validação Pós-Deploy (Smoke Tests)

Após a conclusão da implantação ou restauração, valide o funcionamento dos serviços essenciais com a suíte de *smoke tests*.

Os smoke tests verificam a conectividade real contra o Web Console e a autenticação na OpenAPI do KSC. Por dependerem de serviços ativos e credenciais válidas, **não são executados no fluxo padrão de CI** (possuem o marker `smoke` e são desabilitados por padrão no `pytest`).

### Execução via Pytest
Para executar a validação completa contra a instância alvo definida no arquivo de ambiente:

```bash
# Executa todos os smoke tests marcados
python3 -m pytest -m smoke automation/smoke-tests/
```

### Execução Direta via CLI
Os testes também podem ser disparados individualmente como scripts de linha de comando:

1. **Acessibilidade do Web Console**:
```bash
python3 automation/smoke-tests/verify_web_console.py --config configs/env/ksc_vars.env --insecure
```

2. **Autenticação OpenAPI do KSC**:
```bash
python3 automation/smoke-tests/test_api_login.py --config configs/env/ksc_vars.env --insecure
```

---
[Próximo Passo: Troubleshooting >>](10-troubleshooting.md)
