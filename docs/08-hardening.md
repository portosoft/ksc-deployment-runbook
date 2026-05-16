# 08 - Hardening

## Objetivo
Elevar o nível de segurança da implantação pós-setup inicial.

## Ações Recomendadas
1. **Certificados**: Substituir os certificados auto-assinados por certificados da PKI interna.
2. **Acesso ao Banco**: Restringir o PostgreSQL apenas para o IP do KSC Server no `pg_hba.conf`.
3. **SSH**: Desativar login de root se possível e utilizar chaves.
4. **Firewall**: Fechar portas não utilizadas (`22` deve ser restrita).

## Script de Hardening Final
O script `ksc_harden_db.py` deve ser executado novamente com a flag `--apply` para garantir que as permissões de arquivo do Kaspersky estão corretas.

---
[Próximo Passo: Operação >>](09-operacao.md)
