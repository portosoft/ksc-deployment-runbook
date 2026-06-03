# Sentinel Security Findings

## 2025-02-28 - [CRITICAL] Prevent Command Injection and Secret Exposure in Paramiko SSH Commands
**Vulnerability:** Many Python automation scripts in this codebase execute commands via `client.exec_command(f"echo {password} | sudo -S ...")` or `client.exec_command(f"echo '{secret_content}' > /path/to/file")`.
**Learning:** Passing passwords or secrets directly in shell strings inside `exec_command` exposes them in the system process list (`ps aux`) and causes them to be written to bash history. Furthermore, writing files via `echo '{content}' > file` introduces command injection vulnerabilities if the content contains a single quote (`'`), which would terminate the string and execute arbitrary commands. This is highly risky when constructing files with passwords or configurations.
**Prevention:** Always use `sftp.file('/path/to/file', 'w')` to securely write files to remote servers via SSH, completely avoiding the shell. For `sudo` commands, do not pipe `echo {password}`; instead, use `stdin, stdout, stderr = client.exec_command("sudo -S ...")` and then securely write the password via `stdin.write(password + "\n")` followed by `stdin.flush()`.

## 2024-05-24 - [CRITICAL] Prevent Command Injection and Secret Exposure in SSH Automation

**Vulnerability:** Automation scripts (`automation/setup/reconfigure_ksc_service.py`) were generating remote files containing sensitive passwords by dynamically constructing a multiline string and passing it via shell `echo` over an SSH connection. Furthermore, SSH passwords were being passed to `sudo` via shell `echo` piped to `sudo -S`.

**Learning:** Constructing strings for shell execution over SSH makes the system vulnerable to command injection if a secret contains special shell characters like single quotes, semicolons, or ampersands. It also risks exposing plaintext passwords in the remote machine's process table or bash history.

**Prevention:** Always rely on secure file transfer (SFTP/SCP) to write configuration files remotely instead of piping them through shell commands like `echo` or `cat`. Also, use standard `stdin.write()` via your SSH library to pass passwords when executing `sudo -S` dynamically to avoid exposing them on the command line.

## 2025-02-28 - [MEDIUM] Prevent remote process hang (DoS risk) via SSH EOF
**Vulnerability:** Several Python automation scripts use `paramiko` to execute commands that expect input via stdin (e.g. `sudo -S` or interactive prompts). These scripts would pass input via `stdin.write()` and `stdin.flush()`, but would never signal the end of input by shutting down the write channel.
**Learning:** Failing to send an EOF (`stdin.channel.shutdown_write()`) when passing payloads or commands to interactive processes via Paramiko can cause the remote process to hang indefinitely, waiting for more input. Over time or across many executions, this leads to resource exhaustion and potential Denial of Service (DoS) scenarios on the remote target.
**Prevention:** Always call `stdin.channel.shutdown_write()` after writing and flushing data to a Paramiko `stdin` object for interactive processes. This sends the necessary EOF signal to unblock the remote process.

## 2024-05-24 - Prevent Local Credential and Audit Log Exposure via Strict Permissions
**Vulnerability:** Automation scripts (`env_to_ansible.py` and `logging_utils.py`) generated files containing sensitive credentials (YAML vars) and detailed audit evidence without restricting permissions. The default UMASK allowed read access for other local users on the system, potentially exposing secrets and environmental data.
**Learning:** Local credential exposure is a common risk when scripts convert configuration files or dump execution logs. Even when secrets aren't hardcoded in the script, dynamically generating files containing secrets or security-relevant logs requires explicit permission control.
**Prevention:** Always enforce explicit, strict permissions (`0o600` for files, `0o700` for directories) when dynamically creating files containing credentials or sensitive logging/audit evidence. Use `os.makedirs(mode=0o700)` or `os.open(..., 0o600)` during creation, or apply `os.chmod()` immediately afterwards (or via `pathlib.Path.touch(mode=0o600)`).
