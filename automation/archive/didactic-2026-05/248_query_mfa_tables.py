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
        print("Connected.")

        tables = [
            "v_usrexpmfasettings",
            "v_usrexpmfasecrets",
            "v_usrexpmfaexceptions",
            "v_ak_users_and_groups_with_mfa",
        ]
        for t in tables:
            q = f"SELECT * FROM {t} LIMIT 10;"
            cmd = f'sudo -S -u postgres psql -d ksc -c "{q}"'
            stdin, stdout, stderr = client.exec_command(cmd)
            stdin.write(password + "\n")
            stdin.flush()

            print(f"=== Table: {t} ===")
            print(stdout.read().decode("utf-8"))
            print("-" * 50)

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
