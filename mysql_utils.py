# utils/mysql_utils.py
import mysql.connector
from mysql.connector import Error
from config import (
    MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
)

def get_connection():

    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        if connection.is_connected():
            print("Conexión a MySQL establecida correctamente.")
            return connection
    except Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None


def parse_date(value):

    if not value:
        return None
    try:
        return value.split("T")[0]  # solo la parte de la fecha
    except Exception:
        return None


def insert_document_metadata(doc_ai_data: dict, gcs_uri: str) -> bool:

    connection = get_connection()
    if not connection:
        print("No hay conexión a MySQL.")
        return False

    try:
        cursor = connection.cursor()

        sql = """
        INSERT INTO extracted_id_data (
            document_type, document_number, surnames, names,
            date_of_birth, place_of_birth, height, blood_group,
            gender, date_of_expedition, place_of_expedition,
            full_text, gcs_uri, extraction_timestamp
        ) VALUES (
            %(document_type)s, %(document_number)s, %(surnames)s, %(names)s,
            %(date_of_birth)s, %(place_of_birth)s, %(height)s, %(blood_group)s,
            %(gender)s, %(date_of_expedition)s, %(place_of_expedition)s,
            %(full_text)s, %(gcs_uri)s, %(extraction_timestamp)s
        )
        """

        metadata = {
            "document_type": doc_ai_data.get("document_type"),
            "document_number": doc_ai_data.get("document_number"),
            "surnames": doc_ai_data.get("surnames"),
            "names": doc_ai_data.get("names"),
            "date_of_birth": parse_date(doc_ai_data.get("date_of_birth")),
            "place_of_birth": doc_ai_data.get("place_of_birth"),
            "height": doc_ai_data.get("height"),
            "blood_group": doc_ai_data.get("blood_group"),
            "gender": doc_ai_data.get("gender"),
            "date_of_expedition": parse_date(doc_ai_data.get("date_of_expedition")),
            "place_of_expedition": doc_ai_data.get("place_of_expedition"),
            "full_text": doc_ai_data.get("full_text"),
            "gcs_uri": gcs_uri,
            "extraction_timestamp": doc_ai_data.get("extraction_timestamp"),
        }

        cursor.execute(sql, metadata)
        connection.commit()
        print("Datos insertados en MySQL correctamente.")
        return True

    except Error as e:
        print(f"Error insertando en MySQL: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
