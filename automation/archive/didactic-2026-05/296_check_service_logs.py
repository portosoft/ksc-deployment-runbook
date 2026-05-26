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
        print("Connected.")

        def run_cmd(cmd):
            use_sudo = "sudo" in cmd
            run_cmd = cmd.replace("sudo", "sudo -S", 1) if use_sudo else cmd
            stdin, stdout, stderr = client.exec_command(run_cmd)
            if use_sudo:
                stdin.write(password + "\n")
                stdin.flush()
            out = stdout.read().decode("utf-8", errors="replace").strip()
            err = stderr.read().decode("utf-8", errors="replace").strip()
            return out, err

        print("=== kladminserver_srv Status ===")
        out, _ = run_cmd("systemctl status kladminserver_srv --no-pager -l")
        print(out.encode("ascii", errors="replace").decode("ascii"))

        print("\n=== kladminserver_srv Recent Logs ===")
        out_logs, _ = run_cmd("sudo journalctl -u kladminserver_srv -n 30 --no-pager")
        clean_logs = "\n".join(
            [
                line
                for line in out_logs.split("\n")
                if "senha" not in line and "password" not in line
            ]
        )
        print(clean_logs.encode("ascii", errors="replace").decode("ascii"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
