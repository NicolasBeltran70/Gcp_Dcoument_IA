import base64
import datetime
import binascii
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel

from utils.gcs_utils import upload_to_gcs
from utils.docai_utils import process_document_ai
from utils.mysql_utils import insert_document_metadata
from config import API_KEY
from fastapi import Header

app = FastAPI(title="Document AI Extractor API")


# ========== Seguridad con API KEY ==========
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return True


# ========== Request body ==========
class DocumentRequest(BaseModel):
    filename: str
    file_base64: str


# ========== Endpoint principal ==========
@app.post("/process-document")
async def process_document(request: DocumentRequest, valid: bool = Depends(verify_api_key)):
    try:
        print("INICIO proceso /process-document")

        # 1) Decodificación base64 segura
        print("INICIO decodificacion base64")
        try:
            file_bytes = base64.b64decode(request.file_base64, validate=True)
        except (binascii.Error, ValueError):
            raise HTTPException(status_code=400, detail="Archivo base64 inválido")
        print("FIN decodificacion base64")

        # 2) Subida a GCS
        print("INICIO subida a GCS")
        gcs_uri = upload_to_gcs(request.filename, file_bytes)
        print(f"FIN subida a GCS: {gcs_uri}")

        # 3) Procesamiento Document AI
        print("INICIO procesamiento Document AI")
        extraction_timestamp = datetime.datetime.utcnow()
        doc_metadata = process_document_ai(gcs_uri, extraction_timestamp)
        print("FIN procesamiento Document AI")

        # 4) Inserción MySQL
        print("INICIO insercion en MySQL")
        ok = insert_document_metadata(doc_metadata, gcs_uri)
        if not ok:
            raise HTTPException(status_code=500, detail="Error insertando en MySQL")
        print("FIN insercion en MySQL")

        print("FIN proceso /process-document")
        return {
            "tipo_documento": doc_metadata.get("document_type"),
            "full_text": doc_metadata.get("full_text"),
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error inesperado: {e}")
        raise HTTPException(status_code=500, detail="Error interno")
