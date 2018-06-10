class MergingUsingLatest:
    def __init__(self, decrypted_storage, encrypted_storage):
        self.encrypted_storage = encrypted_storage
        self.decrypted_storage = decrypted_storage

    def merge(self, file_name):
        encrypted_file = self.encrypted_storage.folder / file_name
        decrypted_file = self.decrypted_storage.folder / file_name

        if not encrypted_file.exists():
            self.decrypted_storage.copy(file_name)

        if not decrypted_file.exists():
            self.encrypted_storage.copy(file_name)

        if decrypted_file.stat().st_mtime >= encrypted_file.stat().st_mtime:
            self.decrypted_storage.copy(file_name)
        else:
            self.encrypted_storage.copy(file_name)
