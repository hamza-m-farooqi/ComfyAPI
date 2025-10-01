# ComfyAPI

A RunPod-based service that processes ComfyUI inference jobs with LoRA model support.

## Overview

ComfyAPI polls a backend API for inference jobs, downloads LoRA models, processes them through ComfyUI workflows, and manages automatic pod termination based on idle timeout.

## Features

- Automatic job polling from backend API
- LoRA model download and processing
- ComfyUI workflow execution
- Webhook callbacks for job results
- Idle timeout management with automatic pod termination
- Thread-safe job processing

## Requirements

- Python 3.x
- ComfyUI installation at `/workspace/ComfyUI`
- Google Cloud Storage credentials

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Set the following environment variables:

- `BACKEND_API_URL` - Backend API endpoint for job polling
- `RUNPOD_POD_ID` - RunPod pod identifier
- `RUNPOD_API_KEY` - RunPod API key
- `GCLOUD_BUCKET_NAME` - Google Cloud Storage bucket name
- `IDLE_TIME_IN_SECONDS` - Idle timeout duration (default: 300)
- `POLLING_INTERVAL` - API polling interval in seconds (default: 1)

## Usage

```bash
python main.py
```

The service will:
1. Start polling the backend API for jobs
2. Download LoRA models when jobs are received
3. Process jobs through ComfyUI
4. Send results via webhook
5. Automatically terminate the pod after idle timeout

## Project Structure

```
ComfyAPI/
├── main.py                      # Main entry point
├── requirements.txt             # Python dependencies
├── fancrush-workflow.json       # ComfyUI workflow configuration
└── server/                      # Server modules
    ├── comfyui_service.py       # ComfyUI integration
    ├── gcloud_utils.py          # Google Cloud utilities
    ├── request_processor.py     # Job processing logic
    ├── request_queue.py         # Request/job data structures
    ├── server_settings.py       # Configuration settings
    └── utils.py                 # Utility functions
