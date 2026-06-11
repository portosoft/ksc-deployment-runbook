import paramiko
import time
import sys
import re

hostname = "kscserver.tail8b9ae.ts.net"
username = "suporte"
password = "[REDACTED_SSH_PASS]"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())

print(f"Connecting to {hostname}...")
client.connect(hostname, username=username, password=password)

shell = client.invoke_shell()


def wait_for_prompt(timeout=30):
    end_time = time.time() + timeout
    output = ""
    while time.time() < end_time:
        if shell.recv_ready():
            chunk = shell.recv(4096).decode("utf-8", errors="replace")
            output += chunk
            if re.search(r"(#|\$)\s*$", output):
                time.sleep(0.2)
                if shell.recv_ready():
                    output += shell.recv(4096).decode("utf-8", errors="replace")
                return output
        time.sleep(0.1)
    return output


print("Waiting for initial prompt...")
wait_for_prompt()

print("Sending 'sudo su -'...")
shell.send("sudo su -\n")
time.sleep(1)
out = shell.recv(4096).decode("utf-8", errors="replace")
if "senha" in out.lower() or "password" in out.lower():
    shell.send(password + "\n")
    time.sleep(1)
    shell.recv(4096)

print("Starting postinstall.pl wizard...")
shell.send(
    "LD_LIBRARY_PATH=/opt/kaspersky/ksc64/lib /opt/kaspersky/ksc64/lib/bin/setup/postinstall.pl\n"
)

buffer = ""
log_file = open("postinstall_interactive_log.txt", "w", encoding="utf-8")

start_time = time.time()
last_action_time = time.time()

accepted_eula = False
accepted_priv = False
sent_install_mode = False
accepted_ksn = False

selected_dbms_count = 0
dbhost_count = 0
dbport_count = 0
dbuser_count = 0
dbpass_count = 0

sent_dbname = False
sent_iamname = False
sent_fqdn = False
sent_iam_fqdn = False
sent_runas = False
sent_runas_others = False
sent_runas_kliam = False
sent_group = False
sent_admin_user = False
sent_admin_pass = False
sent_admin_pass_confirm = False

answered_generic_prompts = set()

