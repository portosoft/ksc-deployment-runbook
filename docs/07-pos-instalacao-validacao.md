# 07 - Pós-instalação e Validação

## Objetivo
Confirmar se o sistema está operacional e acessível para o administrador.

## Testes de Serviço
Execute o script de auditoria para validar o estado final:
```bash
python3 automation/python/ksc_audit.py --check
```

## Verificação de Porta Web
Acesse no seu navegador: `https://<ip-ou-fqdn-do-servidor>/`.

## Coleta de Evidências
Salve o output do comando abaixo na pasta `evidence/`:
```bash
sudo klsummary > evidence/deployment_summary.txt
```

---
[Próximo Passo: Hardening >>](08-hardening.md)
