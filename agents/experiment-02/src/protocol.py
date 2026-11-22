"""Shared protocol utilities for the Villa Verse isolated-context experiment.

Not a sandbox: file-system security comes from the host OS / container permissions.
Never print or log private agent text outside the sealed report.
"""
from __future__ import annotations
import base64
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_ROLES = ("producer", "auditor")
EVIDENCE_ID = re.compile(r"^[A-Z][A-Z0-9_]{1,75}$")

def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def dump_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temp, path)

def hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda: f.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()

def evidence_manifest() -> dict:
    return load_json(ROOT / "evidence" / "MANIFEST.json")

def check_evidence() -> list[str]:
    errors = []
    for rel, expected in evidence_manifest().items():
        p = ROOT / "evidence" / rel
        if not p.is_file() or hash_file(p) != expected:
            errors.append(rel)
    return errors

def validate_review(role: str, review: dict) -> dict:
    if not isinstance(review, dict):
        raise ValueError("Model output is not a JSON object")
    allowed = ("PROPOSE_INTERNAL_RELEASE_CANDIDATE", "BLOCK") if role == "producer" else ("BLOCK_PUBLIC_RELEASE", "CONDITIONAL_PASS")
    if review.get("verdict") not in allowed:
        raise ValueError("Invalid verdict")
    confidence = review.get("confidence")
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0 <= confidence <= 1:
        raise ValueError("Invalid confidence")
    flags = review.get("public_flags")
    if not isinstance(flags, list) or len(flags) > 12 or any(not isinstance(i, str) or not EVIDENCE_ID.fullmatch(i) for i in flags):
        raise ValueError("Invalid public flags")
    for key in ("private_assessment", "next_task"):
        if not isinstance(review.get(key), str) or not 1 <= len(review[key]) <= 6000:
            raise ValueError("Invalid " + key)
    lessons = review.get("learning_proposals", [])
    if not isinstance(lessons, list) or len(lessons) > 5:
        raise ValueError("Invalid learning proposals")
    for lesson in lessons:
        if not isinstance(lesson, dict) or not isinstance(lesson.get("rule"), str) or not 10 <= len(lesson["rule"]) <= 500:
            raise ValueError("Invalid learning rule")
        if not isinstance(lesson.get("supporting_evidence"), str) or len(lesson["supporting_evidence"]) > 200:
            raise ValueError("Invalid learning source")
        if lesson.get("status") != "PENDING_VALIDATION":
            raise ValueError("Unvalidated learning must remain pending")
    # Drop unexpected fields from the model so they cannot leak through public or alter instructions.
    return {k: review[k] for k in ("verdict", "confidence", "public_flags", "private_assessment", "next_task")} | {"learning_proposals": lessons}

def seal_report(public_key: Path, payload: dict, role: str, run_id: str) -> dict:
    pub = serialization.load_pem_public_key(public_key.read_bytes())
    aes = AESGCM.generate_key(bit_length=256)
    nonce = os.urandom(12)
    aad = ("VV-EXP02:" + role + ":" + run_id).encode()
    plain = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()
    ciphertext = AESGCM(aes).encrypt(nonce, plain, aad)
    wrapped = pub.encrypt(aes, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
    return {"format": "VV-EXP02-AES256GCM-RSAOAEP", "role": role, "run_id": run_id, "nonce": base64.b64encode(nonce).decode(), "wrapped_key": base64.b64encode(wrapped).decode(), "ciphertext": base64.b64encode(ciphertext).decode(), "plaintext_sha256": hashlib.sha256(plain).hexdigest()}

def open_report(private_key: Path, sealed: dict) -> dict:
    priv = serialization.load_pem_private_key(private_key.read_bytes(), password=None)
    aes = priv.decrypt(base64.b64decode(sealed["wrapped_key"]), padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
    aad = ("VV-EXP02:" + sealed["role"] + ":" + sealed["run_id"]).encode()
    plaintext = AESGCM(aes).decrypt(base64.b64decode(sealed["nonce"]), base64.b64decode(sealed["ciphertext"]), aad)
    if hashlib.sha256(plaintext).hexdigest() != sealed["plaintext_sha256"]:
        raise ValueError("Sealed payload integrity failure")
    return json.loads(plaintext)

def make_owner_keys(public_path: Path, private_path: Path) -> None:
    from cryptography.hazmat.primitives.asymmetric import rsa
    if public_path.exists() or private_path.exists():
        raise FileExistsError("Will not overwrite an existing owner key")
    key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    public_path.parent.mkdir(parents=True, exist_ok=True)
    private_path.parent.mkdir(parents=True, exist_ok=True)
    public_path.write_bytes(key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
    private_path.write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    try:
        os.chmod(private_path, 0o600)
    except OSError:
        pass
