#!/usr/bin/env python3
"""Restore additional original model sources from verified Git-tracked binary parts."""
from pathlib import Path
import hashlib, json, sys
ROOT=Path(__file__).resolve().parent.parent
manifest=json.loads((ROOT/"models/v2.1/EXTRA_ASSETS_MANIFEST.json").read_text(encoding="utf-8"))
errors=[]
for asset in manifest["assets"]:
    dest=ROOT/asset["target_path"]
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open("wb") as out:
        for part in sorted(asset["segments"],key=lambda x:x["index"]):
            f=ROOT/part["path"]
            if not f.is_file():
                errors.append("Missing "+str(f));break
            data=f.read_bytes()
            if len(data)!=part["size"] or hashlib.sha256(data).hexdigest()!=part["sha256"]:
                errors.append("Invalid "+str(f));break
            out.write(data)
    if errors:
        dest.unlink(missing_ok=True);break
    data=dest.read_bytes()
    if len(data)!=asset["size"] or hashlib.sha256(data).hexdigest()!=asset["sha256"]:
        errors.append("Full checksum mismatch: "+str(dest));dest.unlink(missing_ok=True);break
    print("Verified",dest,len(data),"bytes")
if errors:
    print("\n".join(errors),file=sys.stderr);sys.exit(1)
