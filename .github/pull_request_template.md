## 📋 Descrição da Mudança

<!-- Descreva de forma clara o que foi implementado, corrigido ou refatorado. -->
<!-- Se este PR resolve ou está vinculado a uma issue, indique: Ex: Resolve #204 -->

---

## 🔒 Checklist de DevSecOps & Governança (Obrigatório)

Todo Pull Request deve satisfazer as seguintes verificações de segurança antes da aprovação do merge:

- [ ] **Branch Target Correta**: Este PR tem como base a branch **`develop`** (PRs para `main` são exclusivos para releases automatizadas).
- [ ] **Assinatura Criptográfica**: Todos os commits deste PR estão assinados digitalmente (SSH ou GPG).
- [ ] **Varredura de Segredos**: Nenhum segredo, senha de banco de dados, certificado ou credencial foi inserido em plain-text no código ou diff (`detect-secrets`).
- [ ] **Boas Práticas e Qualidade**:
  - [ ] Nenhuma injeção de comando ou concatenação insegura em comandos `psql` ou Bash.
  - [ ] Permissões de arquivos sensíveis respeitam o princípio de menor privilégio (`0600`/`0700`).
  - [ ] Testes automatizados executados e passando (`pytest tests/`).
- [ ] **Documentação & Rastreabilidade**:
  - [ ] Documentação correspondente atualizada em `docs/`.
  - [ ] `CHANGELOG.md` atualizado com o resumo da alteração.

---

## 👤 Aprovação Obrigatória do Code Owner

Conforme política de controle de mudanças e `.github/CODEOWNERS`:
- **Aprovador obrigatório**: `@mendsec`
