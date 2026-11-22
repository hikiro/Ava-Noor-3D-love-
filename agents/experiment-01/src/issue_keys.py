#!/usr/bin/env python3
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
root=Path(__file__).resolve().parents[1]
assert not (root/'keys/exp01_public.pem').exists() and not Path('/mnt/data/VillaVerse_Experiment_01_UNLOCK_PRIVATE_KEY.pem').exists(), 'Refusing to overwrite existing unlock keys.'
key=rsa.generate_private_key(public_exponent=65537,key_size=3072)
(root/'keys/exp01_public.pem').write_bytes(key.public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo))
Path('/mnt/data/VillaVerse_Experiment_01_UNLOCK_PRIVATE_KEY.pem').write_bytes(key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))
print('Key pair generated; private unlock key is separate from experiment directory.')
