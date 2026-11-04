import os
import psycopg2
from dotenv import load_dotenv

# 1. Cargamos las credenciales desde el archivo .env
load_dotenv()

def inicializar_bd():
    try:
        # 2. Conectamos con el VPS 2 mediante psycopg2
        conexion = psycopg2.connect(
            host=os.getenv("DB_HOST", "173.212.252.164"),
            port=int(os.getenv("DB_PORT", 5432)),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        cursor = conexion.cursor()
        print(" Conexión establecida con éxito al VPS 2.")

        # 3. Definición DDL de las tablas
        sql = """
        -- Tabla de usuarios (almacena credenciales)
        CREATE TABLE IF NOT EXISTS usuarios (
            usuario VARCHAR(50) PRIMARY KEY,
            password VARCHAR(255) NOT NULL
        );

        -- Tabla de frases (vinculada al usuario por clave foránea)
        CREATE TABLE IF NOT EXISTS frases (
            id SERIAL PRIMARY KEY,
            frase VARCHAR(255) NOT NULL,
            usuario VARCHAR(50) REFERENCES usuarios(usuario)
        );
        """

        # 4. Ejecutar el script y confirmar cambios
        cursor.execute(sql)
        conexion.commit()
        print(" Tablas 'usuarios' y 'frases' creadas o verificadas con éxito.")

        # 5. Comprobación (equivalente a ejecutar \dt en la consola)
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
        """)
        tablas = cursor.fetchall()
        print("\nTablas activas en tu esquema:")
        for t in tablas:
            print(f"  -> {t[0]}")

        cursor.close()
        conexion.close()
        print("\n Conexión cerrada de forma limpia.")

    except Exception as e:
        print(" Error durante la ejecución:", e)

if __name__ == "__main__":
    inicializar_bd()