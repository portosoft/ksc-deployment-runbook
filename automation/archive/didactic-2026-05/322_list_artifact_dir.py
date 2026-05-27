import os


def main():
    path = r"C:\Users\FábioMendes\.gemini\antigravity-ide\brain\d7b91e0f-3cb7-4c6e-9a3c-01f5eeac5a7e"
    print("--- Artifact Directory Files ---")
    if not os.path.exists(path):
        print(f"Path does not exist: {path}")
        return
    for f in os.listdir(path):
        full_p = os.path.join(path, f)
        if os.path.isfile(full_p):
            print(f"File: {f} | Size: {os.path.getsize(full_p)} bytes")
        else:
            print(f"Dir: {f}")


if __name__ == "__main__":
    main()
