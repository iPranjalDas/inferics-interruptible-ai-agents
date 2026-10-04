// Vercel Serverless Function: POST /api/device/control

export default function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  res.setHeader("Cache-Control", "no-cache, no-store, must-revalidate");

  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  const { device_id, action, value } = req.body || {};
  return res.status(200).json({
    success: true,
    device_id: device_id || "s25_ultra",
    action: action || "status_sync",
    status: "Active",
    value: value || null
  });
}
