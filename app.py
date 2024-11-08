from flask import Flask, request, jsonify, render_template_string
import re
import logging

app = Flask(__name__)

# Set up basic logging
logging.basicConfig(level=logging.INFO)

# Store alerts in memory (just for this session)
whale_alerts = []

# Helper function to shorten addresses for social media
def shorten_address(address):
    return f"{address[:5]}...{address[-4:]}"

# Function to format the message for both website and social media
def format_message(data):
    coin_symbol = f"#{data['currency'].upper()}"
    blockchain = f"#{data['blockchain'].lower()}"

    website_message = f"🐋 Whale Movement Alert: {data['target_value']} {coin_symbol} ({data['value']} USD) was transferred from {data['from']} to {data['to']} {blockchain}"
    social_message = f"🐋 Whale Movement Alert: {data['target_value']} {coin_symbol} ({data['value']} USD) was transferred from {shorten_address(data['from'])} to {shorten_address(data['to'])} {blockchain}"

    return {
        "website_message": website_message,
        "social_message": social_message
    }

# Root route to display alerts
@app.route('/')
def index():
    if whale_alerts:
        # HTML to display whale alerts
        alerts_html = "<br>".join(whale_alerts)
        return render_template_string(f"<h1>Whale Movement Alerts</h1><p>{alerts_html}</p>")
    else:
        return "No whale alerts yet."

# Webhook route to receive alerts
@app.route('/webhook', methods=['POST'])
def handle_webhook():
    # Print raw request data
    print("Received webhook data:", request.data)
    
    # Get and print JSON data
    data = request.get_json()
    print("Parsed JSON data:", data)
    
    return jsonify(data), 200

if __name__ == '__main__':
    app.run(debug=True)
