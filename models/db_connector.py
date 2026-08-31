import mysql.connector
from mysql.connector import Error

# Configuración global para la conexión a la base de datos.
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Root', # Considerar el uso de variables de entorno para credenciales sensibles.
    'database': 'Netflix'
}

def getDbConnection():
    """
    Establece y devuelve una nueva conexión a la base de datos MySQL.
    Retorna None si la conexión falla.
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            # print("DEBUG: Conexión a MySQL exitosa.") # Comentado para producción.
            return conn
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")

    return None # Añadido para asegurar que siempre hay un retorno, aunque ya cubierto por el except.