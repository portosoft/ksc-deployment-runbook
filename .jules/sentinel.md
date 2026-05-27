# Sentinel Security Findings

## 2025-02-28 - [CRITICAL] Prevent Command Injection and Secret Exposure in Paramiko SSH Commands
**Vulnerability:** Many Python automation scripts in this codebase execute commands via `client.exec_command(f"echo {password} | sudo -S ...")` or `client.exec_command(f"echo '{secret_content}' > /path/to/file")`.
**Learning:** Passing passwords or secrets directly in shell strings inside `exec_command` exposes them in the system process list (`ps aux`) and causes them to be written to bash history. Furthermore, writing files via `echo '{content}' > file` introduces command injection vulnerabilities if the content contains a single quote (`'`), which would terminate the string and execute arbitrary commands. This is highly risky when constructing files with passwords or configurations.
**Prevention:** Always use `sftp.file('/path/to/file', 'w')` to securely write files to remote servers via SSH, completely avoiding the shell. For `sudo` commands, do not pipe `echo {password}`; instead, use `stdin, stdout, stderr = client.exec_command("sudo -S ...")` and then securely write the password via `stdin.write(password + "\n")` followed by `stdin.flush()`.

## 2024-05-24 - [CRITICAL] Prevent Command Injection and Secret Exposure in SSH Automation

**Vulnerability:** Automation scripts (`automation/setup/reconfigure_ksc_service.py`) were generating remote files containing sensitive passwords by dynamically constructing a multiline string and passing it via shell `echo` over an SSH connection. Furthermore, SSH passwords were being passed to `sudo` via shell `echo` piped to `sudo -S`.

**Learning:** Constructing strings for shell execution over SSH makes the system vulnerable to command injection if a secret contains special shell characters like single quotes, semicolons, or ampersands. It also risks exposing plaintext passwords in the remote machine's process table or bash history.

**Prevention:** Always rely on secure file transfer (SFTP/SCP) to write configuration files remotely instead of piping them through shell commands like `echo` or `cat`. Also, use standard `stdin.write()` via your SSH library to pass passwords when executing `sudo -S` dynamically to avoid exposing them on the command line.
