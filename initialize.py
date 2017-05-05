def synchronize(merger, decrypted_storage, encrypted_storage):
    decrypted_files = set(decrypted_storage.get_file_names())
    encrypted_files = set(encrypted_storage.get_file_names())

    for file_name in encrypted_files.union(decrypted_files):
        merger.merge(file_name)


def init_folder(decrypted_folder, encrypted_folder):
    encrypted_folder.mkdir(parents=True, exist_ok=True)
    (decrypted_folder / '.config').mkdir(parents=True, exist_ok=True)
