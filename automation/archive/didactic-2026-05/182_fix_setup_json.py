import paramiko
import os
from dotenv import load_dotenv


def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(host, username=user, password=password)
        print("--- Connected successfully to remote server ---")

        setup_json = """{
  "address": "kscserver.tail8b9ae.ts.net",
  "port": 8080,
  "trusted_cert": "",
  "trusted_cert_key": "",
  "defaultLanguageId": "pt-BR",
  "openAPIServers": [
    {
      "address": "kscserver.tail8b9ae.ts.net",
      "port": 13000,
      "openApiPort": 13299
    }
  ]
}"""

        # Write to a temporary file locally or on the remote server
        sftp = client.open_sftp()
        with sftp.open("/tmp/ksc-web-console-setup.json", "w") as f:
            f.write(setup_json)
        sftp.close()
        print("Uploaded remote file to /tmp/ksc-web-console-setup.json")

        # Move to /etc/ksc-web-console-setup.json with sudo
        cmds = [
            "sudo -S mv /tmp/ksc-web-console-setup.json /etc/ksc-web-console-setup.json",
            "sudo -S chown root:root /etc/ksc-web-console-setup.json",
            "sudo -S chmod 644 /etc/ksc-web-console-setup.json",
            "sudo -S cat /etc/ksc-web-console-setup.json",
            # We must run the setup script of Web Console to reconfigure it since the RPM post-install failed!
            # Wait, let's look at what the Web Console post-install script does. It configures the console.
            # Can we run it? Let's check if there is a script like /opt/kaspersky/ksc-web-console/setup/setup.sh
            "sudo -S find /opt/kaspersky -name 'setup.sh' 2>/dev/null",
            "sudo -S find /var/opt/kaspersky -name 'setup.sh' 2>/dev/null",
        ]

        for cmd in cmds:
            print(f"\n--- Running: {cmd} ---")
            stdin, stdout, stderr = client.exec_command(cmd)
            stdin.write(password + "\n")
            stdin.flush()
            out_bytes = stdout.read()
            err_bytes = stderr.read()
            print("STDOUT:")
            print(out_bytes.decode("utf-8", errors="replace").strip())
            print("STDERR:")
            print(err_bytes.decode("utf-8", errors="replace").strip())

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
