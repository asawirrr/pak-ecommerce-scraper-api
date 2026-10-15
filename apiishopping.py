# apiishopping.py
from flask import Flask, jsonify, request
import newishopping  # Import the existing newishopping.py

app = Flask(__name__)

@app.route('/ishopping', methods=['GET'])
def scrape():
    # Get the query parameter from the request
    query = request.args.get('query')
    
    if not query:  # Check if the query is provided
        return jsonify({"error": "Query parameter is required"}), 400

    try:
        # Run the scraper with the given query
        json_output = newishopping.run_scraper(query)  # Call the modified function
        
        # Return the JSON output as the Flask response
        return json_output, 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
