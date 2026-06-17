import paramiko


def fix_quotes(client: paramiko.SSHClient, password: str) -> None:
    target_file = (
        "/var/opt/kaspersky/ksc-web-console/server/core/env-local/web-server.js"
    )

    # Read broken file
    stdin, stdout, stderr = client.exec_command(f"sudo -S cat {target_file}")
    stdin.write(password + "\n")
    stdin.flush()
    # Fix: Prevent the remote process from hanging indefinitely
    stdin.channel.shutdown_write()

    content = stdout.read().decode("utf-8")
    status = stdout.channel.recv_exit_status()
    if status != 0:
        err_msg = stderr.read().decode("utf-8")
        raise RuntimeError(f"Failed to read {target_file}: {err_msg}")

    # Fix known broken strings
    content = content.replace(
        "runtime.logger.error(An error occurred",
        "runtime.logger.error('An error occurred",
    )
    content = content.replace(
        "while counting servers:, err);", "while counting servers:', err);"
    )
    content = content.replace(
        "res.render(private/error-iam", "res.render('private/error-iam'"
    )

    # Write fixed content back using tee
    stdin_write, stdout_write, stderr_write = client.exec_command(
        f"sudo -S tee {target_file} > /dev/null"
    )
    # Write password for sudo, then the content, securely through stdin
    stdin_write.write(password + "\n")
    stdin_write.write(content)
    stdin_write.flush()
    # Fix: Prevent the remote tee process from hanging indefinitely
    stdin_write.channel.shutdown_write()

    status_write = stdout_write.channel.recv_exit_status()
    if status_write != 0:
        err_msg = stderr_write.read().decode("utf-8")
        raise RuntimeError(f"Failed to write to {target_file}: {err_msg}")
