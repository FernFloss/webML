from minio import Minio
from config import Config

minio_client = Minio(
    Config.MINIO_ENDPOINT,
    access_key=Config.MINIO_ACCESS_KEY,
    secret_key=Config.MINIO_SECRET_KEY,
    secure=Config.MINIO_SECURE,
)


def get_frame_bytes(bucket: str, obj: str) -> bytes:
    response = minio_client.get_object(bucket, obj)
    try:
        data = response.read()
    finally:
        response.close()
        response.release_conn()
    return data
