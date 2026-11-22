# Villa Verse — Sealed QA black-box prototype v0.1

This is a **working isolated deterministic QA worker with encrypted reports**, **not a separate LLM**.

## Layout

- `agent/ROLE.md` — standalone audit charter, imported from production v3.0.
- `agent/audit_worker.py` — stateless one-shot independent subprocess runner.
- `config/task.json` — fixed incoming work order.
- `input/` — immutable snapshots of actual v2.1 model/video/QA evidence.
- `keys/auditor_public.pem` — encryption public key (safe to disclose).
- `sealed/` — encrypted detailed report, not opened until user's explicit unlock.
- `public/status.json` — only public worker result.
- `tools/unlock_report.py` — private-key decryption; must **not** run without explicit user instruction.
- `docs/BLACKBOX_CONTRACT.md` — precise limits of isolation / autonomy.

The private key is distributed separately as `VillaVerse_BlackBox_UNLOCK_KEY.pem`.

## Replication

`python agent/audit_worker.py` (needs cryptography, ffprobe). It uses the RSA public key; it cannot decrypt sealed output.

## Integrating a genuinely independent LLM

Replace or extend `agent/audit_worker.py` with an independent model adapter and enforce the same input/output boundary. The present worker is not a neural agent and does not autonomously continue after this response.