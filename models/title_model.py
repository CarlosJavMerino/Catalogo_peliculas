from .db_connector import getDbConnection, DB_CONFIG # DB_CONFIG no se usa aquí directamente.
from mysql.connector import Error
from collections import Counter # Para el sistema de recomendaciones.

class TitleModel:
    # Proporciona métodos para interactuar con datos relacionados con títulos,
    # como detalles, actores, géneros, capítulos, y recomendaciones.

    def getWatchedChaptersForTitle(self, userId, titleId):
        """
        Obtiene un conjunto de IDs de capítulos que el usuario ha marcado como vistos
        para un título específico (serie).
        """
        conn = getDbConnection()
        if not conn:
            print("Error de conexión en getWatchedChaptersForTitle")
            return set() # Retorna un conjunto vacío si no hay conexión.

        watchedIds = set()
        cursor = None
        try:
            cursor = conn.cursor() # No necesita dictionary=True, solo IDs.
            query = """
                SELECT id_capitulo FROM Visto
                WHERE id_usuario = %s AND id_titulo = %s AND id_capitulo IS NOT NULL
            """
            cursor.execute(query, (userId, titleId))
            for row in cursor.fetchall():
                watchedIds.add(row[0]) # row[0] es id_capitulo.
            return watchedIds
        except Error as e:
            print(f"Error en TitleModel.getWatchedChaptersForTitle: {e}")
            return set()
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def getDetails(self, titleId):
        """Obtiene todos los detalles de un título por su ID."""
        conn = getDbConnection()
        if not conn: return None
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Titulo WHERE id_titulo = %s", (titleId,))
            return cursor.fetchone() # Retorna un diccionario o None si no se encuentra.
        except Error as e:
            print(f"Error en TitleModel.getDetails: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def getActors(self, titleId):
        """Obtiene la lista de nombres de actores para un título específico."""
        conn = getDbConnection()
        if not conn: return []
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True) # Devuelve cada actor como {'nombre': 'Nombre Actor'}.
            query = """
                SELECT a.nombre FROM Actor a
                JOIN Titulo_Actor ta ON a.id_actor = ta.id_actor
                WHERE ta.id_titulo = %s
            """
            cursor.execute(query, (titleId,))
            return cursor.fetchall() # Lista de diccionarios.
        except Error as e:
            print(f"Error en TitleModel.getActors: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def getChapters(self, titleId, seasonNumber):
        """Obtiene los capítulos de una temporada específica de una serie."""
        conn = getDbConnection()
        if not conn: return []
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT id_capitulo, numero, nombre, duración FROM Capitulo
                WHERE id_titulo = %s AND temporada = %s ORDER BY numero
            """
            cursor.execute(query, (titleId, seasonNumber))
            return cursor.fetchall()
        except Error as e:
            print(f"Error en TitleModel.getChapters: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def getSeasons(self, titleId):
        """Obtiene una lista de los números de temporada disponibles para una serie."""
        conn = getDbConnection()
        if not conn: return []
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True) # Para acceder a 'temporada' por nombre.
            query = "SELECT DISTINCT temporada FROM Capitulo WHERE id_titulo=%s ORDER BY temporada"
            cursor.execute(query, (titleId,))
            return [str(r["temporada"]) for r in cursor.fetchall()] # Convierte números a string.
        except Error as e:
            print(f"Error en TitleModel.getSeasons: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def getTitlesForHome(self, contentType, limit=10):
        """
        Obtiene títulos para la página de inicio, filtrados por tipo (película/serie)
        y ordenados por calificación.
        """
        conn = getDbConnection()
        if not conn: return []
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT id_titulo, nombre, imagen_url
                FROM Titulo
                WHERE tipo = %s
                ORDER BY calificación DESC LIMIT %s
            """
            cursor.execute(query, (contentType, limit))
            return cursor.fetchall()
        except Error as e:
            print(f"Error en TitleModel.getTitlesForHome: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def getAllGenres(self):
        """
        Obtiene todos los géneros disponibles, devolviendo un diccionario
        con {nombre_genero: id_genero}.
        """
        conn = getDbConnection()
        if not conn: return {}
        genresDict = {}
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id_genero, nombre FROM genero ORDER BY nombre")
            for row in cursor.fetchall():
                genresDict[row['nombre']] = row['id_genero']
            return genresDict
        except Error as e:
            print(f"Error en TitleModel.getAllGenres: {e}")
            return {}
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def getDistinctReleaseYears(self):
        """Obtiene una lista de años de estreno distintos, ordenados descendentemente."""
        conn = getDbConnection()
        if not conn: return []
        cursor = None
        try:
            cursor = conn.cursor() # No necesita dictionary=True, solo una columna.
            cursor.execute("SELECT DISTINCT año_estreno FROM titulo ORDER BY año_estreno DESC")
            return [str(row[0]) for row in cursor.fetchall()] # Convierte años a string.
        except Error as e:
            print(f"Error en TitleModel.getDistinctReleaseYears: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def searchTitles(self, searchTerm="", genreId=None, contentType=None, year=None):
        """
        Busca títulos basados en un término de búsqueda y filtros opcionales
        (género, tipo de contenido, año).
        """
        conn = getDbConnection()
        if not conn: return []
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM titulo WHERE nombre LIKE %s" # Búsqueda inicial por nombre.
            params = [f"%{searchTerm}%"] # Parámetro para LIKE.

            # Añade condiciones a la query dinámicamente según los filtros proporcionados.
            if genreId:
                # Subconsulta para filtrar por género a través de la tabla de unión Titulo_Genero.
                query += " AND id_titulo IN (SELECT id_titulo FROM titulo_genero WHERE id_genero = %s)"
                params.append(genreId)
            if contentType and contentType.lower() != "todos los tipos":
                query += " AND tipo = %s"
                params.append(contentType)
            if year and year.lower() != "todos los años": # "todos los años" indica no filtrar por año.
                query += " AND año_estreno = %s"
                params.append(int(year)) # El año en la BD es numérico.

            query += " ORDER BY calificación DESC" # Ordena los resultados.
            cursor.execute(query, tuple(params)) # Ejecuta la query construida.
            return cursor.fetchall()
        except Error as e:
            print(f"Error en TitleModel.searchTitles: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def isLiked(self, userId, titleId):
        """Verifica si un usuario ha dado 'Me gusta' a un título."""
        conn = getDbConnection()
        if not conn: return False
        cursor = None
        try:
            cursor = conn.cursor()
            query = "SELECT 1 FROM Megusta WHERE id_usuario=%s AND id_titulo=%s"
            cursor.execute(query, (userId, titleId))
            return cursor.fetchone() is not None # True si existe la fila, False si no.
        except Error as e:
            print(f"Error en TitleModel.isLiked: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def toggleLike(self, userId, titleId):
        """
        Cambia el estado de 'Me gusta' de un título para un usuario.
        Si ya le gusta, lo quita. Si no, lo añade.
        Retorna True si la operación fue exitosa, False en caso de error.
        """
        conn = getDbConnection()
        if not conn: return False
        cursor = None
        try:
            cursor = conn.cursor()
            # Verifica el estado actual de 'Me gusta'.
            cursor.execute("SELECT 1 FROM Megusta WHERE id_usuario=%s AND id_titulo=%s", (userId, titleId))
            currentlyLiked = cursor.fetchone() is not None

            if currentlyLiked:
                # Si ya le gusta, elimina el registro.
                cursor.execute("DELETE FROM Megusta WHERE id_usuario=%s AND id_titulo=%s", (userId, titleId))
            else:
                # Si no le gusta, inserta un nuevo registro.
                cursor.execute("INSERT INTO Megusta (id_usuario, id_titulo) VALUES (%s, %s)", (userId, titleId))
            conn.commit()
            return True
        except Error as e:
            print(f"Error en TitleModel.toggleLike: {e}")
            if conn.is_connected(): conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def isWatched(self, userId, titleId, chapterId=None):
        """
        Verifica si un usuario ha marcado un título o un capítulo como 'Visto'.
        Si chapterId es None, verifica el título completo.
        """
        conn = getDbConnection()
        if not conn: return False
        cursor = None
        try:
            cursor = conn.cursor()
            if chapterId is not None: # Verifica un capítulo específico.
                query = "SELECT 1 FROM Visto WHERE id_usuario=%s AND id_titulo=%s AND id_capitulo=%s"
                cursor.execute(query, (userId, titleId, chapterId))
            else: # Verifica el título completo (película o serie marcada como vista en general).
                query = "SELECT 1 FROM Visto WHERE id_usuario=%s AND id_titulo=%s AND id_capitulo IS NULL"
                cursor.execute(query, (userId, titleId))
            return cursor.fetchone() is not None
        except Error as e:
            print(f"Error en TitleModel.isWatched: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def toggleWatched(self, userId, titleId, chapterId=None):
        """
        Cambia el estado de 'Visto' para un título o capítulo.
        Si chapterId es None, afecta al título completo.
        Retorna True si la operación fue exitosa, False en caso de error.
        """
        conn = getDbConnection()
        if not conn: return False
        cursor = None
        try:
            cursor = conn.cursor()
            currentlyWatched = False
            # Verifica el estado actual de 'Visto'.
            if chapterId is not None:
                cursor.execute("SELECT 1 FROM Visto WHERE id_usuario=%s AND id_titulo=%s AND id_capitulo=%s",
                               (userId, titleId, chapterId))
                currentlyWatched = cursor.fetchone() is not None
            else:
                cursor.execute("SELECT 1 FROM Visto WHERE id_usuario=%s AND id_titulo=%s AND id_capitulo IS NULL",
                               (userId, titleId))
                currentlyWatched = cursor.fetchone() is not None

            if currentlyWatched:
                # Si ya está visto, lo elimina.
                if chapterId is not None:
                    cursor.execute("DELETE FROM Visto WHERE id_usuario=%s AND id_titulo=%s AND id_capitulo=%s",
                                   (userId, titleId, chapterId))
                else:
                    cursor.execute("DELETE FROM Visto WHERE id_usuario=%s AND id_titulo=%s AND id_capitulo IS NULL",
                                   (userId, titleId))
            else:
                # Si no está visto, lo inserta con la fecha actual.
                cursor.execute("""
                    INSERT INTO Visto (id_usuario, id_titulo, id_capitulo, fecha_visto)
                    VALUES (%s, %s, %s, NOW())
                """, (userId, titleId, chapterId))
            conn.commit()
            return True
        except Error as e:
            print(f"Error en TitleModel.toggleWatched: {e}")
            if conn.is_connected(): conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def getTitleClassification(self, titleId):
        """Obtiene la clasificación (ej. R, PG-13) de un título."""
        conn = getDbConnection()
        if not conn: return None
        cursor = None
        try:
            cursor = conn.cursor() # Solo una columna y una fila.
            cursor.execute("SELECT clasificacion FROM Titulo WHERE id_titulo = %s", (titleId,))
            result = cursor.fetchone()
            return result[0] if result else None # result[0] es la clasificación.
        except Error as e:
            print(f"Error en TitleModel.getTitleClassification: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def getRecommendedTitles(self, userId, limit=10):
        """
        Genera recomendaciones de títulos para un usuario.
        Se basa en los géneros de los títulos a los que el usuario ha dado 'Me gusta'.
        Excluye títulos ya gustados o vistos por el usuario.
        """
        conn = getDbConnection()
        if not conn: return []

        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)

            # Obtiene los IDs de género de los títulos que le gustan al usuario.
            queryLikedGenreIds = """
                SELECT tg.id_genero
                FROM Megusta mg
                JOIN Titulo_Genero tg ON mg.id_titulo = tg.id_titulo
                WHERE mg.id_usuario = %s
            """
            cursor.execute(queryLikedGenreIds, (userId,))
            likedGenreIdRows = cursor.fetchall()

            if not likedGenreIdRows:
                # Si el usuario no tiene 'Me gusta', no se pueden generar recomendaciones basadas en gustos.
                print(
                    f"TitleModel.getRecommendedTitles: Usuario {userId} no tiene 'Me gusta'. No se generan recomendaciones basadas en gustos.")
                return [] # Podría implementarse un fallback a "populares generales" aquí.

            genreIds = [row['id_genero'] for row in likedGenreIdRows]
            genreCounts = Counter(genreIds) # Cuenta la frecuencia de cada género gustado.

            if not genreCounts: return [] # Improbable si likedGenreIdRows no estaba vacío.

            mostCommonList = genreCounts.most_common() # Lista de (genreId, count) ordenada por count.
            if not mostCommonList: return []

            # Identifica el o los géneros más comunes (puede haber empates).
            maxCount = mostCommonList[0][1]
            topGenreIds = [genreId for genreId, count in mostCommonList if count == maxCount]

            if not topGenreIds: return []

            # Construye la parte IN (%s, %s, ...) de la query dinámicamente.
            genrePlaceholders = ', '.join(['%s'] * len(topGenreIds))

            # Query para obtener recomendaciones: títulos de los géneros preferidos,
            # excluyendo los ya vistos o gustados, ordenados por calificación y aleatoriedad.
            queryRecommendations = f"""
                SELECT DISTINCT T.id_titulo, T.nombre, T.imagen_url, T.calificación
                FROM Titulo T
                JOIN Titulo_Genero tg ON T.id_titulo = tg.id_titulo
                WHERE tg.id_genero IN ({genrePlaceholders})
                  AND T.id_titulo NOT IN (SELECT id_titulo FROM Megusta WHERE id_usuario = %s)
                  AND T.id_titulo NOT IN (SELECT DISTINCT id_titulo FROM Visto WHERE id_usuario = %s)
                ORDER BY T.calificación DESC, RAND() 
                LIMIT %s
            """
            # RAND() se usa para variar los resultados si hay muchos con la misma calificación.

            paramsForRecommendations = topGenreIds + [userId, userId, limit] # Parámetros para la query.
            cursor.execute(queryRecommendations, tuple(paramsForRecommendations))
            recommendations = cursor.fetchall()

            return recommendations

        except Error as e:
            print(f"Error en TitleModel.getRecommendedTitles: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()