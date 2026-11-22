# Release approval gates

Each review is a signed record in `reviews/v22_review_status.json` with `verdict`, `execution_mode`, `evidence`, `defects`, `reviewed_at`. Every PASS must specify existing evidence files, and independent reviewer credit is truthful only if an independent agent/reviewer actually ran. `BLOCKED` is not PASS.

| Gate | Owner / non-author review | Pass criterion |
|---|---|---|
| Story and hook | Creative Director | A coherent 30-second visual story with clear hook, readable reversal, final cliffhanger; first/last frame of each scene exists |
| Visual identity | 3D Art Director | Cast matches approved character references in front/side/three-quarter; anatomical joints and proportions; no capsule-manikin seams |
| Originality | Originality Editor | Distinctive Villa Verse look and behavior, no generic first-default visual grammar; audience-specific reason documented |
| Animation and contact | 3D Animator + Auditor | Natural transfer of body weight, connected joints, stable feet; believable finger wrap, no visible mesh penetration from 3 angles |
| Face | 3D Art Director + Auditor | Mouth corners integrated with face, eyelids and visemes readable in motion; no detached layers, tears, excessive stretch |
| Engineering | Technical Director | Reproducible scene and model build, full video decodes, recorded collision/deformation tests, **actual Godot import + playback screenshots/log** |
| Independent audit | Independent Auditor | Inspects entire clip at normal speed and critical closeups, documents failures and exact evidence; not creator self-review |
| Producer release | Executive Producer | All mandatory gates PASS, no high severity unresolved issues, full versioned handover and signed ledger |

For research/test releases, producer may declare a `PROTOTYPE` status even with blocked gates, but must not call it approved artwork or present it as final.
