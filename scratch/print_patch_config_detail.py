def main():
    with open("scratch/setup.js", "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Print a window around index 1133500 to 1135700
    start = 1133500
    end = 1135700
    print(content[start:end])

if __name__ == "__main__":
    main()
