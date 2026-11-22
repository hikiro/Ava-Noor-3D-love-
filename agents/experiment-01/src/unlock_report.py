#!/usr/bin/env python3
"""User-authorized manual unlock only; do not call until user explicitly requests."""
import argparse,json,pathlib,sys
from cryptography.hazmat.primitives import serialization,padding,hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
ap=argparse.ArgumentParser();ap.add_argument('--private-key',required=True);ap.add_argument('--sealed-report',required=True);a=ap.parse_args()
key=serialization.load_pem_private_key(pathlib.Path(a.private_key).read_bytes(),password=None)
r=json.loads(pathlib.Path(a.sealed_report).read_text())
aes=key.decrypt(bytes.fromhex(r['wrapped_key']),padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
plain=AESGCM(aes).decrypt(bytes.fromhex(r['nonce']),bytes.fromhex(r['ciphertext']),b'VV_EXP01_ROLE_REVIEW')
print(plain.decode())
