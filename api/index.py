import json
from datetime import datetime

# -----------------------
# In-memory data store
# -----------------------
DATA = {
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
# Main Vercel-compatible handler
# -----------------------
def handler(event, context):
    method = event.get("httpMethod", "GET")
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
    }

    # --- OPTIONS ---
    if method == "OPTIONS":
        return {"statusCode": 204, "headers": headers}

    # --- GET (return decks) ---
    if method == "GET":
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(DATA, indent=2)
        }

    # --- POST (actions) ---
    if method == "POST":
        try:
            body = json.loads(event.get("body", "{}"))
        except Exception:
            body = {}

        action = body.get("action", "")
        msg = {"ok": False, "error": "Unknown action"}

        if action == "addDeck":
            deck = body.get("deck", "Untitled")
            DATA["decks"].append({
                "name": deck,
                "updated": str(datetime.now().date()),
                "cards": []
            })
            msg = {"ok": True, "message": f"Deck '{deck}' added"}

        elif action == "addCard":
            deck_name = body.get("deck")
            for d in DATA["decks"]:
                if d["name"] == deck_name:
                    d["cards"].append({
                        "front": body.get("front"),
                        "back": body.get("back")
                    })
                    d["updated"] = str(datetime.now().date())
                    msg = {"ok": True, "message": "Card added"}
                    break
            else:
                msg = {"ok": False, "error": "Deck not found"}

        elif action == "logProgress":
            DATA["logs"].append({
                "timestamp": datetime.now().isoformat(),
                "user": body.get("user", "anon"),
                "deck": body.get("deck", ""),
                "action": body.get("action", ""),
                "notes": body.get("notes", "")
            })
            msg = {"ok": True, "message": "Progress logged"}

        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(msg, indent=2)
        }

    # --- Unsupported ---
    return {
        "statusCode": 405,
        "headers": headers,
        "body": json.dumps({"error": "Method not allowed"})
    }
