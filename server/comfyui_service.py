import os
import uuid
import websocket
import json
import random
import requests
from server.server_settings import BASE_DIR


class ComfyUIService:
    def __init__(
        self,
        server_address="localhost:8188",
        workflow_path="fancrush-workflow.json",
    ):
        self.server_address = server_address
        self.workflow_path = workflow_path
        self.workflow = self.load_workflow()

        self.client_id = str(uuid.uuid4())
        # self.ws = websocket.WebSocket()
        # self.ws.connect(f"ws://{self.server_address}/ws?clientId={self.client_id}")
        self.ws = websocket.create_connection(f"ws://{self.server_address}/ws?clientId={self.client_id}")

    def load_workflow(self):
        with open(self.workflow_path, "r") as file:
            return json.load(file)

    async def queue_prompt(self, prompt):
        """Queue a workflow for execution. The prompt here is the full workflow_api.json file"""
        data = {"prompt": prompt, "client_id": self.client_id}
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            f"http://{self.server_address}/prompt", json=data, headers=headers
        )
        return response.json()

    def update_workflow(self, positive_prompt, lora_name="lora.safetensors"):
        """
        Updates the text value of a node in the workflow dictionary based on the given node title.

        :param node_title: Title of the node in the _meta object.
        :param node_value: New value to set for the text input in the matching node.
        :return: Updated workflow dictionary.
        """
        for node_id, node_data in self.workflow.items():
            if node_data.get("_meta", {}).get("title") == "Positive-Prompt":
                if "inputs" in node_data and "text" in node_data["inputs"]:
                    node_data["inputs"]["text"] = positive_prompt
            if node_data.get("_meta", {}).get("title") == "RandomNoise":
                if "inputs" in node_data and "noise_seed" in node_data["inputs"]:
                    node_data["inputs"]["noise_seed"] = random.randint(
                        10**14, 10**15 - 1
                    )
            if node_data.get("_meta", {}).get("title") == "LoraLoaderModelOnly":
                if "inputs" in node_data and "lora_name" in node_data["inputs"]:
                    node_data["inputs"]["lora_name"] = lora_name

    def track_progress(self, prompt_id):
        """Track the progress of image generation"""
        while True:
            try:
                message = json.loads(self.ws.recv())
                print(message)
                if message["type"] == "progress":
                    """If the workflow is running print k-sampler current step over total steps"""
                    print(
                        f"Progress: {message['data']['value']}/{message['data']['max']}"
                    )

                elif message["type"] == "executing":
                    """Print the node that is currently being executed"""
                    print(f"Executing node: {message['data']['node']}")

                elif message["type"] == "execution_cached":
                    """Print list of nodes that are cached"""
                    print(f"Cached execution: {message['data']}")

                """Check for completion"""
                if (
                    message["type"] == "executed"
                    and "prompt_id" in message["data"]
                    and message["data"]["prompt_id"] == prompt_id
                ):
                    print("Generation completed")
                    return True

            except Exception as e:
                print(f"Error processing message: {e}")
                return False

    async def get_history(self, prompt_id):
        """Fetch the output data for a completed workflow, returns a JSON with generation parameters and results filenames and directories"""
        response = requests.get(f"http://{self.server_address}/history/{prompt_id}")
        return response.json()

    async def get_image(self, filename, subfolder, folder_type):
        """Fetch results. Note that "save image" nodes will save image in the ouptut folder and "preview image" nodes will save image in the temp folder"""
        params = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        response = requests.get(f"http://{self.server_address}/view", params=params)
        return response.content

    def upload_image(
        self,
        input_path,
        filename,
        folder_type="input",
        image_type="image",
        overwrite=False,
    ):
        """Upload an image or a mask to the ComfyUI server. input_path is the path to the image/mask to upload and image_type is either image or mask"""

        with open(input_path, "rb") as file:
            files = {"image": (filename, file, "image/png")}
            data = {"type": folder_type, "overwrite": str(overwrite).lower()}
            url = f"http://{self.server_address}/upload/{image_type}"
            response = requests.post(url, files=files, data=data)
            return response.content

    async def generate_image(self, prompt, lora_name):

        try:
            """Update the workflow with the generation parameters"""
            self.update_workflow(
                positive_prompt=prompt,
                lora_name=lora_name,
            )

            # """Upload the input image to the server"""
            # self.upload_image(input_path=generation_parameters['input_path'], filename='img.jpg', server_address=self.server_address)

            """Send the workflow to the server"""
            prompt_id = await self.queue_prompt(self.workflow)
            prompt_id = prompt_id["prompt_id"]

            """Track the progress"""
            completed = self.track_progress(prompt_id)
            if not completed:
                print("Generation failed or interrupted")
                return None

            """Fetch the output data"""
            history = await self.get_history(prompt_id)
            print("history", history)
            outputs = history[prompt_id]["outputs"]
            print("outputs", outputs)
            """Get output images"""
            for node_id in outputs:
                node_output = outputs[node_id]
                images_output = []
                if "images" in node_output:
                    for image in node_output["images"]:
                        image_data = await self.get_image(
                            image["filename"],
                            image["subfolder"],
                            image["type"],
                        )
                        images_output.append(image_data)
            image_dir = os.path.join(BASE_DIR, "temp")
            if not os.path.exists(image_dir):
                os.makedirs(image_dir)
            image_path = os.path.join(image_dir, f"{str(uuid.uuid4())}.png")
            with open(image_path, "wb") as file:
                file.write(images_output[0])
            return image_path
        except Exception as e:
            print(f"Error generating image: {e}")
            return None
