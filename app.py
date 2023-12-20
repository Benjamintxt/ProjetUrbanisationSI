import json
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook/', methods=['POST'])
def webhook_handler():
    try:
        # Get the JSON data from the request
        json_data = request.get_json()

        # Save the JSON data to a file (you can customize the filename and path)
        with open('webhook_data.json', 'w') as file:
            file.write(json.dumps(json_data, indent=2))  # Convert to JSON string with indentation

        return jsonify({'message': 'Webhook data saved successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
