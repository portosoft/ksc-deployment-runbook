# Relatório Técnico: Estabilização do KSC 16.2 Web Console
**Data:** 11 de Maio de 2026
**Ambiente:** Rocky Linux 9.7 (KSC Server: kscserver.tail8b9ae.ts.net)

---

## 1. Status Geral
O Kaspersky Security Center Web Console está operando com um serviço estável (`systemd`), mas o acesso via navegador resulta em erro de **"Incorrect configuration"** ou falha catastrófica de backend devido a um loop de crash identificado recentemente.

---

## 2. Problemas Resolvidos (Vencidos)
*   **Conflito de Porta (EADDRINUSE):** A porta `13299` estava sendo ocupada pelo Administration Server, impedindo o Web Console de iniciar.
    *   **Solução:** Web Console reconfigurado para a porta `8080`.
*   **Configuração de Rede:** `config.json` atualizado para escutar em `0.0.0.0` e o pool de servidores confiáveis foi populado com o FQDN correto.
*   **Integridade do Código:** Corrigida sintaxe quebrada em `server/core/env-local/web-server.js` resultante de injeções de depuração agressivas.

---

## 3. Problemas Críticos Atuais (Bloqueios)

### 3.1. Crash Loop no Session Manager
*   **Erro:** `TypeError: Cannot read properties of undefined (reading 'getHashMap')`
*   **Localização:** `node_modules/@kl/openapi-module/lib/local/domains/session-manager/core-session-manager.js:374:70`
*   **Causa Raiz:** O objeto `runtime.tempDataStore` está `undefined` no momento em que o `setInterval` de `initClientIdleTimersCheck` tenta acessar o banco de dados temporário (In-Memory ou Redis).
*   **Impacto:** O processo Node.js reinicia continuamente (status `activating` ou crash silencioso).

### 3.2. Falha na Ordem de Inicialização (Race Condition)
*   **Observação:** O construtor da classe base `BusinessLogicServer` (`server/core/server.js`) é responsável por chamar `runtime.extend('tempDataStore', ... )`.
*   **Hipótese:** O `CoreSessionManager` está sendo instanciado e disparando timers antes que a extensão do `runtime` seja concluída.
*   **Evidência:** Logs de depuração injetados no construtor da classe base não estão sendo registrados, sugerindo que a execução sequencial está sendo interrompida ou ignorada por algum orquestrador (`pm.js`).

### 3.3. Bloqueio Lógico no Frontend (`serversCount === 0`)
*   **Erro:** Mesmo quando o servidor não crasha, a página retorna "Incorrect configuration".
*   **Diagnóstico:** O arquivo `web-server.js` inicializa `this.serversCount = 0`. Ele falha em contar os servidores no `config.json`, disparando a página de erro de seleção de servidor.
*   **Possível Causa:** Falha na desserialização do `config.json` ou falha na validação do FQDN contra a lista de `openAPIServers`.

---

## 4. Desafios de Observabilidade
*   **Redirecionamento de Logs:** `console.error` e `stdout` parecem ser capturados pelo orquestrador `pm.js` e não são propagados de forma consistente para o `journalctl`.
*   **Sincronização de Relógio:** Discrepância notada entre o relógio do sistema e os carimbos de data/hora nos arquivos de log (atraso de ~24min), dificultando a correlação de eventos em tempo real.

---

## 5. Próximos Passos Recomendados
1.  **Auditoria de Dependências de Inicialização:** Verificar onde `runtime` é globalmente definido e por que `tempDataStore` não está persistindo.
2.  **Bypass de Timer:** Desativar temporariamente `initClientIdleTimersCheck` no código compilado para validar se o servidor consegue completar o `init()` sem o crash.
3.  **Validação de Config:** Criar um script Node.js isolado que utilize as mesmas bibliotecas internas (`@kl/openapi-module`) para testar o carregamento do `config.json` fora do contexto do serviço.
