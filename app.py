from flask import Flask, request, jsonify, send_file, url_for
from rembg import remove
from PIL import Image
import requests
import base64
import io
from utils.authenticate import Authenticate

app = Flask(__name__)

# Allowed image extensions and their corresponding MIME types
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}

# Maximum allowed file size (in bytes)
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

# Get image data
def get_image_data(image_data, input_type):
    if input_type == "file":
        image_data = image_data.read()
    elif input_type == "base64":
        image_data = base64.b64decode(image_data)
    elif input_type == "url":
        image_data = requests.get(image_data, allow_redirects=True).content
    return image_data

# Check file size by type
def check_file_size(file):
    return len(file)

# Check if the file extension and MIME type are allowed
def allowed_file(filename, mimetype):
    return "." in filename and \
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS and \
        mimetype in ALLOWED_MIME_TYPES

@app.route("/remove-bg", methods=["POST"])
def remove_bg():
    # Authenticate the user
    api_key = request.headers.get("x-api-key")
    authenticated = Authenticate(api_key)

    # If the user is not authenticated, return an error
    if authenticated == False:
        return jsonify({"error": "Unauthorized"}), 401

    image_data = None;
    input_type = ""

    # Check if the image was provided as a file
    if request.files:
        image_data = request.files["image"]
        input_type = "file"

    # If the image was not provided as a file, check if it was provided as a base64 string
    if request.form and "img_base64" in request.form:
        image_data = request.form.get("img_base64")
        input_type = "base64"

    # Check if there's a URL
    if request.form and "img_url" in request.form:
        image_data = request.form.get("img_url")
        input_type = "url"

    # Check if an image was provided either as a file or base64 string
    if image_data is None or type(image_data) == str and image_data == "":
        return jsonify({"error": "No image data provided"}), 400
    
    # Check the file extension and MIME type
    if input_type == "file":
        if not allowed_file(image_data.filename, image_data.mimetype):
            return jsonify({"error": "Image Format is not supported"}), 400
        
    # Open the image with PIL
    input_image = get_image_data(image_data, input_type)
        
    # Check the file size
    file_size = check_file_size(input_image)

    # If the file size exceeds the maximum limit, return an error
    if file_size > MAX_FILE_SIZE:
        return jsonify({"error": f"The file data exceeds the maximum size of {MAX_FILE_SIZE / (1024 * 1024)} MB"}), 400  
    
    # Remove the background from the image
    output_image = remove(input_image)

    # Create BytesIO object to handle the image data
    img_io = io.BytesIO()
    img_io.write(output_image)
    img_io.seek(0)

    # Return the image direct
    return send_file(img_io, mimetype='image/png')

@app.route("/")
def index():
    return jsonify({"message": "REMBG is up and ready!", "success": True})

if __name__ == "__main__":
    app.run(debug=True)