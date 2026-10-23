# ADR-0001: Unificação da Automação no Núcleo Python (kscctl) e Descontinuação da Pilha Ansible

- **Status**: Aceito
- **Data**: 2026-10-23
- **Decisores**: Equipe DevSecOps (`@mendsec`)
- **Contexto Técnico**: Issue [#226](https://github.com/portosoft/ksc-deployment-runbook/issues/226), EPIC [#203](https://github.com/portosoft/ksc-deployment-runbook/issues/203), Limitação **L-12**

---

## 1. Contexto

Historicamente, o projeto mantinha duas pilhas de automação em paralelo:
1. O núcleo nativo em Python (`automation/python/`), centrado na CLI `kscctl`;
2. Playbooks preliminares em Ansible (`automation/ansible/`).

Essa duplicidade foi registrada em `project-review/02-architecture.md` (AD-1) e catalogada em `project-review/06-known-limitations.md` como a limitação **L-12**:

> *"Duas pilhas de automação em paralelo (Python e Ansible) geram divergência de comportamento entre caminhos e constituem dívida técnica."*

A conclusão do deploy E2E real em laboratório (Issue [#209](https://github.com/portosoft/ksc-deployment-runbook/issues/209)) e as recentes evoluções de arquitetura e segurança (Issues [#205](https://github.com/portosoft/ksc-deployment-runbook/issues/205), [#206](https://github.com/portosoft/ksc-deployment-runbook/issues/206), [#207](https://github.com/portosoft/ksc-deployment-runbook/issues/207) e [#237](https://github.com/portosoft/ksc-deployment-runbook/issues/237)) demonstraram que:

- O **núcleo Python** provê uma solução completa, robusta e auditável para o ciclo de vida da aplicação:
  - Validação criptográfica de pacotes via SHA-256 (`packages.py`);
  - Pré-verificação de requisitos de sistema, DNS e SELinux (`checks.py`);
  - Conexão SSH segura com política estrita `RejectPolicy` contra MitM (`remote.py`);
  - Armazenamento cifrado de segredos em cofre local (`vault.py`);
  - Sanitização ativa em memória e em logs para prevenir vazamento de senhas (`logging_utils.py`);
  - Reconfiguração e hardening do PostgreSQL com comandos nativos `ALTER SYSTEM` e parsing JSON estruturado do Web Console;
  - Mecanismo granular de rollback e contingência operacional (`rollback.py`);
  - Cobertura por 180+ testes automatizados (unitários, propriedades e contratos) executados em CI.

- Em contraste, a **pilha Ansible** consistia em apenas um playbook embrionário (`site.yml`, 43 linhas) que se limitava a configurar hostname, pacotes genéricos e acionar `firewalld`. Ela:
  - Não executava o instalador do KSC (`postinstall.pl`);
  - Não manipulava os arquivos de respostas de instalação de maneira segura;
  - Não possuía integração com o cofre de credenciais nem com o sanitizador de evidências;
  - Não possuía suíte de testes de integração ou execução contínua no CI;
  - Introduzia divergências de configuração arquitetural (ex.: manipulava `firewalld` enquanto a arquitetura oficial padronizou tabelas e regras atômicas no `nftables` na Issue #205).

---

## 2. Decisão

Decidiu-se pela **descontinuação formal da pilha Ansible** (`automation/ansible/`) e pela **unificação definitiva de todos os fluxos de automação na CLI nativa Python (`kscctl`)**.

### Diretrizes da Decisão:

1. **Caminho Único de Execução**:
   - A CLI `kscctl` (`python3 -m automation.python.kscctl`) passa a ser o único orquestrador e ponto de entrada oficial para todas as fases operacionais: `precheck`, `packages`, `setup`, `report`, `rollback` e `harden`.
2. **Sinalização de Depreciação da Pilha Ansible**:
   - O diretório `automation/ansible/` recebe aviso explícito de descontinuação (`DEPRECATED.md`).
   - O script `automation/ops/env_to_ansible.py` emite aviso de depreciação (`DeprecationWarning`) para informar eventuais chamadas legadas antes de sua futura remoção.
3. **Não Encapsulamento (Sem Wrapper Artificial)**:
   - Rejeitou-se a alternativa de criar um playbook Ansible como interface fina sobre a CLI Python. Adicionar o ecossistema Ansible apenas para invocar comandos do `kscctl` acarretaria overhead desnecessário de dependências e aumentaria a superfície de falha e incompatibilidade de pacotes.

---

## 3. Consequências

### Positivas:
- **Resolução da Limitação L-12**: Eliminação de duplicação de esforço e garantia de consistência comportamental absoluta.
- **Redução da Complexidade de Dependências**: Elimina a necessidade de empacotamento ou dependência do ecossistema Ansible no ambiente de controle.
- **Segurança Reforçada**: Todas as operações passam obrigatoriamente pelos controles de segurança estabelecidos no núcleo Python (cofre padrão, sanitização de logs, SSH com `RejectPolicy` e sudo restritivo).
- **Manutenibilidade e Testabilidade**: Centralização de 100% dos testes contínuos no pytest e no CI do repositório.

### Considerações Operacionais:
- Procedimentos que eventualmente fizessem menção ao uso de playbooks Ansible devem ser redirecionados para os comandos equivalentes do `kscctl`. Como a pilha Ansible nunca completou um deploy funcional do KSC, não há descontinuação de funcionalidade operacional real.
