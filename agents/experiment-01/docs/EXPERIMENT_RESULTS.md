# Experiment 01 — Observed run

## Hypothesis
A Producer and an Auditor can receive a common evidence packet in two separate execution contexts, maintain private context files, disagree, and route decisions through public messages without cross-reading private records.

## Experiment conditions
- Each was a separate OS subprocess under a separate unprivileged user.
- Common evidence came from v2.1 artifacts and source-validation records.
- Decision backend was `policy`, an **explicit deterministic test fixture**. No language model was present.
- Producer's assigned fixture goal: make a case for progressing to internal candidate stage based on technical checks.
- Auditor's fixture goal: block public release when qualitative contact and engine verification are unresolved.

## Actual public decisions
- Producer: `PROPOSE_INTERNAL_RELEASE_CANDIDATE`.
- Auditor: `BLOCK_PUBLIC_RELEASE`.
- Feedback: `BLOCKED` for publication, with tasks routed to Art Director + Animator (real grasp), Technical Director (Godot playback), and Character Artist (lip topology).
- This is a designed policy disagreement, **not** evidence of independently evolved AI judgments.

## Tests and what they establish
- 20/20 infrastructure/permissions checks passed. The process identities were unable to read each other's private memories, outputs, or private prompts.
- Two concurrent subprocesses exited successfully and wrote independent encrypted private snapshots.
- Model transport adapter passed two-request fake-server test. It sent independent role prompts, individual memory and visual panels. No model was connected.
- The prior QA-01 encrypted report was checked for ciphertext-hash integrity only, without decrypting.

## Not demonstrated
- Genuine LLM inference by either worker: **0 actual model instances executed**.
- Autonomous long-term operation without a powered host/orchestrator: **not demonstrated**.
- AI self-training or model weight adaptation: **not implemented**.
- Artist-level independent critique of original video: **not demonstrated**.
- Full container isolation / admin-inaccessible sealed state: **not demonstrated**.
- Actual Godot player import of the Villa Verse scene: **not demonstrated**.

## Next objective test
On a host with a **local Ollama instance and a capable model already installed**, launch both roles using `--backend ollama`. Verify nonidentical model-generated recommendations and real image-specific references. Run two tasks separated by a memory update, then blind the Auditor to the Producer's private context and test whether its verdict changes only because of its own new evidence. No paid external API is required for that route.
