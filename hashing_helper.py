from pathlib import Path
import hashlib

# from https://stackoverflow.com/questions/22058048/hashing-a-file-in-python
# BUF_SIZE is totally arbitrary, change for your app!
BUF_SIZE = 64 * 1024  # lets read stuff in 64kb chunks!



def get_md5_and_sha256(filepath: Path) -> list[str]:
    md5 = hashlib.md5()
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
            sha256.update(data)
    return [md5.hexdigest(), sha256.hexdigest()]
