import uuid
from datetime import datetime
from enum import Enum
from typing import List
from pydantic import BaseModel


class InferenceRequest(BaseModel):
    prompt: str
    image_width: int = 1280
    image_height: int = 1040
    guidance: float = 2.5
    steps: int = 20
    seed: int = 42


class InferenceResponse(BaseModel):
    job_id: str = None
    image_path: str = None


class Job(BaseModel):
    job_id: str
    webhook_url: str
    lora_url: str
    job_request_params: List[InferenceRequest] = []
    job_s3_folder: str = None

    def __init__(self, **data):
        super().__init__(**data)
        # Dynamically set job_s3_folder using job_id and current date
        if self.job_id:
            self.job_s3_folder = (
                f"images/{datetime.now().strftime('%Y-%m-%d')}/{self.job_id}/"
            )
