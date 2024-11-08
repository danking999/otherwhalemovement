from flask import Flask, request, jsonify, render_template_string
import re
import logging
import sys
import json
from datetime import datetime, timedelta

app = Flask(__name__)

# Set up basic logging
logging.basicConfig(level=logging.INFO)

# Store alerts with timestamps
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
    current_time = datetime.utcnow()
    
    # Keep all alerts less than 8 hours old, remove older ones
    recent_alerts = []
    for alert in whale_alerts:
        alert_time = datetime.strptime(alert['timestamp'], '%Y-%m-%d %H:%M:%S')
        if current_time - alert_time <= timedelta(hours=8):
            recent_alerts.append(alert)
    
    # Update whale_alerts to only keep alerts < 8 hours old
    whale_alerts.clear()
    whale_alerts.extend(recent_alerts)
    
    if not whale_alerts:
        return jsonify({"message": "No whale alerts yet"})
    
    return jsonify(whale_alerts)

# Webhook route to receive alerts
@app.route('/webhook', methods=['POST'])
def handle_webhook():
    try:
        data = request.get_json()
    except:
        try:
            data = json.loads(request.data)
        except:
            data = {"raw_data": str(request.data)}
    
    # Add timestamp as string
    data['timestamp'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    
    # This cleanup happens every time a new alert comes in
    current_time = datetime.utcnow()
    recent_alerts = []
    for alert in whale_alerts:
        alert_time = datetime.strptime(alert['timestamp'], '%Y-%m-%d %H:%M:%S')
        if current_time - alert_time <= timedelta(hours=8):  # Only keeps alerts < 8 hours old
            recent_alerts.append(alert)
    
    whale_alerts.clear()
    whale_alerts.extend(recent_alerts)
    whale_alerts.append(data)  # Add the new alert
    
    return jsonify(data), 200

if __name__ == '__main__':
    app.run(debug=True)
