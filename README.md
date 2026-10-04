# 📱 Samsung PRISM GenAI Hackathon (Theme 05: Interruptible Real-Time Agents)
## Team: **INFERICS** · Submission Master Repository
### Project: **INFERICS Pulse — Multi-Domain Agent OS 2.0**

[![Theme](https://img.shields.io/badge/Samsung%20PRISM-Theme%2005%3A%20Interruptible%20Agents-034EA2.svg)](https://github.com/iPranjalDas/samsung-prism-genai-hackathon)
[![Team](https://img.shields.io/badge/Team-INFERICS-1428A0.svg)](https://github.com/iPranjalDas/samsung-prism-genai-hackathon)
[![FDB-v3 Benchmark](https://img.shields.io/badge/FDB--v3%20Benchmark-PASS%20(100%25)-brightgreen.svg)](run_fdb_benchmark.sh)
[![Barge-in](https://img.shields.io/badge/Interruption%20Halt-11.8ms-blue.svg)](server.py)
[![TTFT](https://img.shields.io/badge/TTFT-84ms%20(Groq%20LPU)-emerald.svg)](server.py)
[![Production](https://img.shields.io/badge/Live%20Demo-inferics--samsung--prism--bay.vercel.app-purple.svg)](https://inferics-samsung-prism-bay.vercel.app)

---

## 📌 Submission Information

- **Team Name**: `INFERICS`
- **Team Lead**: `Pranjal Das`
- **Project Name**: `INFERICS Pulse — Interruptible Multi-Domain Agent OS (Theme 05)`
- **GitHub Repository**: [`https://github.com/iPranjalDas/samsung-prism-genai-hackathon`](https://github.com/iPranjalDas/samsung-prism-genai-hackathon)
- **Live Demo (Vercel)**: [`https://inferics-samsung-prism-bay.vercel.app`](https://inferics-samsung-prism-bay.vercel.app)
- **Submission Date**: `October 4, 2026`

---

## 📋 Hackathon Submission Checklist

| Item | Status | Deliverable & File Location |
| :--- | :---: | :--- |
| **1. Source Code** | ✅ Complete | Complete Next.js/React Frontend UI (`web/`), FastAPI Backend (`server.py`), and RAG Knowledge Base (`samsung_knowledge_base.json`). |
| **2. Presentation** | ✅ Complete | 12-Slide Master Pitch Deck: [`PITCH_DECK.md`](./PITCH_DECK.md) containing the problem statement, architecture diagrams, and competitive moat. |
| **3. Video** | ✅ Complete | High-Definition Demo Video (Youtube Link in Submission Portal) |
| **4. AI Disclosure** | ✅ Complete | Official AI Usage Disclosure: [`INFERICS_Theme05_AI_Disclosure.md`](./INFERICS_Theme05_AI_Disclosure.md) attached in repo root. |
| **5. Detailed README** | ✅ Complete | This master documentation detailing the Fast-Path Reactor, Immutable Slot Ledger, and Tri-Mode RAG architecture. |
| **6. Testing Harness** | ✅ Complete | Automated FDB-v3 Evaluation Benchmark suite: [`run_fdb_benchmark.sh`](./run_fdb_benchmark.sh). |
| **7. Vercel Deployment** | ✅ Complete | Fully deployed serverless API endpoint executing the 84ms Tri-Mode RAG. |

---

## 💡 Why Our Agent is Special: The Tri-Mode & Dual-Queue Architecture

Traditional conversational AI operates under a **rigid, turn-based request-response paradigm**. In real-world human interactions, this paradigm breaks down completely:
1. **The In-Flight Mutation Problem:** Once an external API call is initiated, a user mid-sentence interruption (*"Wait, make that Bangalore, not Delhi!"*) results in duplicate actions, phantom bookings, or corrupted state.
2. **Conversational Lag:** Waiting for end-of-turn token generation introduces an unacceptable 800ms–2500ms latency floor.

**INFERICS Pulse** replaces turn-taking with a **decoupled, full-duplex dual-path event loop**:

### 1. Fast-Path Micro-Reactor (<15ms Barge-in)
Executes sub-15ms cooperative task cancellations and delivers sub-50ms conversational fillers. When a user interrupts the agent via Voice Activity Detection (VAD) or text, the `cancel_all_in_flight()` protocol atomically halts all speculative LLM generation blocks in memory.

### 2. Immutable Slot-DAG Ledger
An immutable dictionary system ensuring deterministic state tracking. We strictly gate state-modifying actions behind a confirmation barrier. If a user interrupts mid-sentence, the DAG execution rolls back instantly, completely preventing side-effect leaks or ghost database writes.

### 3. Tri-Mode Semantic RAG Router (Theme 04 Integration)
To further eliminate latency on generic queries while maintaining bulletproof accuracy for Samsung products, we implemented a Tri-Mode Router (borrowing inspiration from the best Streaming RAG designs):
- **Mode 1 (Zero-Waste Bypass):** For non-Samsung queries, the system completely bypasses the Vector database for an ultra-low **84ms Time-To-First-Token (TTFT)**.
- **Mode 2 (Strict Grounding):** For Samsung specs, the system slices the 23-product JSON corpus and forces the LLM to cite facts using immutable `[DOC-x]` anchors. 
- **Mode 3 (Competitor Neutrality):** Generates flawlessly neutral side-by-side comparison tables against competitors without ever disparaging the rival brand, adhering perfectly to Samsung corporate guidelines.

---

## ⚙️ Running the FDB-v3 Benchmark

The project includes an automated test harness to prove the sub-15ms interruption safety limit. 

```bash
# Make the script executable
chmod +x run_fdb_benchmark.sh

# Run the strict benchmark suite
./run_fdb_benchmark.sh
```

**What the Benchmark Tests:**
1. Atomic Slot Updates: Verifies state changes do not leak on interruption.
2. Latency Thresholds: Asserts Fast-Path halt happens in <15ms.
3. Speculative Rejection: Asserts state-modifying endpoints (like `book_flight`) require user convergence.

---
## 🏆 Built for Samsung PRISM (Theme 05)

---

## 📂 Repository Structure

```text
📦 inferics-interruptible-ai-agents
 ┣ 📂 api/                # Vercel Serverless Functions (Tri-Mode Router & Intent Gates)
 ┣ 📂 images/             # Documentation, HUD visualizers, and UI Mockup Images
 ┣ 📂 public/             # Static Frontend serving the React/Tailwind Bundle
 ┣ 📂 scripts/            # Hardware-specific evaluation and utility scripts
 ┣ 📂 src/                # Core Python Engine (Fast-Path Reactor, Immutable Slot Ledger)
 ┣ 📂 tests/              # Pytest FDB-v3 evaluation harness
 ┣ 📜 INFERICS_Theme05_AI_Disclosure.md  # Official Theme 05 AI Usage Disclosure Form
 ┣ 📜 PITCH_DECK.md       # Master 12-Slide Pitch Deck Presentation
 ┣ 📜 README.md           # Master Technical Architecture Documentation
 ┣ 📜 livekit_agent.py    # WebRTC LiveKit Voice Agent Cloud Worker
 ┣ 📜 run_fdb_benchmark.sh# FDB-v3 Automated Evaluation Suite Entrypoint
 ┣ 📜 samsung_knowledge_base.json # 23-Product Offline Corpus for Semantic RAG
 ┣ 📜 server.py           # Master Asyncio Event Loop & Backend definitions
 ┗ 📜 vercel.json         # Vercel Serverless Deployment & Rewrite Configuration
```

---

## 👥 About Team INFERICS

We are **Team INFERICS**, representing SRM Institute of Science and Technology, KTR. We specialize in building robust, low-latency, and highly scalable AI architectures that prioritize empirical reliability and human-centric design over fragile theoretical models.

- **Pranjal Das** — *Team Lead & Principal Architect*
- **Contact:** pranjal.das@srmist.edu.in
- **Organization:** SRM Institute of Science and Technology, KTR

*Built with precision for the Samsung PRISM GenAI Hackathon 2026 (Theme 05).*
