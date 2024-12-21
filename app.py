from flask import Flask, request, jsonify, send_file, url_for
import os
from rembg import remove
from PIL import Image
import uuid
import base64
import json

app = Flask(__name__)

# Path to the folder where images will be saved
output_dir = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(output_dir, exist_ok=True)  # Create the folder if it doesn"t exist

# Allowed image extensions and their corresponding MIME types
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}

# Maximum allowed file size (in bytes)
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

# Check if the file extension and MIME type are allowed
def allowed_file(filename, mimetype):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS and \
           mimetype in ALLOWED_MIME_TYPES

@app.route("/remove-bg", methods=["POST"])
def remove_bg():
    # They can either send the image as a file or as a base64 string
    image_file = request.files["image"]
    image_b64 = ""

    # Check if there's a base64 image in the request
    # Check if there is a body
    if "body" in request:
        try:
            body = json.loads(request["body"])
            image_b64 = body["img_base64"]
        except (json.JSONDecodeError, TypeError):
            pass

    # Check if an image was sent in the request
    if image_file is None and image_b64 is None:
        return jsonify({"error": "No image provided"}), 400

    # Check the file extension and MIME type
    if image_file is not None:
        if not allowed_file(image_file.filename, image_file.mimetype):
            return jsonify({"error": "Format was not supported"}), 400
    
    # Check the file size
    if image_file is not None:
        file_size = os.fstat(image_file.fileno()).st_size
    else:
        file_size = len(base64.b64decode(image_b64))

    if file_size > MAX_FILE_SIZE:
        return jsonify({"error": f"The file exceeds the maximum size of {MAX_FILE_SIZE / (1024 * 1024)} MB"}), 400  

    # Open the image with PIL
    if image_file is not None:
        input_image = Image.open(image_file)
    else:
        input_image = base64.b64decode(image_b64)
    
    # Generate a unique ID for filenames
    unique_id = str(uuid.uuid4()).replace("-", "")
    
    # Create unique filenames for the original and background-removed images
    # original_filename = f"{unique_id}_original.png"
    # no_bg_filename = f"{unique_id}_no_bg.png"
    
    # Full path to save the original image
    # original_path = os.path.join(output_dir, original_filename)
    # input_image.save(original_path, format="PNG")  # Save the original image

    # Remove the background from the image
    output_image = remove(input_image)
    
    # Full path to save the background-removed image
    # no_bg_path = os.path.join(output_dir, no_bg_filename)
    # output_image.save(no_bg_path, format="PNG", optimize=True)  # Save the background-removed image with compression

    # Generate full URLs for downloading the images
    # original_image_url = request.host_url + "download/" + original_filename
    # no_bg_image_url = request.host_url + "download/" + no_bg_filename

    # return jsonify({
    #     "original_image_url": original_image_url,
    #     "no_bg_image_url": no_bg_image_url
    # })

    return {
        "headers": {
            "Content-Type": "image/png",
        },
        "statusCode": 200,
        "body": base64.b64encode(output_image).decode("utf-8"),
        "isBase64Encoded": True
    }

@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    path = os.path.join(output_dir, filename)

    if os.path.exists(path):
        return send_file(path)
    else:
        return jsonify({"error": "Path does not exist"}), 404  

if __name__ == "__main__":
    app.run(debug=True)