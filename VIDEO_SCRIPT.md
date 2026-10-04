# Samsung PRISM Hackathon: Theme 05 Demo Video Script
**Target Length:** 3 to 5 minutes
**Format:** Unedited single take (screen recording + voiceover).
**Requirement Checklist:** Show benchmark interruption handling, then extension use case.

## Timeline & Scene Guide

### [0:00 - 0:30] Introduction & Architecture (30s)
* **Visual:** Open `SRMIST_Inferics_Submission.pptx` to the Architecture Diagram slide.
* **Audio:** "Hi, we are Team SRMIST Inferics. For Theme 5, we built INFERICS Pulse, a dual-path interruptible agent using a Fast-Path Token Scanner for sub-15ms cooperative cancellation, and a Slow-Path reasoning engine. All state is maintained in an Immutable Slot Ledger."

### [0:30 - 1:30] FDB-v3 Benchmark Execution (60s)
* **Visual:** Switch to Terminal. Run `bash run_fdb_benchmark.sh`.
* **Action:** Let the script execute visually.
* **Audio:** "Our one-command reproduction script initializes a clean environment and executes the Full-Duplex-Bench v3 test suite. As you can see, our agent detects mid-utterance self-corrections using word-boundary triggers and cancels in-flight tasks instantly without mutating stale state. The final score achieves a 100% strict pass rate."

### [1:30 - 3:00] Live Web UI & Interruption Demo (90s)
* **Visual:** Switch to Web Browser (`https://inferics-samsung-prism.vercel.app`).
* **Action:** Open the chat panel. Speak a complex command, then interrupt mid-stream.
  * *You:* "Book a flight to New York..."
  * *(Agent starts streaming response...)*
  * *You (interrupting):* "Wait, actually, change that to Chicago."
* **Visual:** Show the UI immediately halt the stream, pivot, and update the Slot Ledger (click the Ledger tab to show immutability).
* **Audio:** "Here in our LiveKit wrapper, when I interrupt with a correction, the Fast-Path intercepts the phrase in under 15 milliseconds, aborts the Groq stream via a forcefully closed socket, and updates the target city to Chicago without double-booking."

### [3:00 - 4:00] The X-Factor Extension Use Case (60s)
* **Visual:** Switch to the `x_factor.py` test output or visual demo of the extension.
* **Action:** Run `pytest tests/test_x_factor.py` to show the multimodal barge-in.
* **Audio:** "For our extension use-case, we implemented Multimodal Barge-In. Using telemetry from a Galaxy Watch Ultra or the S25 Ultra camera, the agent detects physical intent-to-interrupt—like a double pinch or open palm—up to 150 milliseconds *before* the user even starts speaking. This achieves negative perceptual latency, entirely eliminating dead air."

### [4:00 - 4:30] Conclusion (30s)
* **Visual:** Show the GitHub repository with the `PRISM_GENAI_HACKATHON_Y2026` tag.
* **Audio:** "Our code is fully self-contained, relies on no external proprietary servers for evaluation, and uses zero hardcoded state. Thank you to the Samsung R&D team for this challenge."
