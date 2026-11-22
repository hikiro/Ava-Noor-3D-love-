# Villa Verse Sealed Audit Agent — operation rules

- **Worker:** one-shot unprivileged process `agent/audit_worker.py`, operating only on fixed `input/` snapshots.
- **Owner:** the producer-led studio's `independent-auditor` role; this is a deterministic worker, NOT a separate AI model.
- **Public boundary:** read only `public/status.json` and archival checksums before user unlocks.
- **Private boundary:** never decrypt or inspect `sealed/*.sealed.json` until the user explicitly requests `unlock`.
- **Release policy:** no mechanical benchmark grants final artistic approval. The worker must mark missing Godot/visual review BLOCKED.
- **Future independent reasoning:** connect a genuinely separate model runtime owned by user; no model clone, hidden neural reasoning, or autonomous multi-agent operation has been created here.
- **Persistence:** include the sealed report, the public status, immutable inputs and role charter with every handover. Keep the decryption key outside the ZIP.