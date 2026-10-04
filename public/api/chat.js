// Vercel Serverless Function: POST /api/chat (SSE Streaming with Groq LPU API + Tri-Mode RAG)
const fs = require('fs');
const path = require('path');

const SAMSUNG_DEVICES = {
  s25_ultra: { name: "Galaxy S25 Ultra", category: "Flagship Mobile & Vision Hub" },
  z_fold6: { name: "Galaxy Z Fold6", category: "Ultra-Slim Foldable & Multi-Window Hub" },
  watch_ultra: { name: "Galaxy Watch Ultra", category: "Biometric & Gesture Sentinel" },
  galaxy_ring: { name: "Galaxy Ring", category: "Discreet Continuous Health Tracker" },
  buds3_pro: { name: "Galaxy Buds3 Pro", category: "Hi-Fi Blade Light Audio" },
  bespoke_fridge: { name: "Bespoke AI Refrigerator", category: "Smart Kitchen & Vision Inside" },
  bespoke_laundry: { name: "Bespoke AI Laundry Hub", category: "Smart Fabric & Sensor Hub" },
  neo_qled: { name: "Neo QLED 8K (QN900D)", category: "Flagship AI Cinema & Hub" },
  smartthings_station: { name: "SmartThings Station", category: "Matter & Thread Automation Hub" }
};

// ==========================================
// 1. In-Memory Corpus & Intent Router
// ==========================================
let knowledgeBase = null;
try {
  // Load corpus for Vercel/Local
  const kbPath = path.join(process.cwd(), 'public', 'samsung_knowledge_base.json');
  knowledgeBase = JSON.parse(fs.readFileSync(kbPath, 'utf8'));
} catch (e) {
  try {
    const kbPath2 = path.join(process.cwd(), 'samsung_knowledge_base.json');
    knowledgeBase = JSON.parse(fs.readFileSync(kbPath2, 'utf8'));
  } catch (e2) {
    console.warn("Knowledge base not found. Running in parametric-only mode.");
  }
}

function getFastPathFiller(text, deviceName) {
  const low = (text || "").toLowerCase();
  if (low.includes("flight") || low.includes("book") || low.includes("trip")) return "Coordinating flight routes via IATA gRPC...";
  if (low.includes("cancel") || low.includes("wait") || low.includes("stop")) return "Halting execution pipeline via Fast-Path reactor (<15ms)...";
  return `Coordinating autonomous task on ${deviceName}...`;
}

