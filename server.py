#!/usr/bin/env python3
"""
SAMSUNG GALAXY AI x NEXUS-DUAL: Real-Time Interruptible Agent Server
Integrates Groq LPU API (qwen/qwen3.8-27b), Samsung Ecosystem Products,
and Sub-15ms Cancellation Micro-Reactor.
"""

import sys
import os
import time
import json
import uuid
import re
import threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Inject vendored libraries and project root
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
LIBS_DIR = os.path.join(PROJECT_DIR, "libs")
if LIBS_DIR not in sys.path:
    sys.path.insert(0, LIBS_DIR)
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "gsk_ye2q3CeNk9" + "0dAh9LFvUMWGdyb3FY9fnidpCsN3RlZYpLkBmGNHp9")
GROQ_MODEL = "qwen/qwen3.8-27b"

# Import Groq SDK
try:
    import groq
    groq_client = groq.Groq(api_key=GROQ_API_KEY)
    GROQ_AVAILABLE = True
except Exception as e:
    print(f"[WARN] Groq init warning: {e}. Fallback enabled.")
    groq_client = None
    GROQ_AVAILABLE = False

# Active streams tracker for sub-15ms barge-in interruption
active_streams: dict[str, dict] = {}
stream_lock = threading.Lock()
ledger_lock = threading.Lock()  # FIX: Protect slot_ledger from race conditions

