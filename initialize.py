def synchronize(decrypted_storage, encrypted_storage, decrypted_folder, encrypted_folder):
    decripted_files = [x.name for x in decrypted_folder.iterdir() if not x.is_dir() and not str(x).startswith('.')]
    encrypted_files = [x.name for x in encrypted_folder.iterdir() if not x.is_dir() and not str(x).startswith('.')]

    for file_path in set(decripted_files).intersection(encrypted_files):
        if (decrypted_folder / file_path).stat().st_mtime >= (encrypted_folder / file_path).stat().st_mtime:
            decrypted_storage.copy(decrypted_folder / file_path)
        else:
            encrypted_storage.copy(encrypted_folder / file_path)

    for file_path in set(decripted_files).difference(encrypted_files):
        decrypted_storage.copy(decrypted_folder / file_path)

    for file_path in set(encrypted_files).difference(decripted_files):
        encrypted_storage.copy(encrypted_folder / file_path)


def init_folder(decrypted_folder, encrypted_folder):
    encrypted_folder.mkdir(parents=True, exist_ok=True)
    (decrypted_folder / '.config').mkdir(parents=True, exist_ok=True)
