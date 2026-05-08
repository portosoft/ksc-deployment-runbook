# Arquitetura do Sistema

Esta seção descreve a arquitetura alvo para a implantação do Kaspersky Security Center (KSC) 16.x em ambiente Linux.

## Componentes Principais

### 1. KSC Administration Server (Linux)
O componente central que gerencia a segurança da rede. No Linux, ele roda como um conjunto de serviços nativos.
- **Backend**: Executado em Rocky Linux 9 ou Oracle Linux 9.
- **Serviços**: `kladminserver_srv`, `klnagent_srv`.

### 2. Banco de Dados (PostgreSQL 16)
O KSC utiliza o PostgreSQL como motor de banco de dados para armazenar políticas, inventários e eventos.
- **Versão**: PostgreSQL 16 (recomendado para performance e ***REMOVED*** a longo prazo).
- **Localização**: Pode ser instalado no mesmo servidor (standalone) ou em um servidor dedicado.

### 3. KSC Web Console
Interface de administração baseada em web, permitindo o gerenciamento via navegador.
- **Portas**: 8080 (HTTP) e 8443 (HTTPS).
- **Serviço**: `klwebsrv_srv`.

### 4. Kaspersky Identity and Access Management (IAM)
Serviço de gerenciamento de identidade para autenticação na Web Console.
- **Serviço**: `kliam_srv`.

## Fluxo de Comunicação e Portas

| Origem | Destino | Porta/Protocolo | Descrição |
| :--- | :--- | :--- | :--- |
| Administrador | Web Console | 8443/tcp | Acesso HTTPS à interface web |
| Agentes (End-points) | KSC Server | 13000/tcp | Conexão SSL dos agentes |
| Agentes (End-points) | KSC Server | 14000/tcp | Conexão não-comprimida (opcional) |
| KSC Server | Agentes | 15000/udp | Notificação de ativação (Wake-on-LAN) |
| Web Console | KSC Server | 13291/tcp | Comunicação interna entre console e server |

## Premissas de Design
- **Estabilidade**: Uso de distros RHEL-compliant (Rocky/Oracle) para ***REMOVED*** enterprise.
- **Repetibilidade**: Instalação baseada em pacotes RPM e automação.
- **Segurança**: Comunicação criptografada e isolamento de banco de dados.
