import os
import json
import time
import requests
from datetime import datetime
from threading import Thread
import server.server_settings as server_settings


def webhook_response(webhook_url, status, code, message, data=None):
    response_data = {
        "status": status,
        "code": code,
        "message": message,
        "data": data,
    }
    # print("Going to send data over webhook!")
    # print(response_data)
    if webhook_url and "http" in webhook_url:
        requests.post(webhook_url, json=response_data)


def is_json_compatible(value):
    try:
        json.loads(value)
        return True
    except (TypeError, ValueError):
        return False


def download_lora(lora_url, lora_name=None):
    # download url to directory /workspace/ComfyUI/models/loras/ as lora.safetensors
    try:
        if not lora_name:
            lora_name = "lora.safetensors"
        lora_path = f"{server_settings.LORA_DOWNLOAD_DIR}/{lora_name}"
        response = requests.get(lora_url)
        with open(lora_path, "wb") as file:
            file.write(response.content)
        return lora_path
    except Exception as e:
        print(f"Error downloading lora: {e}")
        return None


def delete_old_images(directory_path):
    """
    Delete image files in the specified directory that are at least 1 hour old.

    Args:
        directory_path (str): Path to the directory containing images

    Returns:
        tuple: (int, list) - Count of deleted files and list of deleted filenames
    """
    # Image file extensions to look for
    image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"]

    # Get current time
    current_time = time.time()
    one_hour_ago = current_time - (60 * 60)  # 1 hour in seconds

    deleted_count = 0
    deleted_files = []

    try:
        # Iterate through all files in the directory
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)

            # Check if it's a file and has an image extension
            if os.path.isfile(file_path) and any(
                filename.lower().endswith(ext) for ext in image_extensions
            ):
                # Get file creation time (or modification time on some systems)
                file_creation_time = os.path.getctime(file_path)

                # If file is at least 1 hour old
                if file_creation_time <= one_hour_ago:
                    # Delete the file
                    os.remove(file_path)
                    deleted_count += 1
                    deleted_files.append(filename)
                    print(
                        f"Deleted: {filename} (Created: {datetime.fromtimestamp(file_creation_time)})"
                    )

        print(f"Deleted {deleted_count} image(s) that were at least 1 hour old.")
        return deleted_count, deleted_files

    except Exception as e:
        print(f"Error: {e}")
        return 0, []
