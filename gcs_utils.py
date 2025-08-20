# utils/gcs_utils.py
import os
import mimetypes
import uuid
from google.cloud import storage
from config import GCS_BUCKET_NAME

def upload_to_gcs(filename, file_bytes):

    print("INICIO upload_to_gcs")

    if not GCS_BUCKET_NAME:
        raise ValueError("GCS_BUCKET_NAME no definido en .env")

    # Detección de tipo MIME
    ext_ct = mimetypes.guess_type(filename)[0] or "application/octet-stream"

    # Nombre único
    uniq_name = f"{uuid.uuid4().hex}_{os.path.basename(filename)}"

    print(f"Subiendo a bucket={GCS_BUCKET_NAME}, content_type={ext_ct}, filename={uniq_name}")
    storage_client = storage.Client()
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(uniq_name)
    blob.upload_from_string(file_bytes, content_type=ext_ct)

    gcs_uri = f"gs://{GCS_BUCKET_NAME}/{uniq_name}"
    print(f"Archivo subido a {gcs_uri}")
    print("FIN upload_to_gcs")
    return gcs_uri
