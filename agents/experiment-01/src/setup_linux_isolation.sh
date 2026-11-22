#!/usr/bin/env bash
# Linux root-only setup. This does not supply or run an LLM model.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
[[ $EUID -eq 0 ]] || { echo 'Root needed for distinct UIDs' >&2; exit 1; }
for u in vvexp01p vvexp01a; do id "$u" >/dev/null 2>&1 || useradd --system --no-create-home --shell /usr/sbin/nologin "$u"; done
mkdir -p "$root/run/private_producer" "$root/run/private_auditor" "$root/outputs/producer" "$root/outputs/auditor"
chown vvexp01p:vvexp01p "$root/run/private_producer" "$root/outputs/producer" "$root/config/PRODUCER_SYSTEM.md"
chown vvexp01a:vvexp01a "$root/run/private_auditor" "$root/outputs/auditor" "$root/config/AUDITOR_SYSTEM.md"
chmod 700 "$root/run/private_producer" "$root/run/private_auditor" "$root/outputs/producer" "$root/outputs/auditor"
chmod 400 "$root/config/PRODUCER_SYSTEM.md" "$root/config/AUDITOR_SYSTEM.md"
chmod 444 "$root/evidence/v21_evidence.json"
chmod 755 "$root" "$root/src" "$root/config" "$root/keys" "$root/run" "$root/evidence" "$root/evidence/visuals"
echo 'Setup completed. These permissions isolate two UIDs but not the host root administrator.'
