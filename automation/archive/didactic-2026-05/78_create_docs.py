import os

docs = [
    "01-pre-requisitos.md", "02-configuracao-env.md", "03-auditoria-previa.md", 
    "04-postgres-setup.md", "05-selinux-hardening.md", "06-ksc-server-install.md", 
    "07-web-console.md", "08-pos-install-hardening.md", "09-auditoria-final.md", 
    "10-relatorios.md", "11-troubleshooting.md", "12-handover.md"
]

os.makedirs('docs', exist_ok=True)

for d in docs:
    title = d.replace(".md", "").replace("-", " ").title()
    content = f"# {title}\n\nEste documento detalha o passo '{title}' da jornada do operador.\n"
    with open(f"docs/{d}", "w", encoding="utf-8") as f:
        f.write(content)

print("Documentos criados.")
