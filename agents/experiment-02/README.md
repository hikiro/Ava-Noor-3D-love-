# Villa Verse — Multi-Agent Experiment 02

## Precise current status

**Two independent local-model requests are implemented but NOT executed here against real models.** This ChatGPT container has no Ollama service, model weights, Claude Code runtime, or independent LLM endpoint. External downloads are blocked. Separate subprocess and model-API protocol tests did run with a deliberately synthetic model server. The synthetic model's outputs are not AI reasoning or creative approval.

## Experiment design

- **Producer** and **Auditor** launch as separate Python processes, with distinct system prompts, vision inputs, and private memory directories.
- Default Windows inference: Producer `qwen3.5:4b` and Auditor `qwen3-vl:4b`, both via Ollama on localhost. Both models are *expected* from prior local usage, but not verified on the user's PC in this session.
- Execution is **sequential by default** to avoid loading both on a GTX 1060 6GB simultaneously. Separate sessions do not require parallel GPU calls.
- Agents receive checksummed **real Villa Verse v2.1** evidence, including a 125-frame MP4, rigged GLBs and real visual panels.
- Each process maintains its own versioned `private_state/<role>/memory.json`. Memory includes previous verdicts and newly proposed rules, labeled **PENDING_VALIDATION**. This is context adaptation, not model weight training.
- Private reports are encrypted with AES-256-GCM and an RSA-OAEP-wrapped data key. The owner's private key is not in the project ZIP.
- The feedback router reads only public verdict codes and cannot unlock reports. The final release is blocked when Auditor rejects or Godot remains unverified.

## Quick start on your own Windows PC (no paid API)

1. Extract `VillaVerse_MultiAgent_Experiment_02.zip`.
2. **For the strongest available privacy, generate the owner key on your own PC.** The Windows launcher generates a new public/private pair on your computer, storing the public key in the project and the private key outside it, under your Windows home directory in `VillaVerse_OwnerKeys`. Do not send that private key into this chat. No private key or pre-generated public key from this chat is required for the Windows run.
3. Ensure Python 3 and Ollama are installed and running. Confirm `ollama list` includes `qwen3.5:4b` and `qwen3-vl:4b`; if not, install models using `ollama pull qwen3.5:4b` and `ollama pull qwen3-vl:4b` (downloads use bandwidth and disk space, not a paid API).
4. In PowerShell, inside the extracted folder, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\Start_Experiment_Windows.ps1 -TestOnly
powershell -ExecutionPolicy Bypass -File .\Start_Experiment_Windows.ps1
```

The first command tests the transport with synthetic responses. The second performs **two real local-model requests**, only if Ollama and both models are available. The visible result is `run/<run-id>/public_result.json`. Each worker's `sealed_review.json` remains encrypted and the private memory is excluded from the shared ZIP.

Repeated invocations let the agents receive their own previous experience. They **do not** run autonomously after the command exits. Memory learning is append-only at the case level and new rules remain proposals; they do not automatically amend permanent policy.

## Security boundary

**Separate contexts are not the same as unbreakable black-box security.** On a single Windows account, both processes and the parent process have OS-level potential access to the same filesystem. This code does not make their directories inaccessible to an administrator or the ChatGPT model that authored the code. Strict isolation needs different Windows user identities with NTFS ACLs, containers or separate VMs, plus owner-controlled keys. An admin may still bypass host-level controls. The current ZIP is a useful functional prototype, not a high-assurance secure sandbox.

The Windows launcher generates a NEW owner key locally, outside the project, so the private key is not supplied to this chat. The code never automatically opens encrypted reports. **Do not use `src/protocol.py`'s `open_report` with the owner key unless explicitly authorized.**

## Status and reproducibility

- **13 distinct local integration tests passed**, including separate model request inputs, private role-scoped memory over two runs, 3-image auditor evidence, encrypted reports, fail-closed on malformed output, immutable evidence hashes, and no auto-approval.
- **Actual real-LLM requests run in this container:** 0. This is a hard blocker for the intended model-behavior experiment, not something the technical tests can replace.
- **Actual independent black-box agent evolution proven:** No. Persistent memory and learning proposal mechanics were tested with deterministic mock responses, not actual learning.
- **Godot engine playback:** Unverified; out of scope for this multi-agent infrastructure experiment.

### Components

`src/agent_worker.py`: model request, review validation, sealed report and role-specific memory.

`src/orchestrator.py`: run isolation, endpoint preflight, sequential worker launch and public feedback routing.

`src/protocol.py`: evidence hashes, report encryption and validation.

`tests/test_local_integration.py`: real subprocess/HTTP checks with synthetic model replies.

`evidence/`: frozen v2.1 samples, image panels, GLBs, original validation records and SHA-256 manifest.

`private_state/`: created locally during runs; **do not upload/share**.

`run/`: locally generated public results and sealed reviews; keep private records private.

`keys/owner_public.pem`: generated locally by the Windows launcher. Never place the owner's private key here.
