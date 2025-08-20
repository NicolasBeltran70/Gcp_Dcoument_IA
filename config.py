import os
from dotenv import load_dotenv

# Carga las variables desde .env
load_dotenv()

# ================== API ==================
API_KEY = os.getenv("API_KEY")

# ================== MySQL ==================
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

# ================== GCS ==================
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")

# ================== Document AI ==================
# Aquí colocarías PROJECT_ID, LOCATION, PROCESSOR_ID si vas a integrar el servicio real
PROJECT_ID = os.getenv("PROJECT_ID", "my-project-id")
LOCATION = os.getenv("LOCATION", "us")  
PROCESSOR_ID = os.getenv("PROCESSOR_ID", "processor-id")

# ================== Parámetros internos ==================
# Umbral mínimo de caracteres para considerar el OCR "legible"
MIN_LEGIBLE_CHARS = int(os.getenv("MIN_LEGIBLE_CHARS", "10"))
