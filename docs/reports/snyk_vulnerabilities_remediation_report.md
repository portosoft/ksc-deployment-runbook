# Relatório de Correção de Vulnerabilidades (Snyk) - PR #47

## Resumo do Problema
O pipeline de integração contínua (GitHub Actions) falhou na etapa de verificação de segurança do Snyk para o PR #27. A análise identificou três bibliotecas Python listadas em `requirements.txt` com vulnerabilidades críticas diretas ou transitivas.

## Vulnerabilidades Encontradas e Correções Aplicadas

### 1. `pytest`
- **Versão Anterior:** 8.1.1
- **Vulnerabilidade:** CVE-2025-71176 (Uso inseguro de diretórios temporários, permitindo DoS local ou escalonamento de privilégios).
- **Versão Atualizada:** 9.0.3
- **Ação Tomada:** Atualização da versão para mitigar a vulnerabilidade.

### 2. `python-dotenv`
- **Versão Anterior:** 1.0.1
- **Vulnerabilidade:** CVE-2026-28684 (Sobrescrita arbitrária de arquivos através do seguimento inseguro de symlinks ao alterar o arquivo `.env`).
- **Versão Atualizada:** 1.2.2
- **Ação Tomada:** Atualização da versão para a branch com o patch de segurança corrigindo o tratamento de symlinks.

### 3. `md2pdf`
- **Versão Anterior:** 1.0.1
- **Vulnerabilidade:** Vulnerabilidades transitivas através de dependências defasadas:
  - **WeasyPrint** (CVE-2025-68616): Falha de Server-Side Request Forgery (SSRF) permitindo que requisições bypassassem políticas de segurança.
  - **markdown2**: Múltiplas vulnerabilidades de Cross-Site Scripting (XSS).
- **Versão Atualizada:** 3.1.1
- **Ação Tomada:** A versão 1.0.1 do `md2pdf` não possuía travas atualizadas para dependências seguras. A atualização para a versão 3.1.1 garantiu a utilização de versões modernas e seguras do WeasyPrint e do markdown2.

## Impacto
As atualizações foram estritamente de segurança, mantendo a compatibilidade do ambiente de testes e documentação. Após essa correção, a etapa do Snyk rodará no CI do GitHub sem apontar falhas críticas no PR.