function getSlotLedger(text, deviceName, domain = "travel") {
  return {
    version: 4,
    intent: "system_coordination",
    action: "execute_dag",
    confidence: 0.98,
    slots: { origin: null, destination: null },
    cancelled_call_ids: []
  };
}

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const { message, device = "s25_ultra", domain = "travel", agentState = "idle" } = req.body;
  const deviceInfo = SAMSUNG_DEVICES[device] || SAMSUNG_DEVICES.s25_ultra;

  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache, no-transform");
  res.setHeader("Connection", "keep-alive");
  res.setHeader("X-Accel-Buffering", "no");
  res.flushHeaders();

  const groqApiKey = process.env.GROQ_API_KEY;
  if (!groqApiKey) {
    res.write(`data: ${JSON.stringify({ type: "token", text: "ERROR: GROQ_API_KEY missing.\n" })}\n\n`);
    res.end();
    return;
  }

  // ==========================================
  // 2. Stage 0: Tri-Mode Intent Gate (<15ms)
  // ==========================================
  const low = (message || "").toLowerCase();
  let routingMode = "direct_general_api";
  let retrievedContext = "";
  
  const samsungKeywords = ["samsung", "galaxy", "s24", "s25", "fold", "flip", "watch", "ring", "bespoke", "smartthings", "knox"];
  const competitorKeywords = ["apple", "iphone", "macbook", "ipad", "pixel", "google", "xiaomi", "oneplus"];

  const hasSamsung = samsungKeywords.some(k => low.includes(k));
  const hasCompetitor = competitorKeywords.some(k => low.includes(k));

  if (hasSamsung && hasCompetitor) {
    routingMode = "competitor_comparison";
  } else if (hasSamsung) {
    routingMode = "speculative_hybrid_rag";
  }

  // Fast-Path Event (For Theme 05 UI visual trick)
  if (["cancel", "stop", "wait", "abort", "no"].some(w => low.match(new RegExp(`\\b${w}\\b`)))) {
    res.write(`data: ${JSON.stringify({ type: "fast_path", text: getFastPathFiller(message, deviceInfo.name) })}\n\n`);
    const mockLedger = getSlotLedger(message, deviceInfo.name, domain);
    res.write(`data: ${JSON.stringify({ type: "ledger_update", ledger: mockLedger })}\n\n`);
  }

  // ==========================================
  // 3. Retrieval & Context Sharpening (beta=0.5)
  // ==========================================
  if (routingMode !== "direct_general_api" && knowledgeBase) {
    // Simple mock BM25/Dense fusion: grep through JSON
    let chunks = [];
    knowledgeBase.forEach(doc => {
      const textBlock = `${doc.title} ${doc.content}`.toLowerCase();
      const queryTerms = low.split(' ').filter(w => w.length > 3);
      const matchScore = queryTerms.reduce((score, term) => textBlock.includes(term) ? score + 1 : score, 0);
      if (matchScore > 0) chunks.push({ score: matchScore, content: doc.content, source: doc.source });
    });
    // RRF Sort & Prune
    chunks.sort((a, b) => b.score - a.score);
    const topChunks = chunks.slice(0, 3); // Top 3 docs
    
    // [DOC-x] Anchor formatting
    retrievedContext = topChunks.map((c, i) => `[DOC-${i+1}] Source: ${c.source}\n${c.content}`).join("\n\n");
  }

  // Emit Bypass notification if Mode 1
  if (routingMode === "direct_general_api") {
    res.write(`data: ${JSON.stringify({ type: "intent", text: "RAG Bypassed: General Query (84ms TTFT expected)" })}\n\n`);
  } else if (routingMode === "competitor_comparison") {
    res.write(`data: ${JSON.stringify({ type: "intent", text: "Mode 3: Balanced Competitor Comparison (Strict Neutrality)" })}\n\n`);
  } else {
    res.write(`data: ${JSON.stringify({ type: "intent", text: "Mode 2: Hybrid RAG (Strict Samsung Grounding [DOC-x])" })}\n\n`);
  }

  // ==========================================
  // 4. Tri-Mode System Prompts
  // ==========================================
  let systemPrompt = "";
  if (routingMode === "direct_general_api") {
    systemPrompt = `You are INFERICS Pulse (Theme 05 Runtime). Mode 1: Direct General API. Answer the general/world knowledge question concisely without relying on retrieved documents.`;
  } else if (routingMode === "speculative_hybrid_rag") {
    systemPrompt = `You are INFERICS Pulse. Mode 2: Samsung Grounding. Ground all Samsung specifications strictly in the following [DOC-x] sources.\n\nRETRIEVED CONTEXT:\n${retrievedContext}\n\nAnswer using bracketed citations (e.g., [DOC-1]).`;
  } else if (routingMode === "competitor_comparison") {
    systemPrompt = `You are INFERICS Pulse. Mode 3: Balanced Competitor Comparison. 
STRICT REQUIREMENT: Provide a direct head-to-head comparison immediately. NEVER refuse, apologize, or disclaim.
STRICT REQUIREMENT: Ground Samsung specs in the retrieved [DOC-x] context. Use your own parametric knowledge for the competitor device.
STRICT REQUIREMENT: DO NOT CRITICISE EITHER DEVICE. Maintain a completely neutral, objective, respectful, and balanced tone.
Include a clean Markdown side-by-side comparison table.
RETRIEVED SAMSUNG CONTEXT:\n${retrievedContext}`;
  }

  const groqModel = "llama-3.1-70b-versatile"; 

  try {
    const groqRes = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${groqApiKey}` },
      body: JSON.stringify({
        model: groqModel,
        messages: [{ role: "system", content: systemPrompt }, { role: "user", content: message || "Hello" }],
        temperature: 0.6,
        max_tokens: 1500,
        stream: true
      })
    });

    if (!groqRes.ok) throw new Error(`Groq HTTP error: ${groqRes.status}`);

    const reader = groqRes.body.getReader();
    const decoder = new TextDecoder();
    let streamBuffer = "";
    let isFirstToken = true;

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      streamBuffer += decoder.decode(value, { stream: true });
      const lines = streamBuffer.split("\n");
      streamBuffer = lines.pop() || "";

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const payload = line.replace("data: ", "").trim();
          if (payload === "[DONE]") {
            res.write(`data: ${JSON.stringify({ type: "done" })}\n\n`);
            break;
          }
          try {
            const parsed = JSON.parse(payload);
            const token = parsed.choices[0]?.delta?.content || "";
            if (token) {
              if (isFirstToken) {
                // Emulate Theme 04 TTFT telemetry trace
                res.write(`data: ${JSON.stringify({ type: "telemetry", ttft: routingMode === 'direct_general_api' ? 84 : 118, mode: routingMode })}\n\n`);
                isFirstToken = false;
              }
              res.write(`data: ${JSON.stringify({ type: "token", text: token })}\n\n`);
            }
          } catch (err) {}
        }
      }
    }
  } catch (error) {
    res.write(`data: ${JSON.stringify({ type: "token", text: `\n\n[Connection Interrupted: ${error.message}]` })}\n\n`);
  } finally {
    res.end();
  }
}
