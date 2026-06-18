def patch_nats_js(client, filepath):
    # Read the file
    sftp = client.open_sftp()
    with sftp.file(filepath, "r") as f:
        content = f.read().decode("utf-8", errors="ignore")

    # Replace the Cyrillic 'a' (\u0430) with standard 'a'
    # The line is: Start create а new connection
    new_content = content.replace("\u0430 new", "a new")

    # Also, let's fix any other potential Cyrillic characters in logs just in case
    cyrillic_to_latin = {
        "\u0430": "a", "\u0441": "c", "\u0435": "e", "\u043e": "o",
        "\u0440": "p", "\u0445": "x", "\u0443": "y", "\u0410": "A",
        "\u0421": "C", "\u0415": "E", "\u041e": "O", "\u0420": "P",
        "\u0425": "X", "\u0423": "Y", "\u041c": "M", "\u041d": "H",
        "\u0422": "T", "\u0412": "B", "\u041a": "K",
    }
    for cyr, lat in cyrillic_to_latin.items():
        new_content = new_content.replace(cyr, lat)

    if content == new_content:
        print("No change detected. Trying byte-level replacement...")
        # Maybe it's encoded differently?
        # \u0430 in UTF-8 is \xd0\xb0
        new_content = content.replace("\xd0\xb0 new", "a new")

        # Byte-level replacement for all homoglyphs
        for cyr, lat in cyrillic_to_latin.items():
            # Get the string representation of the utf-8 bytes (e.g. "\xd0\xb0" for "\u0430")
            cyr_bytes_str = cyr.encode("utf-8").decode("latin1", errors="ignore")
            new_content = new_content.replace(cyr_bytes_str, lat)

    with sftp.file("/tmp/connection-creator.js", "w") as f:
        f.write(new_content)
