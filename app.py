from flask import Flask, request, jsonify
import re

app = Flask(__name__)

# Helper function to shorten addresses for social media
def shorten_address(address):
    return f"{address[:5]}...{address[-4:]}"

# Function to format the message for both website and social media
def format_message(data):
    coin_symbol = f"#{data['currency'].upper()}"
    blockchain = f"#{data['blockchain'].lower()}"

    # Full format for website
    website_message = f"🐋 Whale Movement Alert : {data['target_value']} {coin_symbol} ({data['value']} USD) was transferred from {data['from']} to {data['to']} {blockchain}"

    # Shortened format for social media
    social_message = f"🐋 Whale Movement Alert : {data['target_value']} {coin_symbol} ({data['value']} USD) was transferred from {shorten_address(data['from'])} to {shorten_address(data['to'])} {blockchain}"

    return {
        "website_message": website_message,
        "social_message": social_message
    }

# Root route to indicate the app is running
@app.route('/')
def index():
    return "Whale Movement Alert app is running!"


# Webhook route to handle incoming webhook requests
@app.route('/webhook', methods=['POST'])
def handle_webhook():
    try:
        # Get the data from the webhook
        data = request.get_json()

        # Check if it's a whale alert
        if data and data.get('type') == 'whale':
            # Format the message
            formatted_messages = format_message(data)
            
            # Return the formatted messages for now (you will integrate with your site and socials later)
            return jsonify({
                "status": "success",
                "website_message": formatted_messages['website_message'],
                "social_message": formatted_messages['social_message']
            })
        else:
            return jsonify({"status": "ignored", "reason": "Not a whale alert"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
