import os
import re

scratch_dir = r"c:\Antigravity\ksc-deployment-runbook\scratch"
didactic_dir = r"c:\Antigravity\ksc-deployment-runbook\automation\archive\didactic-2026-05"

# 1. Obter todos os arquivos em didactic e extrair suas bases (ex: 00_debug_env.py -> debug_env.py)
didactic_files = os.listdir(didactic_dir)
didactic_bases = {}
max_num = -1

for filename in didactic_files:
    match = re.match(r"^(\d+)_(.+)$", filename)
    if match:
        num = int(match.group(1))
        base = match.group(2)
        didactic_bases[base] = filename
        if num > max_num:
            max_num = num

print(f"Maior número sequencial encontrado em didactic: {max_num}")
next_num = max_num + 1

# 2. Listar arquivos em scratch
scratch_files = os.listdir(scratch_dir)
copied_count = 0

for filename in sorted(scratch_files):
    if filename == "copy_scratch_to_didactic.py":
        continue

    # Se o arquivo já existe no didactic (com ou sem prefixo numérico), nós pulamos
    if filename in didactic_bases:
        print(f"[-] Já arquivado: {filename} (como {didactic_bases[filename]})")
        continue

    scratch_path = os.path.join(scratch_dir, filename)
    if os.path.isdir(scratch_path):
        continue

    # Ler o conteúdo e higienizar senhas
    with open(scratch_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    # Higienização de senhas (governança DevSecOps)
    sanitized_content = content
    sanitized_content = sanitized_content.replace("p1WuCxrARN9WR0U0Meq4xmi*QUsI^#aZ", "[REDACTED_SSH_PASS]")
    sanitized_content = sanitized_content.replace("R6whXi4joT&OUj6#", "[REDACTED_DB_PASS]")
    sanitized_content = sanitized_content.replace("Porto@2024!", "[REDACTED_ADMIN_PASS]")
    sanitized_content = sanitized_content.replace("r8hk@bCo^53bNbDt", "[REDACTED_KSC_ADMIN2_PASS]")
    sanitized_content = sanitized_content.replace("Ksc@2026", "[REDACTED_KSC_ADMIN_PASS]")

    # Escrever no didactic
    new_filename = f"{next_num}_{filename}"
    dest_path = os.path.join(didactic_dir, new_filename)

    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(sanitized_content)

    print(f"[+] Arquivando: {filename} -> {new_filename} (Segredos Higienizados)")
    next_num += 1
    copied_count += 1

print(f"\nTotal de arquivos arquivados com sucesso: {copied_count}")
