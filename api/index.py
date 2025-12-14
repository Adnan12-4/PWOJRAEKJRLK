import json
from http.server import BaseHTTPRequestHandler

# -----------------------
# Self-contained CyberFlash backend
# -----------------------
# All data stored in memory
data = {
    "decks": [
        {
            "name": "Network Threats",
            "updated": "2025-12-14",
            "cards": [
                {
                    "front": "Misconfigured Firewall",
                    "back": "Open ports allow intrusion → C + I → Close unused ports"
                }
            ]
        }
    ]
}
logs = []

# -----------------------
# HTTP handler
# -----------------------
class handler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(204)

    def do_GET(self):
        self._set_headers(200)
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(body)
        except Exception:
            body = {}

        action = body.get("action", "")
        msg = {"ok": False, "error": "Unknown action"}

        if action == "addDeck":
            deck = body.get("deck", "Untitled")
            data["decks"].append({
                "name": deck,
                "updated": "2025-12-14",
                "cards": []
            })
            msg = {"ok": True, "message": f"Deck '{deck}' added"}

        elif action == "addCard":
            deck_name = body.get("deck")
            for d in data["decks"]:
                if d["name"] == deck_name:
                    d["cards"].append({"front": body.get("front"), "back": body.get("back")})
                    msg = {"ok": True, "message": "Card added"}
                    break
            else:
                msg = {"ok": False, "error": "Deck not found"}

        elif action == "logProgress":
            logs.append({
                "timestamp": body.get("timestamp", "now"),
                "user": body.get("user", "anon"),
                "deck": body.get("deck", ""),
                "action": body.get("action", ""),
                "notes": body.get("notes", "")
            })
            msg = {"ok": True, "message": "Progress logged"}

        self._set_headers(200)
        self.wfile.write(json.dumps(msg).encode("utf-8"))
