import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conexion = psycopg2.connect(
    host=os.getenv("DB_HOST", "173.212.252.164"),
    port=int(os.getenv("DB_PORT", 5432)),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

cursor = conexion.cursor()

with open("script.sql", "r", encoding="utf-8") as f:
    sql = f.read()

cursor.execute(sql)
conexion.commit()

cursor.close()
conexion.close()