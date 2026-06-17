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
[Próximo Passo: Operação >>](09-operacao.md)
