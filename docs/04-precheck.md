# 04 - Precheck

## Objetivo
Validar automaticamente se os pré-requisitos foram atendidos antes de iniciar a instalação.

## Quando Usar
Sempre, antes de iniciar o PostgreSQL ou o KSC.

## Comandos
Navegue até a pasta de automação e execute o script de auditoria no modo check:

```bash
python3 automation/python/ksc_audit.py --check
```

## Saída Esperada
O script deve retornar `OK` para os seguintes itens:
- [x] RAM >= 8GB.
- [x] Conectividade com porta 5432 (se o banco for remoto).
- [x] SELinux em modo Permissive.
- [x] Resolv.conf com DNS válido.

## O que fazer em caso de erro?
Não prossiga para a etapa 05 até que todos os itens Críticos do `ksc_audit.py` estejam verdes. Use as recomendações exibidas no log do script para corrigir.

---
[Próximo Passo: Instalação PostgreSQL >>](05-instalacao-postgresql.md)
