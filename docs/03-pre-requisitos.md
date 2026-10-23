# 03 - Pré-requisitos

## Objetivo
Preparar o terreno antes de iniciar qualquer script de instalação.

## Checklist de Infraestrutura
- [ ] **Hostname**: Deve ser um FQDN válido (ex: `ksc01.empresa.local`).
- [ ] **DNS**: Resolução direta e reversa configurada.
- [ ] **Internet**: Acesso aos repositórios Rocky/Oracle e Kaspersky.
- [ ] **Repositórios**: `epel-release` instalado.
- [ ] **Python 3.11+ (AppStream)**: Interpretador moderno instalado via `dnf install -y python3.11 python3.11-pip`.
- [ ] **Pacotes Oficiais e Checksums**: Pacotes RPM oficiais obtidos e validados via `sha256sum -c configs/ksc/checksums.sha256` ou `kscctl packages --verify-dir`.

> [!IMPORTANT]
> A resolução DNS é o ponto onde 80% das falhas de instalação ocorrem. Certifique-se de que o comando `hostname -f` retorna o FQDN correto.
> Binários não homologados ou com divergência de checksum SHA-256 serão rejeitados pela automação de deploy.

## Ambiente de Execução Python (Rocky Linux 9 / Enterprise Linux 9)

O Rocky Linux 9 entrega o Python 3.9 como o `python3` nativo da distribuição. No entanto, as ferramentas e bibliotecas do KSC Runbook (`requirements.txt`, incluindo `md2pdf`) exigem formalmente **Python >= 3.10**.

A tentativa de executar `pip3 install -r requirements.txt` sob o Python 3.9 resultará em falha de resolução de distribuição.

### Preparação do Ambiente com Python 3.11

1. Instale o módulo Python 3.11 oficial do repositório AppStream do Rocky Linux 9:
   ```bash
   sudo dnf install -y python3.11 python3.11-pip
   ```

2. Crie e ative um ambiente virtual isolado (`.venv`):
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```

3. Instale as dependências do runbook dentro do ambiente virtual:
   ```bash
   pip install -r requirements.txt
   ```

> [!TIP]
> Com o ambiente virtual `.venv` ativado, o comando `python3` apontará automaticamente para o Python 3.11, permitindo executar todos os comandos documentados na jornada (`python3 -m automation.python.kscctl ...`) de forma transparente e segura.

## Liberação de Portas (Firewall Interno)
| Porta | Protocolo | Origem | Destino | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| 443 | TCP | Admin | KSC Server | Console Web |
| 13000 | TCP | Endpoints | KSC Server | SSL Agent Comm |
| 14000 | TCP | Endpoints | KSC Server | Non-SSL Agent Comm |
| 13291 | TCP | Localhost | KSC Server | API Administrativa |

> [!WARNING]
> Se o PostgreSQL for instalado em um servidor remoto, a porta **5432/TCP** deve estar liberada entre o KSC Server e o DB Server.

## Usuário e Princípio de Privilégio Mínimo (Sudoers)

Para ambientes de homologação ou laboratório, o usuário operador pode utilizar permissões administrativas amplas. Entretanto, em ambientes corporativos e de produção, recomenda-se aplicar o **Princípio do Menor Privilégio**, restringindo o operador aos comandos estritamente necessários para o ciclo de vida do KSC e do PostgreSQL.

### Template Recomendado de Privilégios Mínimos (`/etc/sudoers.d/ksc-deploy`)

Crie o arquivo `/etc/sudoers.d/ksc-deploy` (com permissões `0440`) no servidor de destino:

```sudoers
# /etc/sudoers.d/ksc-deploy
# Regras de privilégio mínimo para implantação automatizada do Kaspersky Security Center

User_Alias KSC_OPS = kscdeploy

# Binários de Gerenciamento de Pacotes e Repositórios
Cmnd_Alias KSC_PKGS = /usr/bin/dnf, /usr/bin/rpm

