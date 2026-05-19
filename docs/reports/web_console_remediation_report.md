# Relatório Técnico: Remediação do Kaspersky Security Center Web Console 16.2

## 1. Contexto e Identificação do Problema

Durante a validação pós-instalação da infraestrutura do **Kaspersky Security Center (KSC) 16.2** no servidor Rocky Linux 9 (`kscserver.tail8b9ae.ts.net`), foram constatados dois sintomas críticos no console web:

1. **Falha de Acesso via Protocolo Seguro (HTTPS)**: O serviço `ksc-web-console` estava no ar e escutando na porta TCP `8080`, mas as requisições HTTPS falhavam e as tentativas HTTP comuns recebiam uma mensagem de protocolo inválido.
2. **Layout Descaracterizado (Página de Erro Interna)**: Quando acessada a porta correta, o servidor renderizava uma página de erro genérica em vez do formulário de autenticação: *"Configuração incorreta do Kaspersky Security Center. Tente reinstalar o aplicativo, e então especifique os Servidores de Administração confiáveis..."*.

## 2. Análise Diagnóstica e Engenharia Reversa

### A. Investigação do Comportamento do Serviço
Iniciamos a inspeção baixando e analisando o script de instalação oficial `/var/opt/kaspersky/ksc-web-console/setup.js` e as configurações aplicadas.

- O arquivo padrão de setup `/etc/ksc-web-console-setup.json` utilizava a chave `"openAPIServers"` para declarar o servidor de administração da Kaspersky.
- No entanto, a análise do bundle compilado do `setup.js` revelou que a propriedade correspondente para registrar servidores no pool interno do console web é `"trusted"`.
- Por conta dessa discrepância, a lista de servidores em `/var/opt/kaspersky/ksc-web-console/server/config.json` foi gerada vazia:
  ```json
  "openAPIServers": {
    "pools": [
      {
        "displayName": "Trusted servers",
        "servers": []
      }
    ]
  }
  ```
- O código do servidor Web (`web-server.js`) intercepta as requisições e, se a contagem de servidores válidos for zero (`!this.serversCount`), redireciona o usuário para a página de erro `private/error-iam` (gerando a tela descaracterizada relatada).

### B. Mapeamento de Parâmetros do `setup.js`
A função interna `u` do script de setup foi mapeada para decodificar o parâmetro `"trusted"` fornecido no JSON de configuração:

```javascript
function u({workingDir: e, trusted: t}) {
  if ("object" != typeof t) {
    return t && "NULL" !== t ? t.split("||").map(r => {
      const [t, o, n, i] = r.split("|");
      return { displayName: i, address: t, port: o, certPath: l(n, e), version: "v1.0" }
    }) : []
  }
  // Se for objeto, processa chaves (kscHost, kscPort, kscCertPath)
}
```

## 3. Implementação da Solução

Para corrigir a falha de provisionamento e ativar o acesso HTTPS nativo, adotamos as seguintes etapas:

1. **Elaboração da Configuração Corrigida**:
   Geramos um arquivo temporário `/tmp/ksc-web-console-setup-accepted.json` estruturado de forma compatível com o parser:
   ```json
   {
     "acceptEula": true,
     "address": "kscserver.tail8b9ae.ts.net",
     "port": 8080,
     "defaultLanguageId": "pt-BR",
     "trusted": {
       "kscserver.tail8b9ae.ts.net": {
         "kscHost": "127.0.0.1",
         "kscPort": 13299,
         "kscCertPath": "/var/opt/kaspersky/ksc-web-console/KLRootCA.crt"
       }
     }
   }
   ```

2. **Reconfiguração Não-Interativa**:
   Executamos o instalador apontando para o novo arquivo JSON com permissões administrativas elevadas:
   ```bash
   sudo bash -c 'cd /var/opt/kaspersky/ksc-web-console && ./node setup.js /tmp/ksc-web-console-setup-accepted.json'
   ```

3. **Garantia de Persistência**:
   O arquivo de configuração permanente do sistema `/etc/ksc-web-console-setup.json` foi atualizado com essa mesma estrutura sanitizada para evitar retrocessos em futuras execuções automáticas de atualização ou reinstalação do pacote RPM.

4. **Reinício e Ciclo de Vida do Serviço**:
   O serviço foi reiniciado com o comando `systemctl restart ksc-web-console`, forçando a leitura do novo arquivo `config.json`.

## 4. Validação Visual e de Conectividade

O status final do console web foi testado com sucesso:

- **Protocolo HTTPS**: Respondendo perfeitamente na porta `8080`.
- **Status HTTP**: `302 Found` direcionando para `/login`.
- **Integridade da Interface**: Uma sessão via navegador automatizado confirmou a renderização correta de todos os estilos CSS, fontes e formulários de credenciais de login.

Abaixo está o registro da tela de login renderizada corretamente:

![Login KSC Web Console](file:///C:/Users/F%C3%A1bioMendes/.gemini/antigravity/brain/587fdae5-cebb-4fbc-817c-71812dc64c20/ksc_login_page_1779217460337.png)

---
**Status:** Concluído com sucesso. Todos os scripts locais de apoio criados na pasta `scratch` foram higienizados e devidamente arquivados em `automation/archive/didactic-2026-05/`.
