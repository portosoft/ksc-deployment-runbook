# Pré-requisitos de Implantação

Antes de iniciar a instalação do Kaspersky Security Center 16.x, certifique-se de que todos os requisitos abaixo foram atendidos.

## 1. Infraestrutura de Hardware (Mínimo)
- **CPU**: 4 núcleos (64-bit).
- **RAM**: 8 GB (mínimo para KSC + PostgreSQL no mesmo host).
- **Disco**: 100 GB de espaço livre (SSD recomendado para o banco de dados).

## 2. Sistema Operacional
- **Distribuições Suportadas**: Rocky Linux 9.x ou Oracle Linux 9.x.
- **Tipo de Instalação**: "Server" ou "Minimal".
- **Configuração de Rede**:
    - Hostname estático definido (FQDN).
    - Endereço IP estático.
    - DNS funcional (resolução direta e reversa).

## 3. Banco de Dados (PostgreSQL 16)
- PostgreSQL 16 instalado e configurado.
- Extensão `standard_conforming_strings` deve estar configurada como `on`.
- Usuário `postgres` com acesso administrativo para criação dos bancos.

## 4. Portas de Rede (Firewall)
As seguintes portas devem estar abertas no `firewalld`:
- **8080/tcp**: Web Console (HTTP redirect).
- **8443/tcp**: Web Console (HTTPS).
- **13000/tcp**: Administration Server (SSL).
- **13001/tcp**: Administration Server (SSL para dispositivos móveis/externos).

Comando para liberação rápida:
```bash
sudo firewall-cmd --permanent --add-port={8080/tcp,8443/tcp,13000/tcp,13001/tcp}
sudo firewall-cmd --reload
```

## 5. Pacotes e Arquivos Necessários
Tenha em mãos os instaladores RPM fornecidos pela Kaspersky:
1. `ksc64-[versão].x86_64.rpm` (Administration Server).
2. `ksc-web-console-[versão].x86_64.rpm` (Web Console).
3. Arquivo de licença `.key`.

Pacotes base do sistema:
- `perl`, `zip`, `unzip`, `wget`, `curl`, `postgresql-server`.
