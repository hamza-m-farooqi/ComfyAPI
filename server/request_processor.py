import os
import asyncio
from threading import Thread
from server.request_queue import Job, InferenceRequest, InferenceResponse
from server.comfyui_service import ComfyUIService
from server.gcloud_utils import upload
from server.utils import webhook_response


async def process_job(job: Job):
    service = ComfyUIService()
    for param in job.job_request_params:
        image_path = await service.generate_image(param.prompt, f"{job.job_id}.safetensors")
        
        print(f"Image path: {image_path}")
        Thread(target=process_response, args=(job, image_path)).start()


def process_response(job: Job, image_path: str):
    cloud_storage_path = upload(path=str(image_path), object_name=job.job_s3_folder)
    print(f"Cloud storage path: {cloud_storage_path}")
    response = InferenceResponse(job_id=job.job_id, image_path=cloud_storage_path)
    webhook_response(
        job.webhook_url,
        True,
        200,
        "Image Generated!",
        response.dict(),
    )
    try:
        os.remove(image_path)
    except Exception as e:
        print(f"Error occured during deleting images",str(e))
