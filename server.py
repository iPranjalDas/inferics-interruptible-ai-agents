import http.server
import socketserver
import threading
import time
import json
import uuid
import select
import os
import sys
from urllib.parse import urlparse

# Global state for managing active streams and cancellation
active_streams = {}
stream_lock = threading.Lock()

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

class StreamingHandler(http.server.SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def __init__(self, *args, **kwargs):
        web_dir = os.path.join(PROJECT_DIR, "public")
        super().__init__(*args, directory=web_dir, **kwargs)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/api/chat':
            self.handle_generate()
        elif path == '/api/interrupt':
            self.handle_cancel()
        else:
            self.send_error(404, "Not Found")

    def handle_cancel(self):
        """Endpoint to cancel an ongoing SSE stream."""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            req = json.loads(post_data.decode('utf-8'))
            stream_id = req.get("stream_id")
            
            with stream_lock:
                if stream_id in active_streams:
                    active_streams[stream_id].set()
                    found = True
                else:
                    found = False
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            resp = {"status": "cancelled" if found else "not_found"}
            self.wfile.write(json.dumps(resp).encode('utf-8'))
            
        except Exception:
            self.send_error(400, "Bad Request")

    def handle_generate(self):
        """Endpoint to start an SSE generation stream."""
        stream_id = str(uuid.uuid4())
        cancel_event = threading.Event()
        
        with stream_lock:
            active_streams[stream_id] = cancel_event

        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Connection', 'keep-alive')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('X-Accel-Buffering', 'no')
        self.end_headers()

        self.connection.setblocking(False)

        try:
            self._write_sse(f"data: {json.dumps({'stream_id': stream_id})}\\n\\n", cancel_event)
        except Exception:
            self._cleanup(stream_id)
            return

        def token_generator():
            yield "SYSTEM ONLINE."
            time.sleep(0.5)
            yield " NEURAL LINK ESTABLISHED."
            for i in range(15):
                yield f" [BLOCK_{i}]"
                time.sleep(0.05)

        try:
            for token in token_generator():
                if cancel_event.is_set():
                    self._write_sse(f"data: {json.dumps({'event': 'cancelled'})}\\n\\n", cancel_event)
                    break
                msg = f"data: {json.dumps({'text': token})}\\n\\n"
                success = self._write_sse(msg, cancel_event)
                if not success:
                    break
            else:
                self._write_sse(f"data: {json.dumps({'event': 'done'})}\\n\\n", cancel_event)
        finally:
            self._cleanup(stream_id)

    def _write_sse(self, data: str, cancel_event: threading.Event) -> bool:
        payload = data.encode('utf-8')
        total_sent = 0
        while total_sent < len(payload):
            if cancel_event.is_set():
                return False
            _, writable, _ = select.select([], [self.connection], [], 0.01)
            if not writable:
                continue
            try:
                sent = self.connection.send(payload[total_sent:])
                if sent == 0:
                    return False
                total_sent += sent
            except BlockingIOError:
                continue
            except Exception:
                return False 
        return True

    def _cleanup(self, stream_id):
        with stream_lock:
            active_streams.pop(stream_id, None)

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

if __name__ == '__main__':
    PORT = 3000
    server_address = ('', PORT)
    httpd = ThreadedHTTPServer(server_address, StreamingHandler)
    print(f"Starting INFERICS OS Backend on port {PORT}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()
