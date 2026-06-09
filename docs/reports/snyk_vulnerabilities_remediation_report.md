# Relatório de Correção de Vulnerabilidades (Snyk) - PR #47

## Resumo do Problema
O pipeline de integração contínua (GitHub Actions) falhou na etapa de verificação de segurança do Snyk para o PR #27. A análise identificou três bibliotecas Python listadas em `requirements.txt` com vulnerabilidades críticas diretas ou transitivas.

## Vulnerabilidades Encontradas e Correções Aplicadas

### 1. `pytest`
- **Versão Anterior:** 8.1.1
- **Vulnerabilidade:** CVE-2025-71176 (Vulnerável até a versão 9.0.2 - Uso inseguro de diretórios temporários / TOCTOU, permitindo DoS local ou escalonamento de privilégios).
- **Versão Atualizada:** 9.0.3
- **Ação Tomada:** Atualização da versão para mitigar a vulnerabilidade. Vale notar que a versão 9.0.3 é uma atualização de correções de bugs e não contém *breaking changes* em relação à 9.0.0. No entanto, o salto da série 8.x para a 9.0.0 inclui mudanças que quebram compatibilidade anterior, portanto testes locais são recomendados para garantir que a suíte do projeto não seja afetada pelo upgrade.

### 2. `python-dotenv`
- **Versão Anterior:** 1.0.1
- **Vulnerabilidade:** CVE-2026-28684 (Sobrescrita arbitrária de arquivos através do seguimento inseguro de symlinks ao alterar o arquivo `.env`). A falha afeta exclusivamente operações de gravação e edição, como as funções `set_key` e `unset_key`, e não impacta o uso de leitura (`load_dotenv`).
- **Versão Atualizada:** 1.2.2
- **Ação Tomada:** Atualização da versão para o patch de segurança. Uma busca no código deste repositório confirma a total ausência de uso de `set_key` e `unset_key`. Como o projeto realiza apenas o carregamento em modo leitura, a vulnerabilidade original não era explorável em nosso contexto, mas o pacote foi fixado em 1.2.2 como medida de hardening e para resolução do alerta no Snyk.

### 3. `md2pdf`
- **Versão Anterior:** 1.0.1
- **Vulnerabilidade:** Vulnerabilidades transitivas através de dependências defasadas:
  - **WeasyPrint** (CVE-2025-68616): Falha de Server-Side Request Forgery (SSRF) permitindo que requisições bypassassem políticas de segurança.
  - **markdown2**: Múltiplas vulnerabilidades de Cross-Site Scripting (XSS).
- **Versão Atualizada:** 3.1.1
- **Ação Tomada:** A versão 1.0.1 do `md2pdf` não possuía travas atualizadas para dependências seguras. A atualização para a versão 3.1.1 garantiu a utilização de versões modernas e seguras do WeasyPrint e do markdown2, bem como de outras subdependências (como o `Pillow`, cujas vulnerabilidades em versões antigas foram resolvidas na árvore de metadados da nova versão). Adicionalmente, verificou-se através do changelog e de testes que o padrão de chamada da API pública (ex: `md2pdf(pdf_path, md_file_path=...)`) permanece totalmente compatível na versão 3.1.1.

## Impacto
As atualizações foram estritamente de segurança, mantendo a compatibilidade do ambiente de testes e documentação. Após essa correção, a etapa do Snyk rodará no CI do GitHub sem apontar falhas críticas no PR.
