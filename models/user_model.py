from .db_connector import getDbConnection
from mysql.connector import Error
import bcrypt # Para el hashing seguro de contraseñas.

class UserModel:
    # Proporciona métodos para la autenticación, registro y gestión del PIN de control parental de los usuarios.
    def authenticateUser(self, email, password):
        """
        Autentica un usuario comparando el hash de la contraseña proporcionada
        con el hash almacenado en la base de datos.
        Retorna un diccionario con el estado y datos del usuario si es exitoso,
        o un mensaje de error.
        """
        conn = getDbConnection()
        if not conn:
            return {"estado": "error_db", "mensaje": "No se pudo conectar a la base de datos"}

        cursor = None
        try:
            cursor = conn.cursor(dictionary=True) # Para acceder a los campos por nombre.
            query = "SELECT id_usuario, nombre_usuario, contraseña FROM usuario WHERE email = %s"
            cursor.execute(query, (email,))
            userData = cursor.fetchone()

            if userData:
                storedHashedPasswordStr = userData['contraseña'] # Hash almacenado como string.
                storedHashedPasswordBytes = storedHashedPasswordStr.encode('utf-8') # bcrypt necesita bytes.
                enteredPasswordBytes = password.encode('utf-8')

                # Compara la contraseña ingresada con el hash almacenado.
                if bcrypt.checkpw(enteredPasswordBytes, storedHashedPasswordBytes):
                    return {"estado": "ok", "id_usuario": userData['id_usuario'], "nombre_usuario": userData['nombre_usuario']}
                else:
                    return {"estado": "error_password", "mensaje": "Contraseña incorrecta"}
            else:
                return {"estado": "error_user", "mensaje": "Usuario no encontrado"}
        except Error as e:
            print(f"Error en UserModel.authenticateUser: {e}")
            return {"estado": "error_db", "mensaje": f"Error de base de datos: {e}"}
        finally:
            if conn and conn.is_connected():
                if cursor:
                    cursor.close()
                conn.close()

    def registerUser(self, nombreUsuario, email, contraseña):
        """
        Registra un nuevo usuario en la base de datos.
        Hashea la contraseña antes de almacenarla.
        Retorna un diccionario con el estado y el ID del nuevo usuario si es exitoso,
        o un mensaje de error.
        """
        conn = getDbConnection()
        if not conn:
            return {"estado": "error_db", "mensaje": "No se pudo conectar a la base de datos"}

        cursor = None
        try:
            cursor = conn.cursor()
            # Verifica si el email o nombre de usuario ya existen.
            query_check = "SELECT id_usuario FROM usuario WHERE email = %s OR nombre_usuario = %s"
            cursor.execute(query_check, (email, nombreUsuario))
            if cursor.fetchone():
                return {"estado": "error_exists", "mensaje": "El usuario o correo ya está registrado"}

            # Hashea la contraseña.
            passwordBytes = contraseña.encode('utf-8')
            salt = bcrypt.gensalt() # Genera un salt aleatorio.
            hashedPasswordBytes = bcrypt.hashpw(passwordBytes, salt)
            hashedPasswordStr = hashedPasswordBytes.decode('utf-8') # Guarda el hash como string.

            # Inserta el nuevo usuario.
            query_insert = """
                INSERT INTO usuario (nombre_usuario, email, contraseña, pin_control)
                VALUES (%s, %s, %s, NULL) 
            """
            # pin_control se inicializa a NULL.
            cursor.execute(query_insert, (nombreUsuario, email, hashedPasswordStr))
            conn.commit()
            return {"estado": "ok", "id_usuario": cursor.lastrowid}
        except Error as e:
            print(f"Error en UserModel.registerUser: {e}")
            if conn and conn.is_connected(): conn.rollback()
            return {"estado": "error_db", "mensaje": f"Error de base de datos al registrar: {e}"}
        finally:
            if conn and conn.is_connected():
                if cursor:
                    cursor.close()
                conn.close()

    def getPin(self, userId):
        """Obtiene el PIN de control parental de un usuario."""
        conn = getDbConnection()
        if not conn:
            return None
        cursor = None
        try:
            cursor = conn.cursor() # Solo una columna.
            cursor.execute("SELECT pin_control FROM Usuario WHERE id_usuario = %s", (userId,))
            result = cursor.fetchone()
            return result[0] if result else None # result[0] es el PIN o NULL.
        except Error as e:
            print(f"Error en UserModel.getPin: {e}")
            return None
        finally:
            if conn and conn.is_connected():
                if cursor:
                    cursor.close()
                conn.close()

    def updatePin(self, userId, newPin):
        """
        Actualiza o establece el PIN de control parental para un usuario.
        Retorna True si la operación fue exitosa, False en caso contrario.
        """
        conn = getDbConnection()
        if not conn:
            return False
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE Usuario SET pin_control = %s WHERE id_usuario = %s", (newPin, userId))
            conn.commit()
            return True
        except Error as e:
            print(f"Error en UserModel.updatePin: {e}")
            if conn and conn.is_connected(): conn.rollback()
            return False
        finally:
            if conn and conn.is_connected():
                if cursor:
                    cursor.close()
                conn.close()

    def deletePin(self, userId):
        """
        Elimina (establece a NULL) el PIN de control parental de un usuario.
        Retorna True si la operación fue exitosa, False en caso contrario.
        """
        conn = getDbConnection()
        if not conn:
            return False
        cursor = None
        try:
            cursor = conn.cursor()
            # Establece el pin_control a NULL en lugar de eliminar la fila del usuario.
            cursor.execute("UPDATE Usuario SET pin_control = NULL WHERE id_usuario = %s", (userId,))
            conn.commit()
            return True
        except Error as e:
            print(f"Error en UserModel.deletePin: {e}")
            if conn and conn.is_connected(): conn.rollback()
            return False
        finally:
            if conn and conn.is_connected():
                if cursor:
                    cursor.close()
                conn.close()