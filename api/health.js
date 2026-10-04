// Vercel Serverless Function: GET /api/health

export default function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, OPTIONS");
  res.setHeader("Cache-Control", "no-cache, no-store, must-revalidate");

  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  const groqKey = process.env.GROQ_API_KEY;

  return res.status(200).json({
    status: "healthy",
    engine: "NEXUS-DUAL-v2",
    theme: "Samsung Galaxy AI x Theme 05",
    groq_connected: Boolean(groqKey),
    groq_model: "qwen/qwen3.8-27b",
    latency_guarantee: "<15ms interruption"
  });
}
