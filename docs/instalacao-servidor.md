# Instalação do Servidor KSC

Siga este roteiro para instalar o Kaspersky Security Center 16.x em sistemas Rocky Linux ou Oracle Linux 9.

## Sequência de Instalação

1. **Configuração Base**:
   - Defina o hostname: `sudo hostnamectl set-hostname kscserver.empresa.com`.
   - Atualize o sistema: `sudo dnf update -y`.

2. **Preparação do PostgreSQL**:
   - Instale e inicialize o DB (ver [Guia de Banco de Dados](./banco-de-dados.md)).
   - Certifique-se de que o serviço `postgresql-16` está ativo e habilitado.

3. **Instalação do Pacote KSC**:
   - Execute a instalação do RPM:
     ```bash
     sudo dnf install ksc64-[versão].x86_64.rpm
     ```

4. **Script de Pós-Instalação**:
   - Após a instalação do pacote, você deve rodar o script de configuração:
     ```bash
     sudo /opt/kaspersky/ksc64/lib/bin/setup/postinstall.pl
     ```
   - Siga as instruções na tela (aceite a licença, configure o banco de dados, defina as contas de serviço).

5. **Instalação da Web Console**:
   - Instale o pacote da console web:
     ```bash
     sudo dnf install ksc-web-console-[versão].x86_64.rpm
     ```
   - Configure a console:
     ```bash
     sudo /opt/kaspersky/ksc-web-console/setup/setup.sh
     ```

## Verificação de Serviços

Após a conclusão, todos os serviços abaixo devem estar com status `active (running)`:

| Serviço | Descrição | Comando de Verificação |
| :--- | :--- | :--- |
| `kladminserver_srv` | KSC Administration Server | `systemctl status kladminserver_srv` |
| `klwebsrv_srv` | KSC Web Console | `systemctl status klwebsrv_srv` |
| `kliam_srv` | Identity & Access Mgmt | `systemctl status kliam_srv` |
| `klnagent_srv` | Agente de Rede (Local) | `systemctl status klnagent_srv` |

## Validação de Portas

Verifique se o firewall está permitindo o tráfego nas portas essenciais:
```bash
sudo firewall-cmd --list-ports
# Deve exibir: 8080/tcp 8443/tcp 13000/tcp 13001/tcp
```

## Resultado Esperado
Ao final deste processo, você deverá conseguir acessar a console via:
`https://[IP-DO-SERVIDOR]:8443`
