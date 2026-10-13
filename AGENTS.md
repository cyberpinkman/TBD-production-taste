# Working on this repository

This repository publishes reusable production methods, not private episodes.

- Keep examples fictional. Do not add real recordings, transcripts, guest information, local absolute paths, credentials, model weights or unlicensed assets.
- Keep original source media and historical deliveries immutable. Publishing documentation does not authorize publishing an episode.
- Preserve the distinction between required invariants, adjustable style defaults and unverified observations. ASR, acoustic scores, technical checks and human approval are different evidence.
- Diagnose failures across source, sync, edit mapping, frame extraction, caption generation, rendering and muxing. Establish the causal mechanism and violated invariant before changing behavior; separate trigger, root cause, symptoms and affected consumers.
- Correct the shared layer that owns the invariant. Avoid episode-specific offsets, retries and exceptions. Demonstrate the original failure condition and correction at that boundary; add integration coverage only when actual runtime/media semantics differ.
- The starter supports straight cuts and a single subtitle track; do not silently represent more complex timelines as validated. It does not inspect real media or approve content.
- Keep skills independently usable after installation. Do not add mandatory proprietary plugins or copy third-party skill code without a verified license.
- Run `python3 -m unittest discover -s tests -v` and the synthetic validation after changing executable behavior. Check public links and skills when changing their references.
- Report code/tests, actual media checks, human review and publishing as separate outcomes.
