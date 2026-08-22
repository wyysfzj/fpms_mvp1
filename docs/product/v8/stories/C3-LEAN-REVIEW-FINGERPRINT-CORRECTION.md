# Correction — C3 Lean Review Fingerprints

- Risk: `PROTECTED`
- Outcome: correct seven ledger transcription values so they equal the deterministic
  Git-tree fingerprint of the exact paths at the exact independently approved final
  product commits.
- Product behavior, paths, commits, review verdicts and catalog mappings are unchanged.

| Story | Recorded value | Deterministic exact value |
| --- | --- | --- |
| `V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-CURRENT-ADOPTION` | `30897eb30f288f9e25b7c4f83339227779a1d8f66a2161983234d6f3a28080da` | `b3709aaabde17d8c72c7b88dd683c4f427478cf6842c4fb6292574ece6066ca7` |
| `V8-GRANT-ATTACHMENT-NO-LEGAL-EFFECT-CURRENT-ADOPTION` | `942362f9954afe7829cf2dfee3f395aa096f95cfdeb2eb91bf66ba562e991588` | `a965c22fff742a4fa2f463132e58be068a4e9278f8594a96968f7eec0f0c479b` |
| `V8-GRANT-FEE-DONE-NO-LEGAL-EFFECT-CURRENT-ADOPTION` | `1b08626ba493ad5d6cbc4ead7b0fd503ba44ae04e9022a5b8399701cba72bd51` | `0b32855ce5093c4eeface5e8aa27c676e17cdd4c3b3739b98f80aed3ae1cd455` |
| `V8-FORMAT-LETTER-CONTEXT-CURRENT-ADOPTION` | `4ecc32562627edc76d589b0d63338c82db497f98cc40ea438971f8572d94c822` | `38c1e4bb96ac35ac95505a1d4b2c7cf49ee74a7ec7aaa0169d0f9ebf56d1c42d` |
| `V8-FORMAT-LETTER-RENDER-CURRENT-ADOPTION` | `352dbbdeab9256856451aa2655c46a038939cdd54898463d3ae9cc9cf4cc8fcf` | `aed105f8b183d4e2ae78054de8eca4bf9cd509da382bc827b6e933a4c59c14a8` |
| `V8-FORMAT-LETTER-ARCHIVE-CURRENT-ADOPTION` | `869e85c4d39a133be02987ce7e790643b1f4ee42861ecaba826c402f94552efa` | `89a2d105c9a5b193864083b9bb9c4dc11382590712663de8750f5808da93eee6` |
| `V8-GRANT-INSTRUCTION-OBLIGATION-ADAPTER-CURRENT-ADOPTION` | `634732ca0b991c215e386047865fb1ec55ecf1746e8f22df0902893b7760461a` | `1adde3ccd5c5912ba75ce7130c0a6b350c3478d945d6ca5a810671afb152c315` |

Each deterministic value is produced by the repository checker's published algorithm:
sort the unique exact paths, read each Git mode/type/blob at the story's final commit, hash
the NUL-delimited records, and SHA-256 the concatenation. A correction is accepted only
after independent review recomputes all seven values and the full current ledger validates.
