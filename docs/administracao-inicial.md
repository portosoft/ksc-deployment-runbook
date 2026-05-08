# Administração Inicial

Após a instalação bem-sucedida, siga estes passos para configurar o ambiente básico do Kaspersky Security Center.

## Primeiro Acesso

1. Abra o navegador e acesse: `https://[hostname-ou-ip]:8443`.
2. No primeiro login, utilize as credenciais definidas durante o script de `postinstall.pl`.
3. Caso tenha optado pela autenticação do sistema, utilize um usuário com privilégios administrativos no Linux que faça parte do grupo `kladmin`.

## Configurações Recomendadas

### 1. Assistente de Início Rápido
Ao logar pela primeira vez, o KSC iniciará um assistente.
- **Licenciamento**: Adicione seu arquivo `.key` ou código de ativação.
- **Atualizações**: Configure a tarefa de download de atualizações para o repositório do servidor.
- **Inventário**: Defina a frequência de busca de dispositivos na rede.

### 2. Estrutura de Grupos
Organize seus dispositivos em grupos de administração.
- Exemplo: `Servidores`, `Workstations`, `Mobile`, `VDI`.

### 3. Políticas Iniciais
Crie ou importe as políticas para o Agente de Rede e para o Endpoint Security (KES).
- **Proteção por senha**: Ative a proteção por senha para evitar desinstalações não autorizadas.
- **Rede**: Configure os endereços de conexão (Connection Profiles).

## Gerenciamento de Usuários (IAM)
O serviço `kliam_srv` gerencia quem pode acessar a console.
- Crie usuários dedicados para diferentes níveis de administração (ex.: `ksc_readonly`, `ksc_operator`).
- **Segurança**: Evite usar o usuário `root` para administração diária.

## Verificação de Saúde (Health Check)
Verifique periodicamente o dashboard principal:
- Status de proteção dos computadores.
- Banco de dados de vírus atualizado.
- Espaço em disco no servidor KSC.
