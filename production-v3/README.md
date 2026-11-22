# Villa Verse v3.0 — Producer-led production operating system

This is a **workflow and QA release**, not a newly rendered animation or independently run AI agent team. It preserves a small v2.1 intake evidence set, ten Claude Code-compatible agent definitions, a real dependency-based v2.2 work plan, an evidence-sensitive release gate CLI and regression tests.

## What to open
1. `docs/PRODUCER_WORKFLOW.md`: the hierarchy, parallelism, and feedback loop.
2. `plans/V22_TASK_BOARD.json`: assigned next tasks, not completed work.
3. `docs/PRODUCER_V21_REVIEW.md`: the immediate v2.1 audit and why final production is blocked.
4. `docs/ACCEPTANCE_GATES.md`: who must approve and what proof is required.
5. `.claude/agents/`: ten executable Claude Code *definitions*; they have not been invoked in this ChatGPT session.
6. `AGENTS.md` and `CLAUDE.md`: durable direction and regression constraints.
7. `scripts/producer.py`: release gate status and evaluation; `tests/test_producer.py` for implemented tests.

## Test results
Run `python tests/test_producer.py` and `python scripts/producer.py evaluate` to verify that the release is rightly **HOLD** while v2.2 is unperformed. A fake approval must not pass because evidence paths and an actually independent execution mode are required.

## Constraints and future execution
No ChatGPT-hosted independent subagent executor or Claude Code executable was present for this run. A single-model role review does not equal ten independently functioning agents. Using Claude Code subagents may consume more Claude account usage; experimental teams use more tokens and are deliberately not enabled. This package does not require a new paid subscription to inspect or use its static scripts. The complete v2.1 history, executable source, GLBs, and prior archives are embedded in `baseline/VillaVerse_v2_1_FULL_HANDOVER.zip`, in addition to the small direct evidence samples.