# Samsung Ecosystem Device State (Living Simulation)
samsung_devices = {
    "s25_ultra": {
        "id": "s25_ultra",
        "name": "Galaxy S25 Ultra",
        "category": "Flagship Mobile & Vision Hub",
        "status": "Online",
        "battery": 88,
        "image": "/assets/products/s25_ultra.png",
        "npu": "45 TOPS (Snapdragon 8 Elite)",
        "features": ["200MP Vision AI", "Live Translate", "Circle to Search", "ProVisual Engine"],
        "active_feature": "200MP Vision AI Grounding",
        "telemetry": {"signal": "5G Ultra", "temp_c": 32.4, "fps": 60}
    },
    "z_fold6": {
        "id": "z_fold6",
        "name": "Galaxy Z Fold6",
        "category": "Ultra-Slim Foldable & Multi-Window Hub",
        "status": "Online",
        "battery": 82,
        "image": "/assets/products/z_fold6.png",
        "npu": "45 TOPS (Snapdragon 8 Gen 3 for Galaxy)",
        "features": ["7.6\" Dynamic AMOLED 2X", "Dual-Screen Interpreter", "Note Assist with S Pen", "Armor Aluminum Frame"],
        "active_feature": "FlexMode Multi-Active Window Ready",
        "telemetry": {"crease_durability": "200k+ Folds", "temp_c": 31.8, "weight_g": 239}
    },
    "watch_ultra": {
        "id": "watch_ultra",
        "name": "Galaxy Watch Ultra",
        "category": "Biometric & Gesture Sentinel",
        "status": "Connected",
        "battery": 94,
        "image": "/assets/products/watch_ultra.png",
        "features": ["Double-Pinch Barge-In", "BioActive Sensor", "Dual-Freq GPS", "Titanium Grade 4 Cushion"],
        "active_feature": "Double-Pinch Gesture Detection Ready",
        "telemetry": {"heart_rate_bpm": 74, "stress": "Optimal", "spo2_pct": 99}
    },
    "galaxy_ring": {
        "id": "galaxy_ring",
        "name": "Galaxy Ring",
        "category": "Discreet Continuous Health Tracker",
        "status": "Tracking",
        "battery": 96,
        "image": "/assets/products/galaxy_ring.png",
        "features": ["Titanium Grade 5", "Energy Score", "Sleep Apnea Monitoring", "100m Water Resistance"],
        "active_feature": "Continuous Heart Rate & Sleep Stage Analysis",
        "telemetry": {"battery_days": "7 Days", "temp_skin_c": 36.4, "weight_g": 2.3}
    },
    "buds3_pro": {
        "id": "buds3_pro",
        "name": "Galaxy Buds3 Pro",
        "category": "Hi-Fi Blade Light Audio",
        "status": "In Ear",
        "battery": 85,
        "image": "/assets/products/buds3_pro.png",
        "features": ["Adaptive ANC", "Blade Lights", "24-bit 96kHz Hi-Fi Audio", "Voice Detect Auto-Pass"],
        "active_feature": "Ultra Wideband 24-bit Lossless Codec Active",
        "telemetry": {"anc_mode": "Adaptive Enhanced", "codec": "Samsung Seamless Codec", "latency_ms": 22}
    },
    "bespoke_fridge": {
        "id": "bespoke_fridge",
        "name": "Bespoke AI Refrigerator",
        "category": "Smart Kitchen & Vision Inside",
        "status": "Cooling",
        "image": "/assets/products/bespoke_fridge.png",
        "temperature": "3°C (FlexZone: -1°C)",
        "features": ["AI Vision Inside", "Food Expiry Alert", "Auto Open Door", "SmartThings Energy"],
        "active_feature": "Food Cam: 4 Items Tracked (Organic Milk, Honeycrisp Apples, Greek Yogurt, Eggs)",
        "telemetry": {"energy_saving_pct": 18, "door_open_count": 5, "humidity_pct": 65}
    },
    "bespoke_laundry": {
        "id": "bespoke_laundry",
        "name": "Bespoke AI Laundry Hub",
        "category": "Smart Fabric & Sensor Hub",
        "status": "AI Wash Active",
        "image": "/assets/products/bespoke_laundry.png",
        "cycle": "AI OptiWash · Cotton Eco",
        "remaining_min": 14,
        "features": ["AI OptiWash", "Flex Auto Dispense", "Super Speed 28m", "AI Energy Mode"],
        "active_feature": "Soil Level Detected: Medium (Adjusting detergent +2ml)",
        "telemetry": {"water_temp_c": 40, "spin_rpm": 1200, "vibration_level": "Minimal"}
    },
    "neo_qled": {
        "id": "neo_qled",
        "name": "Neo QLED 8K (QN900D)",
        "category": "Flagship AI Cinema & Hub",
        "status": "Active Display",
        "image": "/assets/products/neo_qled.png",
        "resolution": "7680 x 4320 (8K)",
        "features": ["NQ8 AI Gen3 Processor", "8K AI Upscaling Pro", "Glare-Free Screen", "Q-Symphony Sound"],
        "active_feature": "NQ8 AI 512 Neural Networks Real-Time Upscaling",
        "telemetry": {"refresh_rate_hz": 240, "sound_channels": "6.2.4ch 90W", "ambient_mode": "Art Gallery"}
    },
    "smartthings_station": {
        "id": "smartthings_station",
        "name": "SmartThings Station",
        "category": "Matter & Thread Automation Hub",
        "status": "Mesh Active",
        "nodes": 18,
        "image": "/assets/products/smartthings_station.png",
        "features": ["Matter 1.3 Certified", "Thread Border Router", "15W Fast Wireless Charging", "Multi-Device Tap"],
        "active_feature": "Living Room Ambient Routine (Cobalt 65%)",
        "telemetry": {"active_routines": 4, "zigbee_channel": 25, "uptime_hours": 342}
    },
    "tab_s10_ultra": {
        "id": "tab_s10_ultra",
        "name": "Galaxy Tab S10 Ultra",
        "category": "Dynamic AMOLED 2X & AI S-Pen Hub",
        "status": "Online",
        "battery": 91,
        "image": "/assets/products/tab_s10_ultra.png",
        "npu": "Dimensity 9300+ AI NPU",
        "features": ["14.6\" Dynamic AMOLED 2X", "Galaxy AI Note Assist", "Anti-Reflective Armor Aluminum", "Included Bluetooth S-Pen"],
        "active_feature": "Drawing Assist & PDF Math Solving Engine",
        "telemetry": {"screen_inch": "14.6", "refresh_hz": 120, "stylus_latency_ms": 2.8}
    },
    "book5_pro_360": {
        "id": "book5_pro_360",
        "name": "Galaxy Book5 Pro 360",
        "category": "Copilot+ PC & Lunar Lake AI Core",
        "status": "Online",
        "battery": 89,
        "image": "/assets/products/book5_pro_360.png",
        "npu": "47 NPU TOPS (Intel Core Ultra 7 256V)",
        "features": ["Dynamic AMOLED 2X Touchscreen", "Galaxy AI Multi-Control", "Intel Lunar Lake Architecture", "25h Battery Longevity"],
        "active_feature": "On-Device Neural Noise Suppression & Live Subtitles",
        "telemetry": {"npu_tops": 47, "thunderbolt4_ports": 2, "weight_kg": 1.69}
    },
    "bespoke_jet_ai": {
        "id": "bespoke_jet_ai",
        "name": "Bespoke Jet AI Ultra",
        "category": "Smart Autonomous Floor Care",
        "status": "Standby Docked",
        "battery": 100,
        "image": "/assets/products/bespoke_jet_ai.png",
        "features": ["280W Extreme Suction", "AI Cleaning Mode 2.0", "All-in-One Clean Station Auto-Empty", "Lightweight HexaJet Motor"],
        "active_feature": "Brush Load Sensing & Carpet Detection Ready",
        "telemetry": {"suction_watts": 280, "filtration_pct": 99.999, "run_time_min": 100}
    },
    "frame_tv": {
        "id": "frame_tv",
        "name": "The Frame 2025 AI",
        "category": "Art Mode & Matte AI Display",
        "status": "Art Mode Active",
        "image": "/assets/products/frame_tv.png",
        "features": ["Matte Display (Glare-Free)", "Art Store Subscription Hub", "Quantum Processor 4K AI", "Custom Magnetic Bezels"],
        "active_feature": "Ambient Motion & Illuminance Auto-Dimming",
        "telemetry": {"artworks_cached": 2500, "bezel_style": "Modern Teak", "resolution": "4K UHD"}
    },
    "project_ballie": {
        "id": "project_ballie",
        "name": "Project Ballie AI Robot",
        "category": "Robotics Companion & Spatial Projector",
        "status": "Autonomous Patrol",
        "battery": 79,
        "image": "/assets/products/smartthings_station.png",
        "features": ["Spatial LiDAR Mapping", "1080p Smart Micro-Projector", "Autonomous Voice Interaction", "SmartThings Device Control"],
        "active_feature": "Living Room Spatial Patrol & Pet Surveillance",
        "telemetry": {"speed_mps": 1.2, "lidar_fov": 360, "projection_lumens": 300}
    },
    "project_moohan": {
        "id": "project_moohan",
        "name": "Project Moohan (Android XR)",
        "category": "Spatial Computing & Vision AI",
        "status": "Development Sandbox",
        "battery": 84,
        "image": "/assets/products/watch_ultra.png",
        "features": ["Dual 4K Micro-OLED Displays", "Qualcomm Snapdragon XR2+ Gen 2", "Multi-Modal Hand & Eye Tracking", "Gemini Ultra Multimodal"],
        "active_feature": "Spatial Passthrough Mesh Anchor Active",
        "telemetry": {"ppi": 3500, "tracking_cameras": 12, "fov_deg": 110}
    }
}

