import paramiko
import os
import sys
import base64
import re


def emergency_fix_quotes(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        target_file = (
            "/var/opt/kaspersky/ksc-web-console/server/core/env-local/web-server.js"
        )

        # Read broken file
        stdin, stdout, stderr = client.exec_command(f"sudo -S cat {target_file}")
        stdin.write(password + "\n")
        stdin.flush()
        content = stdout.read().decode("utf-8")

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
        content = content.replace(
            "title: serverSelection.errorPage.title",
            "title: 'serverSelection.errorPage.title'",
        )
        content = content.replace(
            "message: serverSelection.errorPage.description",
            "message: 'serverSelection.errorPage.description'",
        )
        content = content.replace("product: ksc", "product: 'ksc'")
        content = content.replace(
            "runtime.logger.log(Checking IDM", "runtime.logger.log('Checking IDM"
        )
        content = content.replace("isInstalled)", "isInstalled')")
        content = content.replace(
            "runtime.logger.log(No IDM", "runtime.logger.log('No IDM"
        )
        content = content.replace(
            "installed. Checking XDR configuration)",
            "installed. Checking XDR configuration')",
        )
        content = content.replace(
            "runtime.logger.log(IS_XDR", "runtime.logger.log('IS_XDR"
        )
        content = content.replace("login page.)", "login page.')")
        content = content.replace(
            "response.render(public/info", "response.render('public/info'"
        )
        content = content.replace("response.redirect(/);", "response.redirect('/');")

        # ALSO fix the ones that are missing closing quotes
        # ... this is harder.

        # Fix the ones that are obviously just a word
        content = content.replace("/servers-ids", "'/servers-ids'")
        content = content.replace(
            "/service-authentication", "'/service-authentication'"
        )
        content = content.replace("/service-logout", "'/service-logout'")
        content = content.replace("/reactive-tests/", "'/reactive-tests/'")

        # Write back
        b64_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        client.exec_command(f"echo '{b64_content}' > /tmp/web-server-restored.txt")
        client.exec_command(
            f"base64 -d /tmp/web-server-restored.txt > /tmp/web-server-fixed.js"
        )
        stdin, stdout, stderr = client.exec_command(
            f"sudo -S cp /tmp/web-server-fixed.js {target_file}"
        )
        stdin.write(password + "\n")
        stdin.flush()

        # Restart
        client.exec_command("sudo -S systemctl restart KSCWebConsole.service")
        stdin.write(password + "\n")
        stdin.flush()

        print("Done!")
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    emergency_fix_quotes(host, user, password)