# Binários de Gerenciamento de Serviços
Cmnd_Alias KSC_SERVICES = /usr/bin/systemctl start *, /usr/bin/systemctl stop *, \
                          /usr/bin/systemctl restart *, /usr/bin/systemctl reload *, \
                          /usr/bin/systemctl status *, /usr/bin/systemctl enable *, \
                          /usr/bin/systemctl is-active *

# Operações de Banco de Dados PostgreSQL sob o usuário de serviço
Cmnd_Alias KSC_DB = /usr/bin/runuser -u postgres -- /usr/bin/psql *, \
                    /usr/bin/su - postgres -c *

# Manipulação de Diretórios, Permissões e Arquivos de Configuração KSC/PostgreSQL
Cmnd_Alias KSC_FS = /usr/bin/mkdir, /usr/bin/chown, /usr/bin/chmod, /usr/bin/cp, /usr/bin/rm

# Setup KSC e SELinux
Cmnd_Alias KSC_SETUP = /opt/kaspersky/ksc64/lib/bin/setup/postinstall.pl, \
                       /usr/sbin/setenforce, /usr/sbin/getenforce, \
                       /usr/sbin/useradd, /usr/sbin/groupadd, /usr/sbin/userdel, /usr/sbin/groupdel

KSC_OPS ALL=(root) KSC_PKGS, KSC_SERVICES, KSC_DB, KSC_FS, KSC_SETUP
```

---

## Verificação Estrita de Chaves de Host SSH (MitM Prevention)

O módulo de execução remota da automação (`automation.python.remote`) adota rigorosamente a política `RejectPolicy()` do Paramiko. Conexões para servidores cujas chaves de host SSH não estejam cadastradas no arquivo local `~/.ssh/known_hosts` serão imediatamente recusadas por segurança, evitando ataques do tipo *Man-in-the-Middle* (MitM).

Antes de executar as rotinas de deploy ou verificação remota, registre a chave pública do servidor de destino:

```bash
# Registrar chave do servidor KSC no known_hosts local:
ssh-keyscan -H <ksc_host> >> ~/.ssh/known_hosts
```

---

## Passo 2.5 — Gerenciamento Seguro de Segredos e Cofre Cifrado

Todas as rotinas da automação KSC operam com sanitização contínua de memória e logs para evitar o vazamento acidental de credenciais (`KSC_DB_PASS`, `KSC_ADMIN_PASS`, `KSC_PASS`).

### Cofre Padrão (Recomendado)

O cofre criptográfico é o padrão recomendado para armazenamento seguro local:

```bash
python3 -m automation.python.init_config --vault
```

Isso grava as credenciais cifradas em `configs/secrets.bin`. Ao carregar configurações, o KSC Runbook prioriza o cofre cifrado de forma transparente.

### Modo Degradado (Arquivo `.env` em Texto Claro)

Caso a automação seja executada sem o cofre cifrado inicializado, o sistema utilizará as variáveis de ambiente ou o arquivo `configs/env/ksc_vars.env`.

> [!WARNING]
> A ausência de cofre cifrado aciona automaticamente um alerta de auditoria em log (`[SECURITY WARNING] Modo degradado: carregando credenciais a partir de arquivo .env em texto claro`).
> Em conformidade com as regras DevSecOps do repositório, o arquivo `.env` jamais deve ser commitado no Git. Verifique sempre se `configs/env/ksc_vars.env` permanece no `.gitignore`.

As variáveis de ambiente configuráveis são:
`KSC_DB_HOST`, `KSC_DB_PORT`, `KSC_DB_USER`, `KSC_FQDN`, `KSC_HOST`, `KSC_USER`, `KSC_WEB_PORT`, `KSC_SELINUX_MODE`, `KSC_DB_PASS`, `KSC_ADMIN_PASS`, `KSC_PASS`.

---
[Próximo Passo: Precheck >>](04-precheck.md)
