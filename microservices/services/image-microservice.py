import io
import json
import zmq
import requests

from PIL import Image, ImageEnhance

context = zmq.Context()

socket = context.socket(zmq.REP)
socket.bind("tcp://*:7050")

print("ImageScraper Microservice running on tcp://localhost:7050")


def download_image(url):
    headers = {"user-agent": "image-scraper-microservice.py/0.0.1"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("REQUEST FAILED: ", response.status_code)
        raise Exception("Failed to download image.")
    image_data = io.BytesIO(response.content)
    return Image.open(image_data)


def apply_crop(image, edit):
    left = edit.get("left", 0)
    top = edit.get("top", 0)
    right = edit.get("right", 0)
    bottom = edit.get("bottom", 0)
    width, height = image.size
    return image.crop((left, top, width - right, height - bottom))


def apply_brightness(image, edit):
    value = edit.get("value", 1.0)
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(value)


def apply_contrast(image, edit):
    value = edit.get("value", 1.0)
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(value)


def apply_saturation(image, edit):
    value = edit.get("value", 1.0)
    enhancer = ImageEnhance.Color(image)
    return enhancer.enhance(value)


def parse_request(request_data):
    url = request_data["url"]
    image = download_image(url)
    edits = request_data.get("image-edits", [])
    output_format = request_data.get("output_format", "PNG")
    return image, edits, output_format


def apply_edits(image, edits):
    for edit in edits:
        edit_type = edit.get("type", "").lower()
        if edit_type == "crop":
            image = apply_crop(image, edit)
        elif edit_type == "brightness":
            image = apply_brightness(image, edit)
        elif edit_type == "contrast":
            image = apply_contrast(image, edit)
        elif edit_type == "saturation":
            image = apply_saturation(image, edit)
    return image


def serialize_output(image, output_format):
    output_buffer = io.BytesIO()
    image.save(output_buffer, format=output_format)
    image_bytes = output_buffer.getvalue()

    metadata = {
        "status": "success",
        "format": output_format,
        "size_bytes": len(image_bytes),
    }
    return metadata, image_bytes


def process_image(request_data):
    image, edits, output_format = parse_request(request_data)
    image = apply_edits(image, edits)
    return serialize_output(image, output_format)


# MAIN MICROSERVICE LOOP #
while True:
    try:
        request_data = socket.recv_json()
        print(f"Image Request Recieved:\n{request_data}")
        metadata, image_bytes = process_image(request_data)
        socket.send_multipart([json.dumps(metadata).encode(), image_bytes])
    except Exception as error:
        metadata = {"status": "error", "message": str(error)}
        socket.send_multipart([json.dumps(metadata).encode(), b""])
