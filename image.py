from flask import Flask, request, Response
import requests

app = Flask(__name__)

@app.route('/proxy')
def proxy_image():
    # Original image URL
    image_url = request.args.get('url')
    if not image_url:
        return "No URL provided", 400

    # Fetch the image
    response = requests.get(image_url, stream=True)
    if response.status_code == 200:
        # Forward the response without 'Content-Disposition' header
        headers = {key: value for key, value in response.headers.items() if key.lower() != 'content-disposition'}
        return Response(response.content, headers=headers, content_type=response.headers['Content-Type'])
    else:
        return "Failed to fetch image", response.status_code

if __name__ == '__main__':
    app.run(debug=True)
