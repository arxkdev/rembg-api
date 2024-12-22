from flask import Flask, request, jsonify, send_file, url_for
from rembg import remove
from PIL import Image
import requests
import base64

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
    if image_data is None:
        return jsonify({"error": "No image provided"}), 400
    
    # Check the file extension and MIME type
    if input_type == "file":
        if not allowed_file(image_data.filename, image_data.mimetype):
            return jsonify({"error": "Format was not supported"}), 400
        
    # Open the image with PIL
    input_image = get_image_data(image_data, input_type)
        
    # Check the file size
    file_size = check_file_size(input_image, input_type)

    # If the file size exceeds the maximum limit, return an error
    if file_size > MAX_FILE_SIZE:
        return jsonify({"error": f"The file exceeds the maximum size of {MAX_FILE_SIZE / (1024 * 1024)} MB"}), 400  
    
    # Remove the background from the image
    output_image = remove(input_image)
    
    return {
        "headers": {
            "Content-Type": "image/png",
        },
        "statusCode": 200,
        "body": base64.b64encode(output_image).decode("utf-8"),
        "isBase64Encoded": True
    }

if __name__ == "__main__":
    app.run(debug=True)