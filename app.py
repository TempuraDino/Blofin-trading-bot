from flask import Flask, request, jsonify
import hmac, hashlib, time, requests, os

app = Flask(__name__)

API_KEY = os.getenv("BLOFIN_API_KEY")
SECRET_KEY = os.getenv("BLOFIN_SECRET_KEY")
PASSPHRASE = os.getenv("BLOFIN_PASSPHRASE")
BASE_URL = "https://openapi.blofin.com"

def sign_request(timestamp, method, request_path, body=""):
    message = f"{timestamp}{method}{request_path}{body}"
    signature = hmac.new(
        SECRET_KEY.encode(), message.encode(), hashlib.sha256
    ).hexdigest()
    return signature

def place_order(symbol, side, size):
    endpoint = "/api/v1/orders"
    url = BASE_URL + endpoint
    timestamp = str(int(time.time() * 1000))
    body = {
        "symbol": symbol,
        "side": side.upper(),  # BUY or SELL
        "type": "market",
        "size": size
    }
    body_str = str(body).replace("'", '"')
    headers = {
        "Content-Type": "application/json",
        "X-BLOFIN-APIKEY": API_KEY,
        "X-BLOFIN-SIGN": sign_request(timestamp, "POST", endpoint, body_str),
        "X-BLOFIN-TIMESTAMP": timestamp,
        "X-BLOFIN-PASSPHRASE": PASSPHRASE,
    }
    r = requests.post(url, headers=headers, data=body_str)
    return r.json()

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400
    
    symbol = data.get("symbol", "ETH-USDT")
    side = data.get("action", "BUY")
    size = data.get("size", 0.01)

    order = place_order(symbol, side, size)
    return jsonify(order)

@app.route("/")
def home():
    return "🚀 BloFin Auto-Trader Running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
