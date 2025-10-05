import os
import sys
import time
import json
import signal
import runpod
import requests
import threading
from server.request_queue import InferenceRequest, Job
from server.utils import (
    webhook_response,
    download_lora,
    delete_old_images,
)
from server.request_processor import process_job
from server import server_settings

# from flux_inference import generate

runpod.api_key = server_settings.RUNPOD_API_KEY

# Global stop events for graceful thread control
# stop_event = threading.Event()  # Application-wide shutdown

# Thread-safe lock for global variables
# lock = threading.Lock()

# last_message_acknowledge_time = time.time()
# is_last_message_acknowledged = True


# def check_idle_timeout():
#     global last_message_acknowledge_time
#     global is_last_message_acknowledged
#     idle_timeout = (
#         server_settings.IDLE_TIME_IN_SECONDS or 60
#     )  # Configurable idle timeout in seconds
#     while not stop_event.is_set():
#         try:
#             with lock:
#                 if is_last_message_acknowledged:
#                     current_time = time.time()
#                     time_difference = None
#                     if last_message_acknowledge_time:
#                         time_difference = current_time - last_message_acknowledge_time
#                     if time_difference and time_difference > idle_timeout:
#                         print("Idle timeout reached. Stopping pod...")
#                         runpod.stop_pod(server_settings.RUNPOD_POD_ID)
#                         break
#                     else:
#                         print(
#                             f"Idle timeout not reached. Time difference: {time_difference}"
#                         )
#                 else:
#                     print("Message is being processed. Resetting idle timeout...")
#         except Exception as e:
#             print(f"Error during idle timeout check: {e}")
#         time.sleep(5)


def process_request_payload(request_dict):
    job_id = request_dict.get("job_id")
    job_request_params = request_dict.get("job_request_params", None)
    webhook_url = str(request_dict.get("webhook_url", None))
    lora_url = str(request_dict.get("lora_url", None))
    if not webhook_url:
        print("No webhook url provided!")
        return None
    if not job_id:
        print("No job id provided!")
        webhook_response(webhook_url, False, 400, "No job id provided!")
        return None
    if not job_request_params or not isinstance(job_request_params, list):
        print("No job request provided!")
        webhook_response(webhook_url, False, 400, "No job request provided!")
        return None
    job = Job(job_id=job_id, webhook_url=webhook_url, lora_url=lora_url)
    for inference_request in job_request_params:
        inference_request = InferenceRequest(**inference_request)
        job.job_request_params.append(inference_request)
    return job


async def callback(data):
    if not data:
        print("No request payload found!")
        # signal_pod_termination()
        return {"error": "No request payload found!"}
    
    print(f"Received message: {data}")
    job: Job = process_request_payload(data)
    
    if not job:
        print("Failed to create job from payload!")
        # signal_pod_termination()
        return {"error": "Failed to create job from payload!"}
    
    try:
        lora_path = download_lora(job.lora_url, f"{job.job_id}.safetensors")
        await process_job(job)
        try:
            # os.remove(lora_path)
            delete_old_images("/workspace/ComfyUI/output")
        except Exception as e:
            print(f"Error deleting lora file ", lora_path)
        # signal_pod_termination()
        return {"status": "success"}
    except Exception as e:
        print(f"Error processing message: {e}")
        # signal_pod_termination()
        return {"error": str(e) }


# def signal_pod_termination():
#     global last_message_acknowledge_time
#     global is_last_message_acknowledged
#     with lock:
#         last_message_acknowledge_time = time.time()
#         is_last_message_acknowledged = True

async def receive_job(event):
    data_for_job = event["input"]
    if not data_for_job:
        return {"error": "No JSON data provided"}
    await callback(data_for_job)
    return "Image generated successfully"


# def listen_for_messages():
#     while not stop_event.is_set():
#         # Only poll if not currently processing a message
#         with lock:
#             if not is_last_message_acknowledged:
#                 print("Currently processing a job. Skipping poll...")
#                 time.sleep(server_settings.POLLING_INTERVAL)
#                 continue
        
#         try:
#             print(f"Polling backend API: {server_settings.BACKEND_API_URL}")
#             response = requests.get(server_settings.BACKEND_API_URL, timeout=10)
            
#             if response.status_code == 200:
#                 data = response.json()
                
#                 if data is None or data == {}:
#                     print("No new jobs available.")
#                 else:
#                     print(f"Received job data: {data}")
#                     callback(data)
#             else:
#                 print(f"Backend API returned status code: {response.status_code}")
#         except requests.exceptions.RequestException as e:
#             print(f"Error polling backend API: {e}")
#         except json.JSONDecodeError as e:
#             print(f"Error decoding JSON response: {e}")
#         except Exception as e:
#             print(f"Unexpected error in listen_for_messages: {e}")
        
#         time.sleep(server_settings.POLLING_INTERVAL)


# def handle_termination_signal(signum, frame):
#     print("Received termination signal. Stopping listener...")
#     stop_event.set()
#     sys.exit(0)


# Register the signal handlers to gracefully stop the application
# signal.signal(signal.SIGTERM, handle_termination_signal)
# signal.signal(signal.SIGINT, handle_termination_signal)

# idle_time_checker_thread = threading.Thread(target=check_idle_timeout)
# idle_time_checker_thread.start()

# listen_for_messages()

# while True:
#     time.sleep(5)

if __name__ == "__main__":
    runpod.serverless.start({"handler": receive_job})