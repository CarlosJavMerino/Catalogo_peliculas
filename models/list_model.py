from .db_connector import getDbConnection
from mysql.connector import Error

class ListModel:
    # Proporciona métodos para interactuar con la tabla 'lista' y 'Lista_Titulo' en la base de datos.
    # Se encarga de las operaciones CRUD para las listas de reproducción de los usuarios.

    def getUserLists(self, userId):
        """Obtiene todas las listas (id y nombre) de un usuario específico."""
        conn = getDbConnection()
        if not conn: return [] # Retorna lista vacía si no hay conexión.
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True) # Devuelve filas como diccionarios.
            query = "SELECT id_lista, nombre_lista FROM lista WHERE id_usuario = %s"
            cursor.execute(query, (userId,))
            return cursor.fetchall()
        except Error as e:
            print(f"Error en ListModel.getUserLists: {e}")
            return []
        finally:
            # Asegura que la conexión y el cursor se cierren correctamente.
            if conn and conn.is_connected():
                if cursor:
                    cursor.close()
                conn.close()

    def createList(self, userId, listName):
        """
        Crea una nueva lista para un usuario.
        Retorna el ID de la nueva lista si tiene éxito, None en caso contrario.
        """
        conn = getDbConnection()
        if not conn: return None
        cursor = None
        try:
            cursor = conn.cursor()
            query = "INSERT INTO lista (nombre_lista, id_usuario) VALUES (%s, %s)"
            cursor.execute(query, (listName, userId))
            conn.commit() # Confirma la transacción.
            return cursor.lastrowid # ID del último registro insertado.
        except Error as e:
            print(f"Error en ListModel.createList: {e}")
            if conn and conn.is_connected():
                conn.rollback() # Deshace la transacción en caso de error.
            return None
        finally:
            if conn and conn.is_connected():
                if cursor:
                    cursor.close()
                conn.close()

    def deleteList(self, listId):
        """
        Elimina una lista y todas sus referencias en la tabla de unión 'Lista_Titulo'.
        Retorna True si la eliminación es exitosa, False en caso contrario.
        """
        conn = getDbConnection()
        if not conn: return False
        cursor = None
        try:
            cursor = conn.cursor()
            # Primero elimina las referencias en la tabla de unión para evitar errores de clave foránea.
            cursor.execute("DELETE FROM Lista_Titulo WHERE id_lista = %s", (listId,))
            # Luego elimina la lista principal.
            cursor.execute("DELETE FROM lista WHERE id_lista = %s", (listId,))
            conn.commit()
            return True
        except Error as e:
            print(f"Error en ListModel.deleteList: {e}")
            if conn and conn.is_connected():
                 conn.rollback()
            return False
        finally:
            if conn and conn.is_connected():
                if cursor:
                    cursor.close()
                conn.close()

    def getTitlesInList(self, listId):
        """
        Obtiene los datos básicos (id, nombre, sinopsis, imagen) de los títulos
        contenidos en una lista específica.
        """
        conn = getDbConnection()
        if not conn: return []
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT T.id_titulo, T.nombre, T.sinopsis, T.imagen_url
                FROM Titulo T
                JOIN Lista_Titulo LT ON T.id_titulo = LT.id_titulo
                WHERE LT.id_lista = %s
            """
            cursor.execute(query, (listId,))
            return cursor.fetchall()
        except Error as e:
            print(f"Error en ListModel.getTitlesInList: {e}")
            return []
        finally:
            if conn and conn.is_connected():
                if cursor:
                    cursor.close()
                conn.close()

    def addTitleToList(self, listId, titleId):
        """
        Añade un título a una lista específica.
        Retorna True si el título se añadió correctamente.
        Retorna False si el título ya estaba en la lista o si ocurrió un error.
        """
        conn = getDbConnection()
        if not conn: return False
        cursor = None
        try:
            cursor = conn.cursor()
            query = "INSERT INTO lista_titulo (id_lista, id_titulo) VALUES (%s, %s)"
            cursor.execute(query, (listId, titleId))
            conn.commit()
            return True
        except Error as e:
            # Maneja el error de clave duplicada (título ya en la lista).
            if e.errno == 1062: # Código de error para entrada duplicada en MySQL.
                 print(f"El título {titleId} ya está en la lista {listId}.")
            else:
                print(f"Error en ListModel.addTitleToList: {e}")
            # No es necesario rollback aquí ya que INSERT fallido no deja transacciones pendientes.
            return False
        finally:
            if conn and conn.is_connected():
                if cursor:
                    cursor.close()
                conn.close()

    def removeTitleFromList(self, listId, titleId):
        """
        Elimina un título de una lista específica.
        Retorna True si se eliminó al menos una fila, False en caso contrario o si hay error.
        """
        conn = getDbConnection()
        if not conn: return False
        cursor = None
        try:
            cursor = conn.cursor()
            query = "DELETE FROM Lista_Titulo WHERE id_lista = %s AND id_titulo = %s"
            cursor.execute(query, (listId, titleId))
            conn.commit()
            return cursor.rowcount > 0 # True si se afectó alguna fila.
        except Error as e:
            print(f"Error en ListModel.removeTitleFromList: {e}")
            if conn and conn.is_connected():
                conn.rollback()
            return False
        finally:
            if conn and conn.is_connected():
                if cursor:
                    cursor.close()
                conn.close()