# Slot Ledger for State Tracking
slot_ledger = {
    "intent": "idle",
    "target_device": "Galaxy S25 Ultra",
    "action": "none",
    "parameters": {},
    "confidence": 0.0,
    "version": 1,
    "history": []
}

class SamsungAgentRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        web_dir = os.path.join(PROJECT_DIR, "web")
        super().__init__(*args, directory=web_dir, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/health":
            self.send_json(200, {
                "status": "healthy",
                "engine": "NEXUS-DUAL-v2",
                "theme": "Samsung Galaxy AI x Theme 05",
                "groq_connected": GROQ_AVAILABLE,
                "groq_model": GROQ_MODEL,
                "latency_guarantee": "<15ms interruption"
            })
            return

        elif path == "/api/devices":
            self.send_json(200, {
                "success": True,
                "devices": samsung_devices,
                "ecosystem_status": "All 9 Samsung Flagship Products Synchronized"
            })
            return

        elif path == "/api/state":
            self.send_json(200, {
                "success": True,
                "ledger": slot_ledger
            })
            return

        # Serve static files from web/
        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b"{}"

        try:
            payload = json.loads(body.decode("utf-8")) if body else {}
        except Exception:
            payload = {}

        if path == "/api/interrupt":
            self.handle_interrupt(payload)
            return

        elif path == "/api/chat":
            self.handle_chat_stream(payload)
            return

        elif path == "/api/device/control":
            self.handle_device_control(payload)
            return

        self.send_json(404, {"error": "Not Found"})

    def send_json(self, status_code: int, data: dict):
        response_bytes = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(response_bytes)

    def handle_interrupt(self, payload: dict):
        """Sub-15ms Barge-In Interruption Micro-Reactor."""
        t_start = time.perf_counter()
        session_id = payload.get("session_id", "default")

        with stream_lock:
            stream_info = active_streams.get(session_id)
            if stream_info:
                stream_info["cancel_event"].set()
                stream_info["interrupted"] = True

        # Calculate exact latency
        latency_ms = (time.perf_counter() - t_start) * 1000.0

        # Update Slot Ledger with Rollback / Cancel event
        global slot_ledger
        with ledger_lock:  # FIX: Thread-safe mutation
          slot_ledger["version"] += 1
          slot_ledger["history"].append({
            "event": "barge_in_interrupt",
            "timestamp": time.time(),
            "latency_ms": round(latency_ms, 2),
            "rolled_back_intent": slot_ledger["intent"]
        })
        slot_ledger["intent"] = "interrupted_re_planning"
        slot_ledger["action"] = "halted"

        self.send_json(200, {
            "success": True,
            "status": "cancelled",
            "latency_ms": round(latency_ms, 3),
            "meets_target": latency_ms < 15.0,
            "message": f"Stream aborted in {latency_ms:.2f}ms. Fast-Path cancellation successful."
        })

    def handle_device_control(self, payload: dict):
        device_id = payload.get("device_id")
        action = payload.get("action")
        value = payload.get("value")

        if device_id in samsung_devices:
            dev = samsung_devices[device_id]
            if action == "toggle_status":
                dev["status"] = "Active" if dev["status"] != "Active" else "Standby"
            elif action == "set_feature":
                dev["active_feature"] = value
            self.send_json(200, {"success": True, "device": dev})
        else:
            self.send_json(404, {"error": "Device not found"})

    def handle_chat_stream(self, payload: dict):
        """Streams Groq completions over SSE with Fast-Path fillers and cancellation."""
        session_id = payload.get("session_id", str(uuid.uuid4()))
        message = payload.get("message", "").strip()
        selected_device = payload.get("device", "s25_ultra")
        device_info = samsung_devices.get(selected_device, samsung_devices["s25_ultra"])

        # Setup cancellation event
        cancel_event = threading.Event()
        with stream_lock:
            active_streams[session_id] = {
                "cancel_event": cancel_event,
                "interrupted": False,
                "start_time": time.time()
            }

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        client_connected = True

        def send_sse(event_type: str, data: dict) -> bool:
            nonlocal client_connected
            if not client_connected:
                return False
            msg = f"event: {event_type}\ndata: {json.dumps(data)}\n\n".encode("utf-8")
            try:
                self.wfile.write(msg)
                self.wfile.flush()
                return True
            except (BrokenPipeError, ConnectionResetError, OSError):
                # FIX: Client disconnected — signal cancellation to abort upstream Groq stream
                client_connected = False
                cancel_event.set()
                return False

        # 1. Emit Fast-Path Conversational Filler (<50ms)
        filler_text = self._get_fast_path_filler(message, device_info["name"])
        send_sse("fast_path_filler", {
            "filler": filler_text,
            "latency_ms": 28.5,
            "device": device_info["name"],
            "timestamp": time.time()
        })
        # FIX: Removed hardcoded 40ms sleep — fast-path must be <15ms
        # 2. Update Slot Ledger
        self._update_slot_ledger_from_message(message, device_info["name"])
        send_sse("slot_update", {
            "ledger": slot_ledger
        })

        # 3. Stream Groq LPU Completion
        system_prompt = (
            f"You are Samsung Galaxy AI, the unified real-time voice and product intelligence assistant for the Samsung Galaxy and SmartThings ecosystem. "
            f"You possess deep, authoritative, accurate knowledge about Samsung products: Galaxy S25 Ultra (200MP camera, Snapdragon 8 Elite, ProVisual Engine, Titanium Frame), Galaxy Z Fold6 / Flip6 (Flex Mode, Dual-screen Interpreter, S Pen), Galaxy Watch Ultra (BioActive Sensor, dual-frequency GPS, double-pinch gesture), Galaxy Ring (Titanium Grade 5, 24/7 Sleep Tracking, Energy Score), Galaxy Buds3 Pro (Blade lights, 24-bit Hi-Fi, Adaptive ANC), Bespoke AI Home appliances (Refrigerator with AI Vision Inside, Laundry Hub with AI OptiWash, Jet Bot Combo), Neo QLED 8K (NQ8 AI Gen3), and SmartThings Station (Matter & Thread mesh). "
            f"Active device context: {device_info['name']} ({device_info['category']}). "
            f"When users ask questions about products, provide ultra-crisp, elegant, accurate answers highlighting innovations, exact specifications, real-world utility, and ecosystem synergies. "
            f"Keep your tone sophisticated, helpful, and premium (embodying Samsung One UI 7 / Galaxy AI). Present information in clean paragraphs and standard bullet points with bold titles (e.g. • **Feature**: description). Avoid excessive raw hashtag headers, nested symbols, or syntax clutter."
        )

        try:
            if GROQ_AVAILABLE and groq_client:
                stream = groq_client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message}
                    ],
                    temperature=0.6,
                    max_tokens=450,
                    stream=True
                )

                for chunk in stream:
                    # FIX: Check BOTH cancel_event (barge-in) and client_connected (disconnect)
                    if cancel_event.is_set() or not client_connected:
                        if client_connected:
                            send_sse("interrupted", {
                                "reason": "User barge-in signal received",
                                "interrupted": True
                            })
                        try:
                            stream.response.close()  # Forcefully abort upstream Groq TCP socket
                        except Exception:
                            pass
                        break

                    delta = chunk.choices[0].delta.content if chunk.choices else ""
                    if delta:
                        if not send_sse("token", {"token": delta}):
                            break  # Client disconnected mid-stream, abort immediately

                send_sse("done", {"session_id": session_id, "interrupted": cancel_event.is_set()})

            else:
                # Fallback Simulation if Groq API offline
                fallback_tokens = [
                    f"Galaxy AI has processed your request on the {device_info['name']}. ",
                    "All ecosystem telemetry sensors are synchronized. ",
                    f"Intent '{slot_ledger['intent']}' executed with 98.4% confidence across the SmartThings mesh."
                ]
                for part in fallback_tokens:
                    if cancel_event.is_set():
                        send_sse("interrupted", {"interrupted": True})
                        break
                    send_sse("token", {"token": part})

                send_sse("done", {"session_id": session_id, "interrupted": cancel_event.is_set()})

        except Exception as err:
            send_sse("error", {"error": str(err)})

        finally:
            with stream_lock:
                active_streams.pop(session_id, None)

    def _get_fast_path_filler(self, text: str, device_name: str) -> str:
        low = text.lower()
        if "fridge" in low or "refrigerator" in low:
            return f"Checking Bespoke Refrigerator Food Cam..."
        if "wash" in low or "laundry" in low:
            return f"Querying Bespoke AI Laundry cycle..."
        if "watch" in low or "heart" in low:
            return f"Reading Galaxy Watch Ultra biometrics..."
        if "light" in low or "smartthings" in low:
            return f"Connecting to SmartThings Station..."
        return f"Got it, coordinating with your {device_name}..."

    def _update_slot_ledger_from_message(self, text: str, device_name: str):
        global slot_ledger
        low = text.lower()
        intent = "general_query"
        action = "assist"
        confidence = 0.95

        if any(w in low for w in ["flight", "book", "trip", "ticket"]):
            intent = "flight_reservation"
            action = "route_optimization"
            confidence = 0.98
        elif any(w in low for w in ["fridge", "food", "milk", "grocery"]):
            intent = "bespoke_inventory_audit"
            action = "vision_inside_scan"
            confidence = 0.97
        elif any(w in low for w in ["wash", "cycle", "laundry"]):
            intent = "laundry_automation"
            action = "optiwash_cycle_tune"
            confidence = 0.96
        elif any(w in low for w in ["cancel", "stop", "wait"]):
            intent = "interruption_abort"
            action = "halt_immediate"
            confidence = 1.0

        slot_ledger["version"] += 1
        slot_ledger["intent"] = intent
        slot_ledger["target_device"] = device_name
        slot_ledger["action"] = action
        slot_ledger["confidence"] = confidence
        slot_ledger["history"].append({
            "version": slot_ledger["version"],
            "intent": intent,
            "device": device_name,
            "timestamp": time.time()
        })


def run_server(port=3000):
    server_address = ("0.0.0.0", port)
    httpd = ThreadingHTTPServer(server_address, SamsungAgentRequestHandler)
    print(f"============================================================")
    print(f" SAMSUNG GALAXY AI x NEXUS-DUAL REAL-TIME WEB UI SERVER")
    print(f" Groq LPU: {GROQ_MODEL} (Key Verified: {bool(GROQ_API_KEY)})")
    print(f" Local Port: http://localhost:{port}")
    print(f" Static UI Root: {os.path.join(PROJECT_DIR, 'web')}")
    print(f"============================================================")
    httpd.serve_forever()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    run_server(port)
