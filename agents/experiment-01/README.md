# Villa Verse — Multi-Agent Experiment 01 (Producer vs Auditor)

## Truthful result
This package **does not contain a successfully launched pair of independent AI language-model agents**. The environment has no Ollama runtime or accessible language-model endpoint, and no model API credentials are configured. Two separate *OS subprocesses* were executed successfully under distinct Linux identities, using intentionally conflicting deterministic policy fixtures. This proves the agent-envelope and isolation mechanisms; it does **not** prove independent AI reasoning, creativity, visual review, or self-evolution.

**Observed:** Producer proposed an **internal release candidate** based on technical evidence; Auditor **blocked public release** based on unresolved visual and Godot verification issues. The router left publication blocked. Both verdicts were fixture outputs, not model-generated responses.

## Measured source evidence
- Source: original Villa Verse v2.1 files under `/mnt/data/VillaVerse_Models_v2_1`.
- Structural checks: 43/43 passed (reported by v2.1 validator, cross-checked by this experiment).
- Prior opposing-hand collision sweep: 125/125 frames, no intersections recorded.
- Sampled nearest-hand-vertex distance at frames 75–100: approximately 12.34 mm (not proof of believable contact).
- Source motion MP4: 125 frames, 24 FPS, 540×960, verified using OpenCV.
- Godot native playback: not verified.
- The visual defects in the evidence file are **pre-existing documented issues**, not fresh independent artistic judgments by a second LLM.

## Architecture

```
                       [owner]
                          |
                    [evidence JSON + images]
                          |
             +------------+------------+
             |                         |
     [producer process]        [auditor process]
      private UID/memory         private UID/memory
      private role prompt        private role prompt
             |                         |
        [sealed report]            [sealed report]
             |                         |
             +---- public verdicts ----+
                          |
                 [feedback router]
                 BLOCK or ADVANCE
                          |
                public routed tasks
```

- Workers are launched as separate OS processes, and on the tested Linux host use distinct unprivileged UIDs (`vvexp01p`, `vvexp01a`).
- Each writes to its own `0700` private memory and encrypted output; neither UID can read the other UID's private records or system prompt.
- Each can read the same immutable evidence packet; the auditor can receive visual references for local vision-model inference.
- The feedback router reads only public summaries.
- Private review and memory snapshots are encrypted with AES-256-GCM; the data encryption key is wrapped with RSA-OAEP-SHA256. The user-controlled unlock key is **not included** in this ZIP.
- The old QA-01 black box was not decrypted or altered.

### Security limits
These are operating-system permission boundaries **between the two assigned agent UIDs**, not protection against this environment's root administrator. There is **no container or network namespace isolation**. A malicious process may still read world-readable files elsewhere in the host. In production, use separate containers/VMs, least-privilege mounts, strict network policies, and keep unlock keys outside the orchestrator. Source-visible fixture policies do not constitute secret model reasoning.

## Backends
- `--backend policy` — **deterministic fixture** used in the actual run; *not AI*.
- `--backend ollama` — real, local model adapter via `http://127.0.0.1:11434/api/chat`. Currently **not executed against a model**. Requires a compatible local vision model, such as a pulled Ollama image-capable model. The adapter transmits base64-encoded reference panels and each worker's separate memory. This backend produces separate model requests, not separate model weights or fine-tuning.
- The HTTP adapter was exercised with a **synthetic local response server**; transport succeeded, but this is not a live LLM test.

## Reproducible tests run here
1. Distinct OS user permissions and private memory/prompt isolation.
2. Evidence immutability under each worker identity.
3. Opposed public recommendations and release veto.
4. Structured feedback routing without reading private reports.
5. Synthetic encryption/decryption test. Actual encrypted review text remains unopened.
6. Two-worker concurrent launcher and distinct API transport requests against a mock server.
7. v2.1 checksums and video metadata.

See `docs/EXPERIMENT_RESULTS.md`, `outputs/feedback/infrastructure_tests.json`, and `outputs/feedback/transport_fixture_test.json`.

## Files
- `evidence/` — checksummed v2.1 evidence, the actual MP4, both rigged GLBs, original upstream validation records and three actual storyboard/animation PNGs.
- `config/` — individual agent prompts and routing rules.
- `src/` — real worker, local Ollama adapter, fixture backend, producer/auditor orchestrator, feedback router, unlock tool.
- `outputs/producer` and `outputs/auditor` — **encrypted reports and public statuses only**. Private plaintext memory files are deliberately excluded from the portable ZIP.
- `outputs/feedback` — public verdicts, work assignments and tests.
- `keys/exp01_public.pem` — public encryption key (no private key).
- `docs/` — protocol, limitations and handover.

No ongoing task is running after this chat response. The code can be launched in a later model-enabled runtime, but this chat cannot run a persistent autonomous service after completion.