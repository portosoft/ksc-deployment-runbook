# Pilha Ansible Descontinuada (ADR-0001)

> [!WARNING]
> **Aviso de Descontinuação**:
> A pilha de automação baseada em Ansible (`automation/ansible/`) foi formalmente descontinuada em favor do núcleo nativo de orquestração Python (`kscctl`).
>
> Para detalhes completos sobre a fundamentação técnica e arquitetural desta decisão, consulte:
> 👉 [`docs/adr/0001-unificacao-nucleo-python-descontinuacao-ansible.md`](../../docs/adr/0001-unificacao-nucleo-python-descontinuacao-ansible.md)

---

## Motivo da Unificação

1. **Cobertura Operacional Fim-a-Fim**: O núcleo Python (`kscctl`) provê o ciclo de vida completo do deployment (verificação SHA-256 de pacotes oficiais, pré-requisitos, execução remota SSH segura com `RejectPolicy`, cofre cifrado de segredos, reconfiguração do Web Console e rollback granular).
2. **Eliminação de Divergência**: A manutenção em paralelo de playbooks Ansible e scripts Python constituía dívida técnica reconhecida (Limitação **L-12**), gerando retrabalho e risco de configurações divergentes (ex.: firewalld vs. nftables).
3. **Caminho Único de Execução**: Todos os procedimentos operacionais e de homologação utilizam exclusivamente a CLI `kscctl`.
