import uuid
import server.server_settings as settings
import boto3
from datetime import datetime

from botocore.exceptions import NoCredentialsError

client = boto3.client(
    "s3",
    region_name="sfo3",
    endpoint_url=settings.DIGITAL_OCEAN_ENDPOINT_URL,
    aws_access_key_id=settings.DIGITAL_OCEAN_BUCKET_ACCESS_KEY,
    aws_secret_access_key=settings.DIGITAL_OCEAN_BUCKET_SECRET_KEY,
)


def upload(path, extension=".png", object_name=None):
    if object_name is None:
        f"images/{datetime.now().strftime('%Y-%m-%d')}/{str(uuid.uuid4())}/"
    print("###########################  UPLOADING ############################")
    file_name = path.split("/")[-1]
    upload_path = f"{object_name}{file_name}"
    bucket_name = settings.DIGITAL_OCEAN_BUCKET_NAME
    try:
        with open(path, "rb") as f:
            client.put_object(
                Bucket=bucket_name, Key=upload_path, Body=f, ACL="public-read"
            )
        print(
            f"File '{path}' uploaded to bucket '{bucket_name}' as '{upload_path}'."
        )
        return f"{settings.DIGITAL_OCEAN_BUCKET_URL}{upload_path}"
    except FileNotFoundError:
        print("The file was not found.")
    except NoCredentialsError:
        print("Credentials not available.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return None
