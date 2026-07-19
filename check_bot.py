import requests

token = "8616936695:AAE0_6ZVbNVcrTK7tandJU-nJaM-2MTdWkM"

r = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", timeout=15)
data = r.json()

if not data.get("ok") or not data.get("result"):
    print("No updates found")
    exit()

messages = [u["message"] for u in data["result"] if "message" in u]
print(f"Total updates: {len(data['result'])}")
print(f"Messages: {len(messages)}")
print("\nLast 10 sent messages:")
for m in messages[-10:]:
    chat_id = m["chat"]["id"]
    text_preview = m.get("text", "-")[:100]
    print(f"  to={chat_id} date={m['date']} text={text_preview}")
