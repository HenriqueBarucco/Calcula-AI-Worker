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

WAIT_QUEUE_NAME = os.getenv("WAIT_QUEUE_NAME")
PARKING_LOT_QUEUE_NAME = os.getenv("PARKING_LOT_QUEUE_NAME")

EXCHANGE_NAME = os.getenv("EXCHANGE_NAME")
WAIT_ROUTING_KEY = os.getenv("WAIT_ROUTING_KEY")
PARKING_LOT_ROUTING_KEY = os.getenv("PARKING_LOT_ROUTING_KEY")

WAIT_TTL_MS = int(os.getenv("WAIT_TTL_MS", "30000"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
PRE_FETCH_COUNT = int(os.getenv("PRE_FETCH_COUNT", "1"))

MINIO_ENDPOINT = get_env_var("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = get_env_var("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = get_env_var("MINIO_SECRET_KEY")
MINIO_BUCKET = get_env_var("MINIO_BUCKET")

LMSTUDIO_MODEL = get_env_var("LMSTUDIO_MODEL")
LMSTUDIO_API_URL = get_env_var("LMSTUDIO_API_URL")

LMSTUDIO_TIMEOUT_SECONDS = int(os.getenv("LMSTUDIO_TIMEOUT_SECONDS", "120"))
LMSTUDIO_MAX_RETRIES = int(os.getenv("LMSTUDIO_MAX_RETRIES", "2"))
LMSTUDIO_RETRY_BASE_DELAY = float(os.getenv("LMSTUDIO_RETRY_BASE_DELAY", "1.5"))

API_URL = get_env_var("API_URL")

LOGSTASH_URL = os.getenv("LOGSTASH_URL", "localhost:5000")
LOGSTASH_TOKEN = os.getenv("LOGSTASH_TOKEN", "xxx")
LOGSTASH_ENV = os.getenv("LOGSTASH_ENV", "dev")