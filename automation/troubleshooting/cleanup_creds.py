import os
import re

def cleanup_scripts():
    path = r'automation\troubleshooting'
    if not os.path.exists(path):
        print(f"Path {path} does not exist.")
        return

    files = [f for f in os.listdir(path) if f.endswith('.py')]
    
    # Creds to replace
    patterns = {
        r'REDACTED_SSH_PASS': 'os.getenv("KSC_PASS")',
        r'192\.168\.100\.5': 'os.getenv("KSC_HOST")',
        r'["\']***REMOVED***["\']': 'os.getenv("KSC_USER")'
    }

    for f in files:
        fpath = os.path.join(path, f)
        print(f"Cleaning {f}...")
        try:
            with open(fpath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            modified = False
            for pattern, replacement in patterns.items():
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    modified = True
            
            if modified:
                if 'import os' not in content:
                    content = 'import os\n' + content
                with open(fpath, 'w', encoding='utf-8') as file:
                    file.write(content)
                print(f"Done: {f}")
        except Exception as e:
            print(f"Error processing {f}: {e}")

if __name__ == "__main__":
    cleanup_scripts()
