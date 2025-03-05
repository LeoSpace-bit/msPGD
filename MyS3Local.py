from minio import Minio
from minio.error import S3Error
import os

minio_client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)


def upload_photo_to_minio(file_path, bucket_name, object_name):
    try:
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)

        minio_client.fput_object(
            bucket_name,
            object_name,
            file_path
        )
        return True
    except S3Error as e:
        print(f"Ошибка загрузки в MinIO: {e}")
        return False
    except Exception as e:
        print(f"Общая ошибка: {e}")
        return False


def get_photo_url(bucket_name, object_name):
    try:
        return minio_client.presigned_get_object(bucket_name, object_name)
    except S3Error as e:
        print(f"Ошибка получения URL: {e}")
        return None