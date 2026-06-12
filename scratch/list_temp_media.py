import os

def main():
    path = r"C:\Users\FábioMendes\.gemini\antigravity\brain\587fdae5-cebb-4fbc-817c-71812dc64c20\.tempmediaStorage"
    if not os.path.exists(path):
        print(f"Path does not exist: {path}")
        return

    files = sorted(os.listdir(path), key=lambda x: os.path.getmtime(os.path.join(path, x)))
    print("--- Files in tempmediaStorage ---")
    for f in files:
        full_p = os.path.join(path, f)
        size = os.path.getsize(full_p)
        print(f"{f} | Size: {size} bytes | Mtime: {os.path.getmtime(full_p)}")

if __name__ == "__main__":
    main()
