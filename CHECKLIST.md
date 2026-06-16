# Checklist de Aceite Operacional (DoD)

Este checklist deve ser preenchido ao final de cada implantação e arquivado na pasta `evidence/`.

## 🖥️ 1. Validação do Host
- [ ] Hostname configurado como FQDN.
- [ ] `/etc/hosts` contém a entrada do próprio IP.
- [ ] SELinux em modo `permissive` (verificado via `getenforce`).
- [ ] Repositórios EPEL e PostgreSQL 16 ativos.

## 🗄️ 2. Banco de Dados
- [ ] PostgreSQL 16 `active (running)`.
- [ ] Usuário do KSC criado com permissões adequadas.
- [ ] `max_connections` ajustado para pelo menos 1000.
- [ ] Conectividade local testada via `psql`.

## 🛡️ 3. Kaspersky Security Center
- [ ] `klserver` ativo e rodando como usuário `ksc`.
- [ ] `klnagent` ativo.
- [ ] Web Console acessível via `https://<FQDN>`.
- [ ] Login efetuado com sucesso no Web Console.

## 🔗 4. Rede e Conectividade
- [ ] Porta 13000 (Agent SSL) aberta no firewall.
- [ ] Porta 14000 (Agent Non-SSL) aberta no firewall.
- [ ] Porta 443 (Web) aberta e acessível externamente.

## 📂 5. Execução do Runbook (Pre-check)
- [ ] `init_config.py` executado interativamente pelo operador (sem .env copiado de outro host)
- [ ] Arquivo de variáveis `.env` populado sem segredos pendentes.
- [ ] Executou `python3 automation/python/ksc_audit.py --check`
- [ ] O output validou o SELinux, Memória e Discos sem falhas críticas.

## 📂 6. Execução do Deploy e Post-check
- [ ] Executou `python3 automation/python/ksc_setup.py --apply` com sucesso.
- [ ] Executou `python3 automation/python/ksc_audit.py --postcheck` com sucesso.
- [ ] O Relatório de Auditoria foi gerado (em `evidence/reports/`).
- [ ] Backup inicial realizado com sucesso.

---
**Assinatura do Operador:** ___________________________
**Data:** ____/____/_______
