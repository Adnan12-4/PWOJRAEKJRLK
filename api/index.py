import json, os
from datetime import datetime
from http.server import BaseHTTPRequestHandler

# -----------------------
# CONFIG
# -----------------------
DATA_PATH = os.path.join(os.path.dirname(__file__), "data.json")

# -----------------------
# UTILS
# -----------------------
def safe_load(default):
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w") as f:
            json.dump(default, f, indent=2)
        return default
    try:
        with open(DATA_PATH) as f:
            return json.load(f)
    except Exception:
        with open(DATA_PATH, "w") as f:
            json.dump(default, f, indent=2)
        return default

def safe_save(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

# -----------------------
# INITIAL DATA TEMPLATE
# -----------------------
def get_default_data():
    return {
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
        ],
        "logs": []
    }

# -----------------------
# MAIN HTTP HANDLER
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
        db = safe_load(get_default_data())
        body = json.dumps(db, indent=2)
        self._set_headers(200)
        self.wfile.write(body.encode("utf-8"))

    def do_POST(self):
        db = safe_load(get_default_data())
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
            db["decks"].append({
                "name": deck,
                "updated": str(datetime.now().date()),
                "cards": []
            })
            safe_save(db)
            msg = {"ok": True, "message": f"Deck '{deck}' added"}

        elif action == "addCard":
            deck_name = body.get("deck")
            for d in db["decks"]:
                if d["name"] == deck_name:
                    d["cards"].append({"front": body.get("front"), "back": body.get("back")})
                    d["updated"] = str(datetime.now().date())
                    safe_save(db)
                    msg = {"ok": True, "message": "Card added"}
                    break
            else:
                msg = {"ok": False, "error": "Deck not found"}

        elif action == "logProgress":
            db["logs"].append({
                "timestamp": datetime.now().isoformat(),
                "user": body.get("user", "anon"),
                "deck": body.get("deck", ""),
                "action": body.get("action", ""),
                "notes": body.get("notes", "")
            })
            safe_save(db)
            msg = {"ok": True, "message": "Progress logged"}

        self._set_headers(200)
        self.wfile.write(json.dumps(msg, indent=2).encode("utf-8"))
