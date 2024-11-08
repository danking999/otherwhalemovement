from flask import Flask, request, jsonify, render_template_string
import re
import logging
import sys
import json
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

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
    
    # Fix timestamp assignment
    data['timestamp'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    
    current_time = datetime.utcnow()
    recent_alerts = []
    
    # First add existing alerts that are less than 8 hours old
    for alert in whale_alerts:
        try:
            alert_time = datetime.strptime(alert['timestamp'], '%Y-%m-%d %H:%M:%S')
            if current_time - alert_time <= timedelta(hours=8):
                recent_alerts.append(alert)
        except:
            # Keep alerts with invalid timestamps to prevent data loss
            recent_alerts.append(alert)
    
    # Add new alert and update list
    recent_alerts.append(data)
    whale_alerts.clear()
    whale_alerts.extend(recent_alerts)
    
    return jsonify(data), 200

# Add cleanup function
def cleanup_old_alerts():
    current_time = datetime.utcnow()
    recent_alerts = []
    
    for alert in whale_alerts:
        try:
            alert_time = datetime.strptime(alert['timestamp'], '%Y-%m-%d %H:%M:%S')
            if current_time - alert_time <= timedelta(hours=8):
                recent_alerts.append(alert)
        except:
            recent_alerts.append(alert)
    
    whale_alerts.clear()
    whale_alerts.extend(recent_alerts)

# Set up scheduler to run cleanup every hour
scheduler = BackgroundScheduler()
scheduler.add_job(func=cleanup_old_alerts, trigger="interval", hours=1)
scheduler.start()

if __name__ == '__main__':
    app.run(debug=True)
