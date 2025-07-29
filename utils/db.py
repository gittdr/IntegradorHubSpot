import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """
    Establece la conexion con la base de datos y devuelve un objeto de conexión a SQL usando variables de entorno
    """
    try:
        return pyodbc.connect(
            f'DRIVER={os.getenv("BD_DRIVER")};'
            f'SERVER={os.getenv("bd_server")};'
            f'DATABASE={os.getenv("bd_database")};'
            f'UID={os.getenv("bd_username")};'
            f'PWD={os.getenv("bd_password")}'
        )
    except Exception as e:
        print("Error al conectar con SQL Server: ", e)
        raise
    

def save_to_database(data, query):
    """
    Save the fetched data to a database.
    :param data: The data to save.
    """
    conn = None
    try:
        # Establecer conexión a SQL Server
        conn = get_connection()
        cursor = conn.cursor()
        # Insertar los registros
        for registro in data:
            cursor.execute(query, tuple(registro.values()))
        # Confirmar cambios
        conn.commit()
        print("Datos insertados correctamente en SQL Server.")

    except Exception as e:
        print(f"Error al guardar en SQL Server con query {query}:\n{e}")

    finally:
        # Cerrar conexión
        conn.close()