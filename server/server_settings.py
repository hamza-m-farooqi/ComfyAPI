import os

# get base directory of , like the directory of project

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LORA_DOWNLOAD_DIR = "/workspace/ComfyUI/models/loras"

IDLE_TIME_IN_SECONDS = int(os.environ.get("IDLE_TIME_IN_SECONDS", 300))

# Backend API settings
BACKEND_API_URL = os.environ.get("BACKEND_API_URL")
POLLING_INTERVAL = int(os.environ.get("POLLING_INTERVAL", 1))


RUNPOD_POD_ID = os.environ.get("RUNPOD_POD_ID")
RUNPOD_API_KEY = os.environ.get("RUNPOD_API_KEY")

DIGITAL_OCEAN_ENDPOINT_URL = os.environ.get("DIGITAL_OCEAN_ENDPOINT_URL")
DIGITAL_OCEAN_BUCKET_ACCESS_KEY = os.environ.get("DIGITAL_OCEAN_BUCKET_ACCESS_KEY")
DIGITAL_OCEAN_BUCKET_SECRET_KEY = os.environ.get("DIGITAL_OCEAN_BUCKET_SECRET_KEY")
DIGITAL_OCEAN_BUCKET_NAME = os.environ.get("DIGITAL_OCEAN_BUCKET_NAME")
DIGITAL_OCEAN_BUCKET_URL = os.environ.get("DIGITAL_OCEAN_BUCKET_URL")
