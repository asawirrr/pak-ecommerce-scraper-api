from flask import Flask, jsonify, request
import darazheadlesschangeforapi  # Import the refactored darazheadlesschangeforapi.py

app = Flask(__name__)


#http://127.0.0.1:5000/daraz?query=catfood
#catfood Fluffy
#http://127.0.0.1:5000/daraz?query=catfood%20Fluffy

@app.route('/daraz', methods=['GET'])
def scrape():
    try:
        # Get the query parameter from the request
        query = request.args.get('query')  # Default value if no query is provided
        if not query:
            return jsonify({"error": "No query URL provided"}), 400
        
        # Call the run_scraper function with the query parameter
        json_output = darazheadlesschangeforapi.run_scraper(query)
        
        # Return the JSON output as the Flask response
        return json_output, 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
