import paramiko
import os
import sys
import base64


def fix_bootstrap_order(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        target_file = "/var/opt/kaspersky/ksc-web-console/server/index.js"

        # Read file
        stdin, stdout, stderr = client.exec_command(f"sudo -S cat {target_file}")
        stdin.write(password + "\n")
        stdin.flush()
        content = stdout.read().decode("utf-8")

        # Pattern to find the block
        # await this.setupSessionManager();
        # await this.setupApiModule();
        # const serverSetupFilePath = path_1.default.resolve(__dirname, 'core', config.targetFolder, 'server');
        # const BusinessLogicServer = await (0, dynamic_import_module_1.dynamicImportModule)(serverSetupFilePath, 'BusinessLogicServer');
        # const businessLogicServer = new BusinessLogicServer();
        # await businessLogicServer.init();

        # We want to move setupSessionManager and setupApiModule AFTER new BusinessLogicServer()

        old_block = """        await this.setupSessionManager();
        await this.setupApiModule();
        const serverSetupFilePath = path_1.default.resolve(__dirname, 'core', config.targetFolder, 'server');
        const BusinessLogicServer = await (0, dynamic_import_module_1.dynamicImportModule)(serverSetupFilePath, 'BusinessLogicServer');
        const businessLogicServer = new BusinessLogicServer();
        await businessLogicServer.init();"""

        new_block = """        const serverSetupFilePath = path_1.default.resolve(__dirname, 'core', config.targetFolder, 'server');
        const BusinessLogicServer = await (0, dynamic_import_module_1.dynamicImportModule)(serverSetupFilePath, 'BusinessLogicServer');
        const businessLogicServer = new BusinessLogicServer();
        await this.setupSessionManager();
        await this.setupApiModule();
        await businessLogicServer.init();"""

        if old_block in content:
            content = content.replace(old_block, new_block)
            print("Block found and replaced.")
        else:
            # Try a less strict match if whitespace differs
            print("Exact block not found, trying alternative match...")
            # Fallback logic could go here if needed
            pass

        # Write back
        b64_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        client.exec_command(f"echo '{b64_content}' > /tmp/server-index-fixed.txt")
        client.exec_command(
            f"base64 -d /tmp/server-index-fixed.txt > /tmp/server-index-fixed.js"
        )
        stdin, stdout, stderr = client.exec_command(
            f"sudo -S cp /tmp/server-index-fixed.js {target_file}"
        )
        stdin.write(password + "\n")
        stdin.flush()

        # RESTART
        print("--- Restarting ---")
        client.exec_command("sudo -S killall -9 node")
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

    fix_bootstrap_order(host, user, password)
