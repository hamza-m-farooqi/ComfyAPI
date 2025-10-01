import os

# get base directory of , like the directory of project

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LORA_DOWNLOAD_DIR = "/workspace/ComfyUI/models/loras"

GCLOUD_BUCKET_NAME = os.environ.get("GCLOUD_BUCKET_NAME") 
GCLOUD_STORAGE_CREDENTIALS = "gcloud-storage-credentials.json"
IDLE_TIME_IN_SECONDS = int(os.environ.get("IDLE_TIME_IN_SECONDS", 300))

# Backend API settings
BACKEND_API_URL = os.environ.get("BACKEND_API_URL")
POLLING_INTERVAL = int(os.environ.get("POLLING_INTERVAL", 1))


RUNPOD_POD_ID = os.environ.get("RUNPOD_POD_ID")
RUNPOD_API_KEY = os.environ.get("RUNPOD_API_KEY")
