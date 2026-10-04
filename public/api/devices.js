// Vercel Serverless Function: GET /api/devices
const samsungDevices = {
  s25_ultra: {
    id: "s25_ultra",
    name: "Galaxy S25 Ultra",
    category: "Flagship Mobile & Vision Hub",
    status: "Online",
    battery: 88,
    image: "/assets/products/s25_ultra.png",
    npu: "45 TOPS (Snapdragon 8 Elite)",
    features: ["200MP Vision AI", "Live Translate", "Circle to Search", "ProVisual Engine"],
    active_feature: "200MP Vision AI Grounding",
    telemetry: { signal: "5G Ultra", temp_c: 32.4, fps: 60 }
  },
  z_fold6: {
    id: "z_fold6",
    name: "Galaxy Z Fold6",
    category: "Ultra-Slim Foldable & Multi-Window Hub",
    status: "Online",
    battery: 82,
    image: "/assets/products/z_fold6.png",
    npu: "45 TOPS (Snapdragon 8 Gen 3 for Galaxy)",
    features: ["7.6\" Dynamic AMOLED 2X", "Dual-Screen Interpreter", "Note Assist with S Pen", "Armor Aluminum Frame"],
    active_feature: "FlexMode Multi-Active Window Ready",
    telemetry: { crease_durability: "200k+ Folds", temp_c: 31.8, weight_g: 239 }
  },
  watch_ultra: {
    id: "watch_ultra",
    name: "Galaxy Watch Ultra",
    category: "Biometric & Gesture Sentinel",
    status: "Connected",
    battery: 94,
    image: "/assets/products/watch_ultra.png",
    features: ["Double-Pinch Barge-In", "BioActive Sensor", "Dual-Freq GPS", "Titanium Grade 4 Cushion"],
    active_feature: "Double-Pinch Gesture Detection Ready",
    telemetry: { heart_rate_bpm: 74, stress: "Optimal", spo2_pct: 99 }
  },
  galaxy_ring: {
    id: "galaxy_ring",
    name: "Galaxy Ring",
    category: "Discreet Continuous Health Tracker",
    status: "Tracking",
    battery: 96,
    image: "/assets/products/galaxy_ring.png",
    features: ["Titanium Grade 5", "Energy Score", "Sleep Apnea Monitoring", "100m Water Resistance"],
    active_feature: "Continuous Heart Rate & Sleep Stage Analysis",
    telemetry: { battery_days: "7 Days", temp_skin_c: 36.4, weight_g: 2.3 }
  },
  buds3_pro: {
    id: "buds3_pro",
    name: "Galaxy Buds3 Pro",
    category: "Hi-Fi Blade Light Audio",
    status: "In Ear",
    battery: 85,
    image: "/assets/products/buds3_pro.png",
    features: ["Adaptive ANC", "Blade Lights", "24-bit 96kHz Hi-Fi Audio", "Voice Detect Auto-Pass"],
    active_feature: "Ultra Wideband 24-bit Lossless Codec Active",
    telemetry: { anc_mode: "Adaptive Enhanced", codec: "Samsung Seamless Codec", latency_ms: 22 }
  },
  bespoke_fridge: {
    id: "bespoke_fridge",
    name: "Bespoke AI Refrigerator",
    category: "Smart Kitchen & Vision Inside",
    status: "Cooling",
    battery: null,
    image: "/assets/products/bespoke_fridge.png",
    temperature: "3°C (FlexZone: -1°C)",
    features: ["AI Vision Inside", "Food Expiry Alert", "Auto Open Door", "SmartThings Energy"],
    active_feature: "Food Cam: 4 Items Tracked (Organic Milk, Honeycrisp Apples, Greek Yogurt, Eggs)",
    telemetry: { energy_saving_pct: 18, door_open_count: 5, humidity_pct: 65 }
  },
  bespoke_laundry: {
    id: "bespoke_laundry",
    name: "Bespoke AI Laundry Hub",
    category: "Smart Fabric & Sensor Hub",
    status: "AI Wash Active",
    battery: null,
    image: "/assets/products/bespoke_laundry.png",
    cycle: "AI OptiWash · Cotton Eco",
    remaining_min: 14,
    features: ["AI OptiWash", "Flex Auto Dispense", "Super Speed 28m", "AI Energy Mode"],
    active_feature: "Soil Level Detected: Medium (Adjusting detergent +2ml)",
    telemetry: { water_temp_c: 40, spin_rpm: 1200, vibration_level: "Minimal" }
  },
  neo_qled: {
    id: "neo_qled",
    name: "Neo QLED 8K (QN900D)",
    category: "Flagship AI Cinema & Hub",
    status: "Active Display",
    battery: null,
    image: "/assets/products/neo_qled.png",
    resolution: "7680 x 4320 (8K)",
    features: ["NQ8 AI Gen3 Processor", "8K AI Upscaling Pro", "Glare-Free Screen", "Q-Symphony Sound"],
    active_feature: "NQ8 AI 512 Neural Networks Real-Time Upscaling",
    telemetry: { refresh_rate_hz: 240, sound_channels: "6.2.4ch 90W", ambient_mode: "Art Gallery" }
  },
  smartthings_station: {
    id: "smartthings_station",
    name: "SmartThings Station",
    category: "Matter & Thread Automation Hub",
    status: "Mesh Active",
    battery: null,
    image: "/assets/products/smartthings_station.png",
    nodes: 18,
    features: ["Matter 1.3 Certified", "Thread Border Router", "15W Fast Wireless Charging", "Multi-Device Tap"],
    active_feature: "Living Room Ambient Routine (Cobalt 65%)",
    telemetry: { active_routines: 4, zigbee_channel: 25, uptime_hours: 342 }
  },
  tab_s10_ultra: {
    id: "tab_s10_ultra",
    name: "Galaxy Tab S10 Ultra",
    category: "Dynamic AMOLED 2X & AI S-Pen Hub",
    status: "Online",
    battery: 91,
    image: "/assets/products/tab_s10_ultra.png",
    npu: "Dimensity 9300+ AI NPU",
    features: ["14.6\" Dynamic AMOLED 2X", "Galaxy AI Note Assist", "Anti-Reflective Armor Aluminum", "Included Bluetooth S-Pen"],
    active_feature: "Drawing Assist & PDF Math Solving Engine",
    telemetry: { screen_inch: "14.6", refresh_hz: 120, stylus_latency_ms: 2.8 }
  },
  book5_pro_360: {
    id: "book5_pro_360",
    name: "Galaxy Book5 Pro 360",
    category: "Copilot+ PC & Lunar Lake AI Core",
    status: "Online",
    battery: 89,
    image: "/assets/products/book5_pro_360.png",
    npu: "47 NPU TOPS (Intel Core Ultra 7 256V)",
    features: ["Dynamic AMOLED 2X Touchscreen", "Galaxy AI Multi-Control", "Intel Lunar Lake Architecture", "25h Battery Longevity"],
    active_feature: "On-Device Neural Noise Suppression & Live Subtitles",
    telemetry: { npu_tops: 47, thunderbolt4_ports: 2, weight_kg: 1.69 }
  },
  bespoke_jet_ai: {
    id: "bespoke_jet_ai",
    name: "Bespoke Jet AI Ultra",
    category: "Smart Autonomous Floor Care",
    status: "Standby Docked",
    battery: 100,
    image: "/assets/products/bespoke_jet_ai.png",
    features: ["280W Extreme Suction", "AI Cleaning Mode 2.0", "All-in-One Clean Station Auto-Empty", "Lightweight HexaJet Motor"],
    active_feature: "Brush Load Sensing & Carpet Detection Ready",
    telemetry: { suction_watts: 280, filtration_pct: 99.999, run_time_min: 100 }
  },
  frame_tv: {
    id: "frame_tv",
    name: "The Frame 2025 AI",
    category: "Art Mode & Matte AI Display",
    status: "Art Mode Active",
    battery: null,
    image: "/assets/products/frame_tv.png",
    features: ["Matte Display (Glare-Free)", "Art Store Subscription Hub", "Quantum Processor 4K AI", "Custom Magnetic Bezels"],
    active_feature: "Ambient Motion & Illuminance Auto-Dimming",
    telemetry: { artworks_cached: 2500, bezel_style: "Modern Teak", resolution: "4K UHD" }
  },
  project_ballie: {
    id: "project_ballie",
    name: "Project Ballie AI Robot",
    category: "Robotics Companion & Spatial Projector",
    status: "Autonomous Patrol",
    battery: 79,
    image: "/assets/products/smartthings_station.png",
    features: ["Spatial LiDAR Mapping", "1080p Smart Micro-Projector", "Autonomous Voice Interaction", "SmartThings Device Control"],
    active_feature: "Living Room Spatial Patrol & Pet Surveillance",
    telemetry: { speed_mps: 1.2, lidar_fov: 360, projection_lumens: 300 }
  },
  project_moohan: {
    id: "project_moohan",
    name: "Project Moohan (Android XR)",
    category: "Spatial Computing & Vision AI",
    status: "Development Sandbox",
    battery: 84,
    image: "/assets/products/watch_ultra.png",
    features: ["Dual 4K Micro-OLED Displays", "Qualcomm Snapdragon XR2+ Gen 2", "Multi-Modal Hand & Eye Tracking", "Gemini Ultra Multimodal"],
    active_feature: "Spatial Passthrough Mesh Anchor Active",
    telemetry: { ppi: 3500, tracking_cameras: 12, fov_deg: 110 }
  }
};

export default function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, OPTIONS");
  res.setHeader("Cache-Control", "no-cache, no-store, must-revalidate");

  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  return res.status(200).json({
    success: true,
    devices: samsungDevices,
    ecosystem_status: "All 15 Samsung Flagship Products & AI Projects Synchronized"
  });
}
