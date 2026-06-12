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

        remote_script = """
files_to_print = [
    '1756292312_dynamic_registration.up.sql',
    '1756292320_grant_infinite.up.sql',
    '1760002529_dc_info_size.up.sql',
    '1764853655_change_ds_info_tenant_type.up.sql',
    '1769090852_account_external_id_change_length.up.sql',
    '1769180000_drop_unused_external_accounts_for_domain_users.up.sql',
    '1770629073_increase_resources_accounts_column_len.up.sql'
]

for f in files_to_print:
    print(f"\\n=================== FILE: {f} ===================")
    try:
        with open(f'/tmp/extracted_migrations/{f}', 'r', encoding='utf-8') as file_obj:
            print(file_obj.read())
    except Exception as e:
        print(f"Error reading file: {e}")
"""
        sftp = client.open_sftp()
        f = sftp.file("/tmp/view_remaining.py", "w")
        f.write(remote_script)
        f.close()
        sftp.close()

        stdin, stdout, stderr = client.exec_command("python3 /tmp/view_remaining.py")
        print(stdout.read().decode("utf-8"))

        client.exec_command("rm -f /tmp/view_remaining.py")
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
