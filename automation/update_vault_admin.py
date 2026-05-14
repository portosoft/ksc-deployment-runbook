import sys
import os
import getpass

sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
import vault

def update_vault():
    print("KSC Security Vault Update")
    print("-------------------------")
    print("Leave blank to keep existing value (if any).\n")

    secrets = {}
    try:
        secrets = vault.decrypt_secrets()
    except Exception:
        print("Vault not found or key missing. Starting fresh.")

    fields = [
        ("KSC_HOST", "KSC Server IP"),
        ("KSC_USER", "SSH Username"),
        ("KSC_PASS", "SSH Password"),
        ("KSC_ADMIN_USER", "KSC Admin Username"),
        ("KSC_ADMIN_PASS", "KSC Admin Password"),
        ("KSC_FQDN", "KSC FQDN"),
        ("KSC_PORT", "KSC OpenAPI Port")
    ]

    for key, label in fields:
        current = secrets.get(key, "***") if key in secrets else "Not set"
        val = input(f"{label} [{current}]: ").strip()
        if val:
            secrets[key] = val
        elif key not in secrets:
            print(f"Error: {key} is required for a fresh vault.")
            return

    vault.encrypt_secrets(secrets)
    print("\nVault updated and encrypted successfully.")

if __name__ == "__main__":
    update_vault()
