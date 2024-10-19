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
    try:
        # Get the data from the webhook
        data = request.get_json()

        # Log the incoming data for debugging
        logging.info(f"Received webhook data: {data}")

        # If this is a confirmation or verification message, return 200 OK
        if data and 'Confirmation message' in data['message']:
            logging.info(f"Received verification message: {data}")
            return jsonify({"status": "success", "message": "Webhook verified"}), 200

        # Check if it's a whale alert
        if data and data.get('type') == 'whale':
            formatted_messages = format_message(data)
            
            # Store the website message in memory (latest first)
            whale_alerts.insert(0, formatted_messages['website_message'])
            
            # Trim the list if it gets too large (limit to last 10 alerts)
            if len(whale_alerts) > 20:
                whale_alerts.pop()

            return jsonify({
                "status": "success",
                "website_message": formatted_messages['website_message'],
                "social_message": formatted_messages['social_message']
            }), 200
        else:
            logging.warning(f"Ignored non-whale alert: {data}")
            return jsonify({"status": "ignored", "reason": "Not a whale alert"}), 400
    except Exception as e:
        logging.error(f"Error processing webhook: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
