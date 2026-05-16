# Contribuindo para o KSC Deployment Runbook

Obrigado por seu interesse em contribuir para a documentação e automação da Portosoft!

## Como contribuir

### Abrindo Issues
- Utilize as Issues para reportar bugs, sugerir melhorias ou documentar novos casos de troubleshooting.
- Seja descritivo e inclua detalhes do ambiente (versão do OS, versão do KSC, etc.).

### Propondo Pull Requests
1. Faça um fork do repositório (ou crie uma branch se tiver acesso).
2. Implemente suas alterações seguindo o padrão de diretórios.
3. Garanta que scripts Bash e Python tenham comentários claros.
4. Envie o PR com uma descrição clara do que foi alterado.

## Padrões de Commit
- Utilize mensagens curtas e descritivas (ex.: `docs: adiciona caso de erro no postgres`, `feat: novo script de validação`).
- Prefira o uso de Conventional Commits.

## Segurança e Privacidade
- **MUITO IMPORTANTE**: Nunca inclua segredos nos seus commits. Isso inclui:
    - Senhas de banco de dados.
    - Arquivos de licença `.key`.
    - Certificados e chaves privadas.
    - Dumps de banco de dados contendo dados sensíveis.
- Verifique sempre o `.gitignore` antes de commitar.

### Uso do pre-commit e detect-secrets
Este repositório utiliza o `pre-commit` para garantir a qualidade do código e evitar o vazamento de credenciais via `detect-secrets`.
Antes de realizar qualquer commit, certifique-se de que instalou os hooks:
```bash
pip install pre-commit
pre-commit install
```
Antes de enviar suas mudanças, rode:
```bash
pre-commit run --all-files
```
O `detect-secrets` baseia-se no arquivo `.secrets.baseline`. Se você adicionou um "falso positivo", precisará atualizar a baseline localmente.
## Estilo de Documentação
- Documentação técnica deve ser direta ao ponto (estilo runbook).
- Utilize Markdown para formatação.

---
Portosoft - DevOps Team
