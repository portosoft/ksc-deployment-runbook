# Contribuindo para o KSC Deployment Runbook

Obrigado por seu interesse em contribuir com este projeto open-source!

## Como contribuir

### Abrindo Issues
- Utilize as Issues para reportar bugs, sugerir melhorias ou documentar novos casos de troubleshooting.
- Seja descritivo e inclua detalhes do ambiente (versão do OS, versão do KSC, etc.).

### Propondo Pull Requests
1. Faça um fork do repositório (ou crie uma branch se tiver permissão).
2. **Branch de Origem e Destino**: Todas as branches de trabalho DEVEM ser criadas a partir da branch **`develop`** (branch padrão do repositório).
   - **NUNCA direcione Pull Requests diretamente para a branch `main`**. A branch `main` é estritamente restrita a releases e promoções automatizadas vindas de `develop`.
   - Todo PR de desenvolvimento ou documentação deve ter como base (`base ref`) a branch **`develop`**.
3. **Padrão de Nomenclatura de Branches**:
   - `feat/<nome>` ou `feature/<nome>`: Novas funcionalidades ou automações.
   - `fix/<nome>` ou `bugfix/<nome>`: Correção de bugs.
   - `docs/<nome>`: Manuais, runbooks ou atualizações de documentação.
   - `ci/<nome>` ou `chore/<nome>`: Ajustes de CI/CD, linters ou tarefas operacionais.
   - `security/<nome>`: Correções e remediações de segurança.
4. Implemente suas alterações seguindo o padrão de diretórios e boas práticas de código seguro.
5. Garanta que scripts Bash e Python tenham comentários claros, tratamento de erros e idempotência.
6. Envie o PR direcionado para `develop` com o checklist DevSecOps preenchido no template.

## Padrões de Commit e Assinatura Criptográfica
- **Conventional Commits**: Utilize a convenção de commits (`<tipo>(<escopo>): <descrição>`).
  - Tipos permitidos: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `security`, `perf`, `ci`.
  - Exemplos: `feat(infra): add proxmox local test environment (#204)`, `fix(ops): harden psql connection string`.
- **Commits obrigatoriamente assinados (GPG ou SSH)**:
  - 100% dos commits enviados ao repositório devem ser assinados criptograficamente.
  - Commits não assinados são rejeitados pelo check `Enforce Main Branch Rules` e pelas proteções de branch.
  - Configure sua chave SSH ou GPG no GitHub e habilite o signing local:
    ```bash
    git config --global gpg.format ssh
    git config --global user.signingkey ~/.ssh/id_ed25519.pub
    git config --global commit.gpgsign true
    ```

## Estratégia de Merge
- **NUNCA use `Squash and merge`** entre branches de integração (`develop`) e produção (`main`). O squash quebra a linearidade de auditoria e a rastreabilidade das assinaturas criptográficas individuais.
- Utilize **Merge Commit padrão** (`--no-ff` / `--merge`) ou **Rebase** para preservar o grafo de histórico do Git.

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

## Governança e Automação de PR via Agentes de IA
Este repositório utiliza agentes de IA (Jules, Antigravity, Claude Code) como executores de prompts de implementação com escopo restrito (arquivos e critérios de aceite definidos previamente). PRs abertos por esses agentes passam pelo pipeline de CI completo (lint, testes, SAST, secret scanning) e exigem aprovação humana obrigatória antes do merge na branch `main`.

Os workflows automatizados operam sob regras rígidas:
- O workflow `recreate-prs.yml` permite recriar PRs sob a identidade `github-actions[bot]` para fins de revisão.
- O workflow `trigger-bot-pr.yml` automatiza a abertura de PRs a partir da branch `trigger-bot-pr`, que é protegida e restrita a mantenedores autorizados.
- Todos os segredos e chamadas de API de automação nos fluxos utilizam o escopo de token efêmero padrão `GITHUB_TOKEN`, eliminando o uso de PATs pessoais.

## Estilo de Documentação
- Documentação técnica deve ser direta ao ponto (estilo runbook).
- Utilize Markdown para formatação.
