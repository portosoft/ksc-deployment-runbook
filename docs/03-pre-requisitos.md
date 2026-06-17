# 03 - Pré-requisitos

## Objetivo
Preparar o terreno antes de iniciar qualquer script de instalação.

## Checklist de Infraestrutura
- [ ] **Hostname**: Deve ser um FQDN válido (ex: `ksc01.empresa.local`).
- [ ] **DNS**: Resolução direta e reversa configurada.
- [ ] **Internet**: Acesso aos repositórios Rocky/Oracle e Kaspersky.
- [ ] **Repositórios**: `epel-release` instalado.

> [!IMPORTANT]
> A resolução DNS é o ponto onde 80% das falhas de instalação ocorrem. Certifique-se de que o comando `hostname -f` retorna o FQDN correto.

## Liberação de Portas (Firewall Interno)
| Porta | Protocolo | Origem | Destino | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| 443 | TCP | Admin | KSC Server | Console Web |
| 13000 | TCP | Endpoints | KSC Server | SSL Agent Comm |
| 14000 | TCP | Endpoints | KSC Server | Non-SSL Agent Comm |
| 13291 | TCP | Localhost | KSC Server | API Administrativa |

> [!WARNING]
> Se o PostgreSQL for instalado em um servidor remoto, a porta **5432/TCP** deve estar liberada entre o KSC Server e o DB Server.

## Usuário
- O operador deve ter privilégios de `sudo` total.

---

## Passo 2.5 — Geração Interativa do Arquivo de Variáveis de Ambiente

Antes de executar o `ksc_audit.py --check`, preencha as variáveis de ambiente de produção com o script interativo:

```bash
python3 -m automation.python.init_config
```

> [!IMPORTANT]
> O arquivo gerado (`configs/env/ksc_vars.env`) **não deve ser commitado** no repositório.
> Para cifrar os campos sensíveis, use a flag `--vault`:
> ```bash
> python3 -m automation.python.init_config --vault
> ```
> Isso grava as credenciais cifradas em `configs/secrets.bin`, mas o arquivo `.env` com as credenciais em texto puro **também é gravado** no mesmo passo (o `.env` é necessário para carregamento pelo `load_config()`).

As variáveis solicitadas interativamente são:
`KSC_DB_HOST`, `KSC_DB_PORT`, `KSC_DB_USER`, `KSC_FQDN`, `KSC_HOST`, `KSC_USER`, `KSC_WEB_PORT`, `KSC_SELINUX_MODE`, `KSC_DB_PASS`, `KSC_ADMIN_PASS`, `KSC_PASS`.

---
[Próximo Passo: Precheck >>](04-precheck.md)
