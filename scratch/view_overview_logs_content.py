import os
import json

def main():
    log_path = r"C:\Users\FábioMendes\.gemini\antigravity\brain\587fdae5-cebb-4fbc-817c-71812dc64c20\.system_generated\logs\overview.txt"
    if not os.path.exists(log_path):
        print(f"Log path does not exist: {log_path}")
        return

    print("Parsing log file...")
    with open(log_path, "r", encoding="utf-8", errors="replace") as f:
        for line_num, line in enumerate(f, 1):
            try:
                data = json.loads(line)
                # Check message or details or content field
                content = ""
                if "content" in data:
                    content = str(data["content"])
                elif "message" in data:
                    content = str(data["message"])
                elif "CommandLine" in data:
                    content = str(data["CommandLine"])
                elif "Task" in data:
                    content = str(data["Task"])

                if any(w in content.lower() for w in ["mfa", "totp", "login", "credential"]):
                    # Strip long fields
                    if len(content) > 500:
                        content = content[:500] + "... [TRUNCATED]"
                    print(f"--- Line {line_num} | Source: {data.get('source')} | Type: {data.get('type')} ---")
                    print(content)
                    print()
            except Exception as e:
                pass

if __name__ == "__main__":
    main()
