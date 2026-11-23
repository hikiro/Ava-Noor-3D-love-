#!/usr/bin/env python3
"""Reassemble Ava/Noor v2.1 GLBs from immutable GitHub-tracked binary parts."""
from pathlib import Path
import hashlib, json, sys

ROOT = Path(__file__).resolve().parent.parent
manifest = json.loads((ROOT / "models/v2.1/PARTS_MANIFEST.json").read_text(encoding="utf-8"))
failed = []
for model in manifest["models"]:
    target = ROOT / model["target_path"]
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("wb") as output:
        for part in sorted(model["segments"], key=lambda x: x["index"]):
            source = ROOT / part["path"]
            if not source.is_file():
                failed.append("Missing part: " + str(source))
                break
            data = source.read_bytes()
            if len(data) != part["size"] or hashlib.sha256(data).hexdigest() != part["sha256"]:
                failed.append("Invalid part: " + str(source))
                break
            output.write(data)
    if failed:
        target.unlink(missing_ok=True)
        continue
    data = target.read_bytes()
    if len(data) != model["size"] or hashlib.sha256(data).hexdigest() != model["sha256"]:
        failed.append("Hash mismatch: " + str(target))
        target.unlink(missing_ok=True)
    else:
        twin = ROOT / model["source_path"]
        twin.parent.mkdir(parents=True, exist_ok=True)
        twin.write_bytes(data)
        print("Reassembled and SHA-256 verified:", target, len(data), "bytes")
if failed:
    print("\n".join(failed), file=sys.stderr)
    sys.exit(1)
