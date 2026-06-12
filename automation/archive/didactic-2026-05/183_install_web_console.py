import paramiko
import os
from dotenv import load_dotenv


def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())

    try:
        client.connect(host, username=user, password=password)
        print("--- Connected successfully to remote server ---")

        # 1. Check/create /etc/ksc-web-console-setup.json
        # We can run bash command to safely create the file
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
        # Escape single quotes and write to a temp file, then move to /etc/ksc-web-console-setup.json
        cmd_create_json = (
            f"sudo -S bash -c \"echo '{setup_json}' > /etc/ksc-web-console-setup.json\""
        )
        print(f"\n--- Creating setup.json: {cmd_create_json} ---")
        stdin, stdout, stderr = client.exec_command(cmd_create_json)
        stdin.write(password + "\n")
        stdin.flush()
        print("STDOUT:", stdout.read().decode("utf-8", errors="replace").strip())
        print("STDERR:", stderr.read().decode("utf-8", errors="replace").strip())

        # 2. Install Web Console RPM
        cmd_install = (
            "sudo -S rpm -ivh /home/suporte/ksc-web-console-16.2.11309.x86_64.rpm"
        )
        print(f"\n--- Installing Web Console: {cmd_install} ---")
        stdin, stdout, stderr = client.exec_command(cmd_install)
        stdin.write(password + "\n")
        stdin.flush()
        print("STDOUT:", stdout.read().decode("utf-8", errors="replace").strip())
        print("STDERR:", stderr.read().decode("utf-8", errors="replace").strip())

        # 3. Check status of Web Console service
        cmd_status = "sudo -S systemctl status ksc-web-console --no-pager"
        print(f"\n--- Checking service status: {cmd_status} ---")
        stdin, stdout, stderr = client.exec_command(cmd_status)
        stdin.write(password + "\n")
        stdin.flush()
        print("STDOUT:", stdout.read().decode("utf-8", errors="replace").strip())
        print("STDERR:", stderr.read().decode("utf-8", errors="replace").strip())

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
