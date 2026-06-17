# 08 - Hardening

## Objetivo
Elevar o nível de segurança da implantação pós-setup inicial.

## Ações Recomendadas
1. **Certificados**: Substituir os certificados auto-assinados por certificados da PKI interna.
2. **Acesso ao Banco**: Restringir o PostgreSQL apenas para o IP do KSC Server no `pg_hba.conf`.
3. **SSH**: Desativar login de root se possível e utilizar chaves.
4. **Firewall**: Fechar portas não utilizadas (`22` deve ser restrita).

## Script de Hardening Final
O comando de hardening do banco de dados deve ser executado através da CLI unificada:
```bash
python3 -m automation.python.kscctl db harden --apply
```

---

## 🛡️ Modelo de Ameaças (Threat Model)

Para garantir a integridade de um deploy de segurança do KSC 16.x, mapeamos a superfície de ataque e as respectivas mitigações:

| Vetor de Ameaça | Impacto | Mitigação Aplicada |
| :--- | :--- | :--- |
| **Vazamento de credenciais via Git** | Vazamento de credenciais de produção. | Limpeza do histórico de commits, uso obrigatório de `.gitignore` e verificação ativa do `detect-secrets` via pre-commit. |
| **Escuta e Man-in-the-Middle (MitM) no SSH** | Roubo de credenciais ou injeção de comandos durante a orquestração remota. | Conexão estrita usando `RejectPolicy` para chaves de host desconhecidas. |
| **Exposição de senhas no Process List (`ps aux`)** | Senhas expostas em texto claro nos servidores. | Passagem de senhas remota usando exclusivamente fluxos de entrada segura no canal stdin do SSH (no-args injection). |
| **Vazamento de credenciais em arquivos temporários** | Outros processos locais leem segredos no `/tmp`. | Escrita segura via SFTP de arquivos temporários com permissões restritas `0o600` antes de preencher o conteúdo. |
| **Desativação permanente do SELinux** | Redução do isolamento e segurança geral do sistema operacional. | O SELinux é alterado para `permissive` estritamente durante a execução da instalação e restaurado para `enforcing` no bloco `finally`. |

---

## 🤝 Matriz de Responsabilidade Compartilhada

A segurança geral da implantação é dividida entre os seguintes atores:

1. **Kaspersky (Provedor do Produto)**:
   - Garantir a segurança interna, correções de vulnerabilidades e integridade dos pacotes do KSC Server, Web Console e agentes.
2. **Mantenedores do Runbook (Projeto Open-Source)**:
   - Fornecer scripts de implantação seguros (sem vazamentos, sem passagem de parâmetros inseguros).
   - Manter as ferramentas operacionais de auditoria e hardening atualizadas e
     livres de vulnerabilidades conhecidas.
   - Aceitar contribuições da comunidade via pull requests revisados.
3. **Cliente / Operador (Provedor da Infraestrutura e Governança)**:
   - Rotacionar e gerenciar credenciais de produção (`KSC_PASS`, `KSC_DB_PASS`, `KSC_ADMIN_PASS`) de forma segura.
   - Manter o repositório privado caso contenha configurações ou variáveis locais.
   - Habilitar e gerenciar controles de segurança de rede (Firewalls, VPN/Tailscale) e review humano obrigatório no pipeline de CI/CD.

---

## 6. CIS Benchmarks para Rocky Linux 9

### 6.1. Serviços Desnecessários
Desativar e remover serviços não utilizados:
```bash
systemctl disable --now avahi-daemon
systemctl disable --now cups
systemctl disable --now postfix
systemctl disable --now rpcbind
systemctl disable --now snmpd

# Verificar status:
systemctl list-units --type=service --state=running
```

### 6.2. Configuração de nftables (recomendado) ou iptables
```bash
# Instalar nftables
dnf install nftables -y

# Criar ruleset mínimo
cat > /etc/nftables/rules.nft << 'NW'
#!/usr/sbin/nft -f

flush ruleset

table inet filter {
    chain input {
        type filter hook input priority 0;
        policy drop;

        # Accept loopback
        iif "lo" accept

        # Accept established connections
        ct state established,related accept

        # Accept ICMP
        ip protocol icmp accept
        ip6 protocol icmpv6 accept

        # Accept SSH (limit 10/min)
        tcp dport 22 ct state new limit 10/min accept

        # Accept KSC ports (apenas da VLAN de gestão)
        tcp dport 1329 ct state new from 10.0.0.0/16 accept
        tcp dport 3000 ct state new from 10.0.0.0/16 accept

        # Drop tudo mais
        drop
    }

    chain forward {
        type filter hook forward priority 0;
        policy drop;
    }

    chain output {
        type filter hook output priority 0;
        policy accept;
    }
}
NW

# Aplicar ruleset
nft -f /etc/nftables/rules.nft

# Verificar
nft list ruleset
```

### 6.3. Configuração de auditd
```bash
# Instalar audit
dnf install audit -y

# Configurar regras mínimas
cat > /etc/audit/audit.rules << 'AUD'
# Desativar regras existentes
-r

# Monitorar alterações em sistemas críticos
-w /etc/passwd -p wa -k identity
-w /etc/group -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/sudoers -p wa -k sudo

# Monitorar execução de comandos privilegiados
-w /usr/sbin/useradd -p wa -k usermod
-w /usr/sbin/userdel -p wa -k usermod
-w /usr/sbin/usermod -p wa -k usermod

# Monitorar mudanças de permissão
-w /etc -p wa -k config_change

# Logar tentativas de acesso inválido
-a always,exit -F path=/bin/chmod -p ax -k chmod
-a always,exit -F path=/bin/chown -p ax -k chown
-a always,exit -F path=/bin/setfacl -p ax -k acl
AUD

# Reiniciar auditd
systemctl restart auditd
systemctl enable auditd

# Verificar
auditctl -l
```

### 6.4. Fail2Ban para SSH
```bash
# Instalar fail2ban
dnf install fail2ban -y

# Configurar jail para SSH
cat > /etc/fail2ban/jail.local << 'FB'
[ssh]
enabled = true
port = 22
filter = sshd
logpath = /var/log/secure
maxretry = 3
findtime = 600
bantime = 3600
FB

# Reiniciar fail2ban
systemctl restart fail2ban
systemctl enable fail2ban

# Verificar
fail2ban-client status ssh
```

### 6.5. Política de Senhas (complexidade e rotação)
```bash
# Instalar pam_pwquality
dnf install pam_pwquality -y

# Configurar complexidade mínima
cat > /etc/security/pwquality.conf << 'PW'
minlen = 14
minclass = 3
maxrepeat = 3
maxdeltaif = 3
retry = 3
PW

# Configurar rotação de 90 dias
cat > /etc/login.defs << 'LD'
PASS_MAX_DAYS   90
PASS_MIN_DAYS   7
PASS_WARN_AGE   14
LD

# Aplicar para usuários existentes
chage --maxdays 90 --mindays 7 --warnage 14 admin
```

### 6.6. Verificação Final
```bash
# Executar script de validação
automation/bash/validate-harden.sh

# Relatório esperado: todos os vetores pass
```

---
[Próximo Passo: Operação >>](09-operacao.md)
