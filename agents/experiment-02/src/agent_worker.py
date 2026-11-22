#!/usr/bin/env python3
"""One worker process per role, with no access to opposing role's context by design.
Host OS permissions must enforce isolation: this script alone is NOT a security boundary.
"""
from __future__ import annotations
import argparse, base64, hashlib, json, os
from pathlib import Path
import sys
import urllib.parse, urllib.request
from protocol import ROOT, load_json, dump_json, hash_file, check_evidence, seal_report, utc_now, validate_review

ROLE_SYSTEM = {"producer": "PRODUCER_SYSTEM.md", "auditor": "AUDITOR_SYSTEM.md"}
VISUALS = {"producer": ["SIX_POSE_V21_INSPECTION.png"], "auditor": ["SIX_POSE_V21_INSPECTION.png", "CONTACT_V21_DETAIL.png", "MOUTH_BEFORE_AFTER_v21.png"]}

def request_review(role, memory, model, endpoint, backend, timeout):
    u = urllib.parse.urlparse(endpoint)
    if u.scheme != "http" or u.hostname not in ("127.0.0.1", "localhost", "::1") or u.path != "/api/chat" or u.username or u.password:
        raise ValueError("Endpoint must be local Ollama-compatible HTTP /api/chat")
    system = (ROOT / "config" / ROLE_SYSTEM[role]).read_text(encoding="utf-8")
    evidence = load_json(ROOT / "evidence" / "v21_evidence.json")
    task = {
        "experiment": "VV-EXP02",
        "instruction": "Independently review Villa Verse v2.1 readiness, cite supplied evidence and report ONLY JSON. Do not claim to have run tools or inspected anything not supplied.",
        "evidence": evidence,
        "role_private_memory": memory["events"][-6:],
        "output_schema": {
            "verdict": "role-specific enum",
            "confidence": "number 0..1",
            "public_flags": ["UPPER_CASE_CODES"],
            "private_assessment": "brief evidence-based judgment, not internal hidden reasoning",
            "next_task": "one concrete next task",
            "learning_proposals": [{"rule": "new, reusable rule grounded in observed evidence", "supporting_evidence": "source ID", "status": "PENDING_VALIDATION"}]
        }
    }
    user = {"role": "user", "content": json.dumps(task, ensure_ascii=False), "images": [base64.b64encode((ROOT / "evidence/visuals" / name).read_bytes()).decode() for name in VISUALS[role]]}
    request = {"model": model, "stream": False, "format": "json", "options": {"temperature": 0.2, "num_ctx": 8192}, "keep_alive": "0s", "messages": [{"role": "system", "content": system}, user]}
    raw = json.dumps(request).encode()
    with urllib.request.urlopen(urllib.request.Request(endpoint, data=raw, headers={"Content-Type": "application/json"}), timeout=timeout) as response:
        data = json.loads(response.read())
    if not isinstance(data.get("message", {}).get("content"), str) or data.get("done") is not True:
        raise ValueError("Incomplete Ollama-compatible response")
    if data.get("model") != model:
        raise ValueError("Model response identity mismatch")
    result = validate_review(role, json.loads(data["message"]["content"]))
    telemetry = {"declared_model": data.get("model"), "eval_count": data.get("eval_count"), "prompt_eval_count": data.get("prompt_eval_count"), "total_duration_ns": data.get("total_duration"), "transport_backend": backend}
    return result, telemetry

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--role", choices=list(ROLE_SYSTEM), required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--backend", choices=["ollama", "mock"], required=True)
    ap.add_argument("--endpoint", default="http://127.0.0.1:11434/api/chat")
    ap.add_argument("--state-dir", required=True)
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--public-key", required=True)
    ap.add_argument("--timeout", type=int, default=360)
    args = ap.parse_args()
    if len(args.run_id) > 100 or not args.run_id.replace("-", "").replace("_", "").isalnum():
        raise ValueError("Invalid run id")
    if check_evidence():
        raise ValueError("Evidence hash mismatch")
    state_dir = Path(args.state_dir)
    run_dir = Path(args.run_dir)
    state_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    memory_path = state_dir / "memory.json"
    memory = load_json(memory_path) if memory_path.exists() else {"role": args.role, "version": 1, "events": []}
    if memory.get("role") != args.role:
        raise ValueError("Role memory mismatch")
    try:
        review, telemetry = request_review(args.role, memory, args.model, args.endpoint, args.backend, args.timeout)
    except Exception as e:
        # No model output or private data is emitted to stdout/stderr in the error path.
        dump_json(run_dir / "public_status.json", {"role": args.role, "run_id": args.run_id, "status": "ERROR", "backend": args.backend, "model_inference_verified": False, "error_type": type(e).__name__, "private_review": "not_published"})
        print(json.dumps({"role": args.role, "status": "ERROR", "error_type": type(e).__name__}))
        return 2
    event = {"event_id": "E" + str(len(memory["events"]) + 1).zfill(4), "timestamp": utc_now(), "evidence_digest": hash_file(ROOT / "evidence/v21_evidence.json"), "review_verdict": review["verdict"], "proposed_rules": review["learning_proposals"], "status": "OBSERVED_IN_MODEL_RUN" if args.backend == "ollama" else "SIMULATED_FIXTURE"}
    memory["events"].append(event)
    memory["version"] += 1
    # Memory remains private to its role. For true separation use OS user accounts/VMs.
    dump_json(memory_path, memory)
    try:
        os.chmod(memory_path, 0o600)
    except OSError:
        pass
    report = {"role": args.role, "run_id": args.run_id, "review": review, "telemetry": telemetry, "private_memory_snapshot": memory}
    sealed = seal_report(Path(args.public_key), report, args.role, args.run_id)
    dump_json(run_dir / "sealed_review.json", sealed)
    public = {"role": args.role, "run_id": args.run_id, "verdict": review["verdict"], "confidence": review["confidence"], "public_flags": review["public_flags"], "model": args.model, "backend": args.backend, "model_inference_verified": args.backend == "ollama", "private_review": "SEALED_UNOPENED", "model_api_attestation": "not_cryptographically_attested", "memory_version": memory["version"], "sealed_sha256": hash_file(run_dir / "sealed_review.json")}
    dump_json(run_dir / "public_status.json", public)
    print(json.dumps({"role": args.role, "status": "OK", "verdict": public["verdict"], "backend": args.backend, "memory_version": public["memory_version"]}))
    return 0

if __name__ == "__main__":
    sys.exit(main())
