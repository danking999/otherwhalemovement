from flask import Flask, request, jsonify
import re
import logging

app = Flask(__name__)

# Set up basic logging
logging.basicConfig(level=logging.INFO)

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

# Root route to indicate the app is running
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        logging.warning('POST request made to root endpoint. This should be redirected to /webhook.')
        return jsonify({"status": "error", "message": "POST request to the wrong endpoint. Use /webhook."}), 405
    return "Whale Movement Alert app is running!"

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    try:
        # Get the data from the webhook
        data = request.get_json()

        # Log the incoming data for debugging
        logging.info(f"Received webhook data: {data}")

        # If this is a confirmation or verification message, always return 200 OK
        if data and 'Confirmation message' in data['message']:
            logging.info(f"Received verification message: {data}")
            return jsonify({"status": "success", "message": "Webhook verified"}), 200

        # Check if it's a whale alert
        if data and data.get('type') == 'whale':
            formatted_messages = format_message(data)
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