while time.time() - start_time < 900:  # Max 15 minutes
    if shell.recv_ready():
        chunk = shell.recv(4096).decode("utf-8", errors="replace")
        buffer += chunk
        log_file.write(chunk)
        log_file.flush()

        try:
            sys.stdout.write(
                chunk.encode(sys.stdout.encoding, errors="replace").decode(
                    sys.stdout.encoding
                )
            )
            sys.stdout.flush()
        except Exception:
            pass

        last_action_time = time.time()

    # Pager handling
    if re.search(r"--mais--\(\d+%\)|--more--\(\d+%\)", buffer, re.IGNORECASE):
        shell.send(" ")
        buffer = re.sub(
            r"--mais--\(\d+%\)|--more--\(\d+%\)", "", buffer, flags=re.IGNORECASE
        )
        time.sleep(0.05)
        continue

    lower_buf = buffer.lower()

    # 1. EULA Accept
    if (
        not accepted_eula
        and "accept the terms of the end" in lower_buf
        and "[n]:" in lower_buf
    ):
        shell.send("Y\n")
        accepted_eula = True
        buffer = ""
        print("\n[ROBUST-SENT: Y (EULA)]")
        time.sleep(1)
        continue

    # 2. Privacy Policy Accept
    if not accepted_priv and "privacy policy" in lower_buf and "[n]:" in lower_buf:
        shell.send("Y\n")
        accepted_priv = True
        buffer = ""
        print("\n[ROBUST-SENT: Y (Privacy Policy)]")
        time.sleep(1)
        continue

    # 2.5. Installation Mode
    if (
        not sent_install_mode
        and "choose the administration server installation mode" in lower_buf
        and "]:" in lower_buf
    ):
        shell.send("1\n")
        sent_install_mode = True
        buffer = ""
        print("\n[ROBUST-SENT: 1 (Installation Mode Standard)]")
        time.sleep(1.5)
        continue

    # 3. KSN Accept
    if (
        not accepted_ksn
        and "kaspersky security network" in lower_buf
        and "ksn" in lower_buf
        and "[n]:" in lower_buf
    ):
        shell.send("Y\n")
        accepted_ksn = True
        buffer = ""
        print("\n[ROBUST-SENT: Y (KSN)]")
        time.sleep(1)
        continue

    # 4. DBMS Type
    if (
        selected_dbms_count < 2
        and "choose" in lower_buf
        and "dbms" in lower_buf
        and ("]:" in lower_buf or lower_buf.strip().endswith(":"))
    ):
        match = re.search(r"(\d+)\.\s+postgres", lower_buf)
        if match:
            db_num = match.group(1)
            shell.send(f"{db_num}\n")
            print(f"\n[ROBUST-SENT DBMS ({selected_dbms_count + 1}): {db_num}]")
        else:
            shell.send("2\n")  # Postgres is standard 2 in this prompt list
            print(
                f"\n[ROBUST-SENT DBMS ({selected_dbms_count + 1}): 2 (Fallback Postgres)]"
            )
        selected_dbms_count += 1
        buffer = ""
        time.sleep(1.5)
        continue

    # 5. Hostname / DBMS Address
    if (
        dbhost_count < 2
        and ("database server hostname" in lower_buf or "dbms address" in lower_buf)
        and ("]:" in lower_buf or lower_buf.strip().endswith(":"))
    ):
        shell.send("127.0.0.1\n")
        dbhost_count += 1
        buffer = ""
        print(f"\n[ROBUST-SENT HOSTNAME ({dbhost_count}): 127.0.0.1]")
        time.sleep(1.5)
        continue

    # 6. Port / DBMS Port
    if (
        dbport_count < 2
        and ("database server port" in lower_buf or "dbms port" in lower_buf)
        and ("]:" in lower_buf or lower_buf.strip().endswith(":"))
    ):
        shell.send("5432\n")
        dbport_count += 1
        buffer = ""
        print(f"\n[ROBUST-SENT PORT ({dbport_count}): 5432]")
        time.sleep(1.5)
        continue

    # 7. Database Name (KSC)
    if (
        not sent_dbname
        and "database name" in lower_buf
        and "identity" not in lower_buf
        and "iam" not in lower_buf
        and ("]:" in lower_buf or lower_buf.strip().endswith(":"))
    ):
        shell.send("ksc\n")
        sent_dbname = True
        buffer = ""
        print("\n[ROBUST-SENT DB NAME: ksc]")
        time.sleep(1.5)
        continue

    # 8. Database Name (IAM)
    if (
        not sent_iamname
        and ("identity" in lower_buf or "iam" in lower_buf)
        and "database name" in lower_buf
        and ("]:" in lower_buf or lower_buf.strip().endswith(":"))
    ):
        shell.send("ksciam\n")
        sent_iamname = True
        buffer = ""
        print("\n[ROBUST-SENT IAM DB: ksciam]")
        time.sleep(1.5)
        continue

    # 9. DB User Name / DBMS Login
    if (
        dbuser_count < 2
        and ("dbms user name" in lower_buf or "dbms login" in lower_buf)
        and ("]:" in lower_buf or lower_buf.strip().endswith(":"))
    ):
        shell.send("kluser\n")
        dbuser_count += 1
        buffer = ""
        print(f"\n[ROBUST-SENT DB USER ({dbuser_count}): kluser]")
        time.sleep(1.5)
        continue

    # 10. DB Password
    if (
        dbpass_count < 2
        and "dbms" in lower_buf
        and "password" in lower_buf
        and buffer.strip().endswith(":")
    ):
        shell.send("[REDACTED_DB_PASS]\n")
        dbpass_count += 1
        buffer = ""
        print(f"\n[ROBUST-SENT DB PASS ({dbpass_count}): ******]")
        time.sleep(2)
        continue

    # 11. FQDN / DNS Name
    if (
        not sent_fqdn
        and (
            "administration server ip address or fqdn" in lower_buf
            or "dns-name or static ip-address" in lower_buf
        )
        and "iam" not in lower_buf
        and ("]:" in lower_buf or lower_buf.strip().endswith(":"))
    ):
        shell.send("kscserver.tail8b9ae.ts.net\n")
        sent_fqdn = True
        buffer = ""
        print("\n[ROBUST-SENT FQDN: kscserver.tail8b9ae.ts.net]")
        time.sleep(1.5)
        continue

    # 11.5. IAM FQDN / DNS Name
    if (
        not sent_iam_fqdn
        and "iam server dns-name" in lower_buf
        and ("]:" in lower_buf or lower_buf.strip().endswith(":"))
    ):
        shell.send("kscserver.tail8b9ae.ts.net\n")
        sent_iam_fqdn = True
        buffer = ""
        print("\n[ROBUST-SENT IAM FQDN: kscserver.tail8b9ae.ts.net]")
        time.sleep(1.5)
        continue

    # 12. Run As service account (Administration Server)
    if (
        not sent_runas
        and (
            "service will run" in lower_buf
            or "account name to start the administration server" in lower_buf
        )
        and ("]:" in lower_buf or lower_buf.strip().endswith(":"))
    ):
        shell.send("ksc\n")
        sent_runas = True
        buffer = ""
        print("\n[ROBUST-SENT RUN AS (ADMIN): ksc]")
        time.sleep(1.5)
        continue

    # 12.5. Run As service account (Other Services)
    if (
        not sent_runas_others
        and "account name to start other services" in lower_buf
        and ("]:" in lower_buf or lower_buf.strip().endswith(":"))
    ):
        shell.send("ksc\n")
        sent_runas_others = True
        buffer = ""
        print("\n[ROBUST-SENT RUN AS (OTHERS): ksc]")
        time.sleep(1.5)
        continue

    # 12.7. Run As service account (KLIAM)
    if (
        not sent_runas_kliam
        and "account name to start kliam service" in lower_buf
        and ("]:" in lower_buf or lower_buf.strip().endswith(":"))
    ):
        shell.send("ksc\n")
        sent_runas_kliam = True
        buffer = ""
        print("\n[ROBUST-SENT RUN AS (KLIAM): ksc]")
        time.sleep(1.5)
        continue

    # 13. Security Group
    if (
        not sent_group
        and (
            "administrators group name" in lower_buf
            or "security group name for services" in lower_buf
        )
        and ("]:" in lower_buf or lower_buf.strip().endswith(":"))
    ):
        shell.send("kladmins\n")
        sent_group = True
        buffer = ""
        print("\n[ROBUST-SENT ADMIN GROUP: kladmins]")
        time.sleep(1.5)
        continue

    # 14. KSC Admin User Name
    if (
        not sent_admin_user
        and (
            "name of the administrator account" in lower_buf
            or "enter the user name" in lower_buf
        )
        and ("]:" in lower_buf or lower_buf.strip().endswith(":"))
    ):
        shell.send("kscadmin\n")
        sent_admin_user = True
        buffer = ""
        print("\n[ROBUST-SENT KSC ADMIN USER: kscadmin]")
        time.sleep(1.5)
        continue

    # 15. KSC Admin Password
    if (
        not sent_admin_pass
        and sent_admin_user
        and "password" in lower_buf
        and "confirm" not in lower_buf
        and "repeat" not in lower_buf
        and buffer.strip().endswith(":")
    ):
        shell.send("Ksc@2026\n")
        sent_admin_pass = True
        buffer = ""
        print("\n[ROBUST-SENT KSC ADMIN PASS: ******]")
        time.sleep(2)
        continue

    # 16. Confirm KSC Admin Password
    if (
        not sent_admin_pass_confirm
        and sent_admin_pass
        and ("confirm" in lower_buf or "repeat" in lower_buf)
        and "password" in lower_buf
        and buffer.strip().endswith(":")
    ):
        shell.send("Ksc@2026\n")
        sent_admin_pass_confirm = True
        buffer = ""
        print("\n[ROBUST-SENT CONFIRM PASS: ******]")
        time.sleep(2)
        continue

    # 17. Generic Default Prompt Handler
    if "]:" in buffer:
        match = re.search(r"([^\[\n]+)\s*\[[^\]\n]+\]:\s*$", buffer)
        if match:
            prompt_name = match.group(1).strip().lower()
            if prompt_name not in answered_generic_prompts:
                shell.send("\n")
                answered_generic_prompts.add(prompt_name)
                buffer = ""
                print(f"\n[ROBUST-SENT DEFAULT (NEWLINE) for: {prompt_name}]")
                time.sleep(1.5)
                continue

    # Exit check
    if (
        "completed successfully" in lower_buf
        or "concluída com êxito" in lower_buf
        or "concluída com sucesso" in lower_buf
    ):
        print("\nWizard completed successfully.")
        break

    if "error" in lower_buf and (
        "failed" in lower_buf or "falhou" in lower_buf or "abort" in lower_buf
    ):
        print("\nWizard encountered an error:")
        print(buffer)
        break

    # If the process returned to bash prompt
    if "[root@kscserver" in buffer and time.time() - last_action_time > 5:
        print("\nReturned to prompt. Finished.")
        break

    time.sleep(0.05)

log_file.close()
client.close()
