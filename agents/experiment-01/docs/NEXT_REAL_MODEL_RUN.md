# Next experiment — two real local language-model instances

Prerequisites (currently unavailable in this chat runtime):
- Ollama or another compatible local LLM inference service running at 127.0.0.1:11434.
- A model with image support (the auditor receives three image panels as base64).
- A host able to run two separate subprocesses under different users, or genuinely isolated containers.

Recreate the UID permissions described by `src/setup_linux_isolation.sh`, ensure the experimental unlock key is managed by the owner, then invoke:

```bash
python src/launch_agents.py --backend ollama --model qwen3-vl:4b
```

The default model is an example of a vision-oriented option. It must already be installed; installation and performance have not been tested here. Start with serial inference requests if hardware resources are constrained; parallel worker processes do not require simultaneous GPU inference.

To assess whether role-specific memory changes decisions, submit a second candidate and confirm memory files persist separately. Do not mistake two model calls from one shared model as model fine-tuning or architectural independence of the weights.

On Windows, use containers or separate OS accounts to preserve privacy. Running `--allow-same-uid` deliberately weakens the separation and must not be called a secure black box.
