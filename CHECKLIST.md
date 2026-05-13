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

## 📂 5. Governança e Evidências
- [ ] Log de instalação salvo em `evidence/install.log`.
- [ ] Output do `ksc_audit.py --check` sem erros críticos.
- [ ] Backup inicial realizado com sucesso.

---
**Assinatura do Operador:** ___________________________
**Data:** ____/____/_______
