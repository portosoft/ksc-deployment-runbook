# Security Policy

## Supported Versions

Atualmente, apenas a versão estável mais recente do runbook é suportada.

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | ✅ Yes              |
| < 1.0   | ❌ No               |

## Reporting a Vulnerability

Se você encontrar uma vulnerabilidade de segurança, por favor não abra uma Issue pública. Envie um e-mail para `seguranca@portosoft.com.br`.

Nós responderemos em até 48 horas com um plano de mitigação.

## Boas Práticas (Principle of Least Privilege)
- **Zero Segredos no Código**: Nunca comite senhas, dumps de DB ou chaves no repositório. Use o `.secrets.baseline` se necessitar suprimir um falso positivo do `detect-secrets`.
- **Validação Automática**: Ao criar um PR, seu código deverá passar por nossas verificações automatizadas de segredos. PRs bloqueados não serão fundidos (merged).
- **Sem Exceções Permanentes**: Caso alguma configuração temporária seja feita durante o debug (ex. desabilitar o firewall, chmod 777, ou SELinux disabled), ela deve ser reportada e desfeita.
