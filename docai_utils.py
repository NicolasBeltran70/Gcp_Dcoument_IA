# utils/docai_utils.py
import datetime
import mimetypes
from google.cloud import storage, documentai
from config import PROJECT_ID, LOCATION, PROCESSOR_ID, MIN_LEGIBLE_CHARS

def process_document_ai(gcs_uri, extraction_timestamp):

    print("INICIO process_document_ai")

    # === Descargar archivo desde GCS ===
    storage_client = storage.Client(project=PROJECT_ID)

    if gcs_uri.startswith("https://"):
        bucket_name = gcs_uri.split('/')[3]
        blob_name = '/'.join(gcs_uri.split('/')[4:])
    else:  # formato gs://
        bucket_name = gcs_uri.split('/')[2]
        blob_name = '/'.join(gcs_uri.split('/')[3:])

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    document_content = blob.download_as_bytes()
    mime_type = blob.content_type or mimetypes.guess_type(blob_name)[0] or "application/pdf"

    # === Cliente de Document AI ===
    opts = {"api_endpoint": f"{LOCATION}-documentai.googleapis.com"}
    docai_client = documentai.DocumentProcessorServiceClient(client_options=opts)
    name = docai_client.processor_path(PROJECT_ID, LOCATION, PROCESSOR_ID)

    raw_document = documentai.RawDocument(content=document_content, mime_type=mime_type)
    request = documentai.ProcessRequest(name=name, raw_document=raw_document)
    result = docai_client.process_document(request)

    document_response = result.document

    # === Inicializa diccionario resultado ===
    extracted_data = {
        "document_type": None,
        "document_number": None,
        "surnames": None,
        "names": None,
        "date_of_birth": None,
        "place_of_birth": None,
        "height": None,
        "blood_group": None,
        "gender": None,
        "date_of_expedition": None,
        "place_of_expedition": None,
        "full_text": document_response.text,
        "gcs_uri": gcs_uri,
        "extraction_timestamp": extraction_timestamp,
    }

    # === Mapeo entidades → columnas MySQL ===
    field_map = {
        "tipo_documento": "document_type",
        "id_documento": "document_number",
        "Apellidos": "surnames",
        "Nombre": "names",
        "f_nacimiento": "date_of_birth",
        "lugar_nacimiento": "place_of_birth",
        "estatura": "height",
        "g_sanguineo": "blood_group",
        "genero": "gender",
        "fecha_expedicion": "date_of_expedition",
        "lugar_expedicion": "place_of_expedition",
    }

    # === Recorrer entidades y mapear ===
    for entity in document_response.entities:
        mysql_column = field_map.get(entity.type_)
        if mysql_column:
            if entity.type_ in ["f_nacimiento", "fecha_expedicion"] and entity.normalized_value:
                extracted_data[mysql_column] = entity.normalized_value.text
            elif entity.mention_text:
                extracted_data[mysql_column] = entity.mention_text

    # === Validar legibilidad según full_text ===
    extracted_data["legible"] = (
        len(extracted_data["full_text"].strip()) >= MIN_LEGIBLE_CHARS
    )

    print("FIN process_document_ai")
    return extracted_data
