import hashlib

def compute_sha256(file):
    data = file.read()
    sha256_hash = hashlib.sha256(data).hexdigest()
    return sha256_hash
