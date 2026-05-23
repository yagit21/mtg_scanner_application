from flask import Blueprint, render_template, request, jsonify
import base64
import numpy as np
from PIL import Image
import io
from ml.scripts.pipeline import scan_card

views = Blueprint("views", __name__)


@views.route("/")
def home():
    return render_template("index.html")


@views.route("/scan", methods=["POST"])
def scan():

    data = request.get_json()

    image_data = data["image"]

    #Remove base64 header
    image_data = image_data.split(",")[1]

    #Decode base64 into bytes
    image_bytes = base64.b64decode(image_data)

    #Convert bytes into PIL image
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    #Convert PIL image into NumPy array
    img = np.array(image)

    result = scan_card(img)

    return jsonify(result)