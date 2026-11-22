# Black-box boundary and unlock protocol

The two workers have independent OS identities, private role instructions, and private memory directories. Only public verdicts are copied into the routing result. The sealed reviews are encrypted and are distributed in the ZIP without the private key.

**User control:** the private unlock key is a distinct downloadable artifact, not contained in this package. No sealed report has been decrypted during this experiment. An unlock requires an explicit user instruction. On any host that has the unlock key, use `src/unlock_report.py --private-key /path/to/key.pem --sealed-report /path/to/sealed_review.json` only after that instruction.

**Caveat:** the current chat's administrative runtime has access to its file system and could technically read unencrypted runtime state or the separately stored key. This is a procedural lock and an OS-identity boundary, **not** a proof that the supervising model is physically incapable of accessing state. True administrator-independent privacy requires external key custody and a separate security domain.

Do not distribute the private key in the workspace ZIP. Do not hand an Auditor access to Producer memory, or vice versa. Do not let a creator approve its own artistic work.
