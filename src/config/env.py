import os
from dotenv import load_dotenv # type: ignore

load_dotenv()

def get_env_var(name: str) -> str:
    value = os.getenv(name)
    if value is None or value == "":
        raise EnvironmentError(f"Required environment variable '{name}' is not set.")
    return value

RABBITMQ_URL = get_env_var("RABBITMQ_URL")
QUEUE_NAME = get_env_var("QUEUE_NAME")

MINIO_ENDPOINT = get_env_var("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = get_env_var("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = get_env_var("MINIO_SECRET_KEY")
MINIO_BUCKET = get_env_var("MINIO_BUCKET")

LMSTUDIO_MODEL = get_env_var("LMSTUDIO_MODEL")
LMSTUDIO_API_URL = get_env_var("LMSTUDIO_API_URL")

API_URL = get_env_var("API_URL")