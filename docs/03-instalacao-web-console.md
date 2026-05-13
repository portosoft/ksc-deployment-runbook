# 03 - Instalação da Web Console

A falha mais comum é instalar a Web Console sem o arquivo de resposta prévio. Siga esta sequência rigorosamente.

## Fase 2: Configuração do Setup JSON

O arquivo `/etc/ksc-web-console-setup.json` **DEVE** existir antes da instalação do RPM.

1. **Criar o arquivo de resposta**:
   ```bash
   sudo tee /etc/ksc-web-console-setup.json << 'EOF'
   {
     "address": "FQDN_AQUI",
     "port": 8080,
     "trusted_cert": "",
     "defaultLanguageId": "pt-BR",
     "openAPIServers": [
       {
         "address": "FQDN_AQUI",
         "port": 13000,
         "openApiPort": 13299
       }
     ]
   }
   EOF
   ```

2. **Instalar o pacote da Web Console**:
   ```bash
   sudo rpm -ivh ksc-web-console-16.2.11309.x86_64.rpm
   ```

3. **Verificar o `config.json` gerado**:
   ```bash
   cat /var/opt/kaspersky/ksc-web-console/server/config.json
   ```
   Confirme se o campo `openAPIServers` contém o FQDN correto.
