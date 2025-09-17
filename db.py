import psycopg2
from psycopg2 import OperationalError
from datetime import datetime
import logging

DB_NAME = "images_db"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "db"
DB_PORT = 5432

logger = logging.getLogger(__name__)

def connect_db():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except OperationalError as e:
        logger.error(f"[DB] Database connection error: {e}")
        return None

def close_db(conn):
    if conn:
        conn.close()

def create_table_db():
    conn = connect_db()
    if not conn:
        return
    cur = conn.cursor()
    sql = """
        CREATE TABLE IF NOT EXISTS images (
            id SERIAL PRIMARY KEY,
            filename TEXT NOT NULL,
            original_name TEXT NOT NULL,
            size INTEGER NOT NULL,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_type TEXT NOT NULL
        );
    """
    cur.execute(sql)
    conn.commit()
    cur.close()
    close_db(conn)
    logger.info("[DB] Table 'images' checked/created")

def save_image(filename, original_name, size, file_type, upload_time=None):
    conn = connect_db()
    if not conn:
        return
    cur = conn.cursor()
    sql = """
        INSERT INTO images (filename, original_name, size, upload_time, file_type)
        VALUES (%s, %s, %s, %s, %s)
    """
    if upload_time is None:
        upload_time = datetime.now()
    cur.execute(sql, (filename, original_name, size, upload_time, file_type))
    conn.commit()
    cur.close()
    close_db(conn)
    logger.info(f"[DB] Metadata for {filename} inserted.")


def delete_image(filename: str):
    """
    Delete an image record from the database by filename.
    :param filename: The name of the file to be deleted from the `images` table.
    :return: None
    """
    conn = connect_db()
    if not conn:
        return
    try:
        cur = conn.cursor()
        sql = """DELETE FROM images WHERE filename = %s;"""
        cur.execute(sql, (filename,))
        conn.commit()
        logger.info(f"[DB] File {filename} has been deleted.")
    except Exception as e:
        logger.error(f"[DB] Error deleting file {filename}: {e}.")
        conn.rollback()
    finally:
        cur.close()
        close_db(conn)



def get_all_images():
    conn = connect_db()
    if not conn:
        return []
    cur = conn.cursor()
    sql = "SELECT id, filename, original_name, size, upload_time, file_type FROM images ORDER BY id DESC;"
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    close_db(conn)
    return [
        {
            "id": r[0],
            "filename": r[1],
            "original_name": r[2],
            "size": r[3],
            "upload_time": r[4],
            "file_type": r[5],
        }
        for r in rows
    ]

def count_images(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM images;")
    total = cur.fetchone()[0]
    cur.close()
    return total

def get_images_page(conn, limit: int, offset: int):
    cur = conn.cursor()
    sql = """
        SELECT id, filename, original_name, size, file_type, upload_time
        FROM images
        ORDER BY upload_time DESC
        LIMIT %s OFFSET %s;
    """
    cur.execute(sql, (limit, offset))
    rows = cur.fetchall()
    cur.close()
    images = [
        {
            "id": r[0],
            "filename": r[1],
            "original_name": r[2],
            "size": r[3],
            "file_type": r[4],
            "upload_time": r[5],
        }
        for r in rows
    ]
    return images