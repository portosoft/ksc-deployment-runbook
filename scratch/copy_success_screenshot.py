import os
import shutil

def main():
    temp_dir = r"C:\Users\FábioMendes\.gemini\antigravity\brain\587fdae5-cebb-4fbc-817c-71812dc64c20\.tempmediaStorage"
    dest_dir = r"C:\Users\FábioMendes\.gemini\antigravity\brain\587fdae5-cebb-4fbc-817c-71812dc64c20"

    if not os.path.exists(temp_dir):
        print(f"Source dir does not exist: {temp_dir}")
        return

    # Find the most recent .png files
    files = [f for f in os.listdir(temp_dir) if f.endswith(".png")]
    files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(temp_dir, x)))

    if not files:
        print("No screenshots found.")
        return

    # Copy the last 3 screenshots
    print("Recent screenshots:")
    for f in files[-5:]:
        src = os.path.join(temp_dir, f)
        print(f"- {f} (mtime: {os.path.getmtime(src)}, size: {os.path.getsize(src)} bytes)")

    # Copy the last one as ksc_gui_login_success.png
    latest = files[-1]
    shutil.copy2(os.path.join(temp_dir, latest), os.path.join(dest_dir, "ksc_gui_login_success.png"))
    print(f"Copied {latest} to artifacts/ksc_gui_login_success.png")

if __name__ == "__main__":
    main()
