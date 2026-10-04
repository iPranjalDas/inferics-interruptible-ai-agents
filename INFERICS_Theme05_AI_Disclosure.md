# AI Usage DISCLOSURE FORM

### 1. Team Details
*   **Team Name:** INFERICS
*   **Project / Product Name:** Samsung PRISM — Interruptible Multi-Domain Agent OS 2.0 (Theme 05)
*   **Organization / Institution (if any):** SRM Institute of Science and Technology, KTR
*   **Submission Date:** October 4, 2026

### 2. AI Usage Declaration
*   **Did your team use any Artificial Intelligence (AI) in developing this project?** [X] Yes [ ] No
*   **Brief Declaration:** Yes, AI tools were utilized strictly as pair-programming assistants for debugging syntax errors, generating frontend CSS boilerplate, and formatting markdown documentation. 100% of the core system architecture, concurrency logic, and interruptible state-management was manually designed, coded, and tested by the team.

### 3. Purpose of AI Usage *(Brief Details)*
*   **Idea generation / brainstorming:** Used as a sounding board to compare Python `asyncio` event loop performance limits.
*   **Code generation or assistance:** Generated generic Tailwind CSS styling boilerplate and standard WebSocket connection templates to save time on UI scaffolding.
*   **UI / UX design:** AI suggested color palettes for the dark/light mode toggle.
*   **Content creation:** Polished the grammar and formatting of the README.md and Pitch Deck slides.
*   **Data analysis:** None / N/A (Metrics were logged and calculated manually via our custom telemetry engine).
*   **Testing / debugging:** Used to quickly spot missing commas in JSON files and resolve basic React `useEffect` dependency warnings.
*   **Other:** None / N/A

### 4. Feature Origin Classification

**1. Feature Name:** Sub-15ms Fast-Path Voice Interruption Reactor
*   **Self-Generated/AI-Generated/Both:** Both (95% Human Architecture, 5% AI Syntax Assistance)
*   **Description:** *AI tools: Antigravity / Groq.* Prompt: "How to properly cancel an asyncio.Task in Python 3.10?". Output Summary: Provided standard Python documentation examples for task cancellation. Modification: We manually engineered the entire Barge-in Reactor, bound it to the Voice Activity Detection (VAD) buffer, and built the multi-threaded lock mechanisms to guarantee sub-15ms halts.

**2. Feature Name:** Immutable Slot Ledger & Atomic DAG Rollback
*   **Self-Generated/AI-Generated/Both:** Self-Generated (AI used only for Unit Tests)
*   **Description:** *AI tools: Antigravity.* Prompt: "Generate a pytest mock harness for a dictionary state manager". Output Summary: Generated a basic `pytest` file with mock user inputs. Modification: We completely designed the immutable data structures, thread-safe cloning logic, and the DAG rollback engine from scratch to prevent state-leaks.

**3. Feature Name:** Tri-Mode Semantic Routing Engine & Zero-Waste Bypass
*   **Self-Generated/AI-Generated/Both:** Both (90% Human, 10% AI Regex Optimization)
*   **Description:** *AI tools: Antigravity.* Prompt: "Optimize this regex pattern for faster string matching". Output Summary: AI provided a slightly faster `\b` word-boundary regex. Modification: We manually engineered the tri-mode logic gate, manually compiled the 23-product Samsung knowledge base, and strictly coded the neutral competitor comparison prompt logic.

**4. Feature Name:** React Telemetry HUD & Live Metrics
*   **Self-Generated/AI-Generated/Both:** Both (85% Human, 15% AI Styling)
*   **Description:** *AI tools: Antigravity.* Prompt: "Tailwind CSS classes for a floating glassmorphism sidebar". Output Summary: AI provided the CSS class strings for the sidebar. Modification: We manually built the React state management, custom Server-Sent Events (SSE) chunk decoder, and the live Time-To-First-Token (TTFT) calculating logic.

### 5. Ethical & Compliance Confirmation
*   **AI usage complies with guidelines and policies:** [X] Yes
*   **No proprietary or copyrighted data misused:** [X] I Agree

### 6. Declaration & Sign-Off
*   **Name of Team Representative:** Pranjal Das
*   **Role:** Team Lead / Principal Architect
*   **Signature:** Pranjal Das
*   **Date:** October 4, 2026
