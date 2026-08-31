class TitleController:
    # Gestiona la lógica de negocio relacionada con la visualización y la interacción con títulos.
    # Esto incluye la página de inicio, detalles del título, "Me Gusta", "Visto", y añadir a listas.
    def __init__(self, appController, titleModel, userModel, listModel):
        self.appController = appController # Controlador principal de la aplicación.
        self.titleModel = titleModel # Modelo para operaciones de títulos.
        self.userModel = userModel # Modelo para operaciones de usuario (ej. PIN para control parental).
        self.listModel = listModel # Modelo para operaciones de listas (ej. añadir título a lista).
        self.currentView = None # Referencia a la vista actual (InicioView, DetallesView).
        self._cachedSeasonsData = None # Caché para datos de temporadas y capítulos de una serie.
        self.currentTitleIdForDetails = None # ID del título actualmente mostrado en DetallesView.

    def setCurrentView(self, view):
        # Establece la vista actual y, si es DetallesView, el ID del título correspondiente.
        self.currentView = view
        if hasattr(view, 'id_titulo'): # Si la vista tiene un 'id_titulo', es DetallesView.
            self.currentTitleIdForDetails = view.id_titulo
        else:
            self.currentTitleIdForDetails = None

    def loadHomeContent(self):
        # Carga el contenido para la pantalla de inicio (InicioView).
        # Esto incluye películas y series populares, y recomendaciones para el usuario.
        if not self.currentView or not hasattr(self.currentView, 'displayCategories'):
            return

        userId = self.appController.getCurrentUserId()
        if userId is None: # Requiere usuario logueado para recomendaciones.
            self.appController.navigateToLogin()
            return

        peliculasPopulares = self.titleModel.getTitlesForHome("película", limit=10)
        seriesPopulares = self.titleModel.getTitlesForHome("serie", limit=10)
        titulosRecomendados = self.titleModel.getRecommendedTitles(userId, limit=10)

        categoriesData = [
            {"title": "🎬 Películas Populares", "items": peliculasPopulares},
            {"title": "📺 Series Populares", "items": seriesPopulares},
        ]
        if titulosRecomendados: # Solo añade la categoría de recomendados si hay resultados.
            categoriesData.append({"title": "🌟 Recomendado para ti", "items": titulosRecomendados})

        # Asegura que la vista todavía existe antes de intentar actualizarla.
        if hasattr(self.currentView, 'winfo_exists') and self.currentView.winfo_exists():
            self.currentView.displayCategories(categoriesData)

    def loadTitleDetailsData(self, titleId):
        # Carga y muestra los detalles completos de un título específico (DetallesView).
        if not self.currentView or not hasattr(self.currentView, 'displayTitleDetails'):
            return

        userId = self.appController.getCurrentUserId()
        if userId is None:
            self.appController.navigateToLogin()
            return

        titleData = self.titleModel.getDetails(titleId)
        if not titleData: # Si no se encuentran datos del título, muestra un estado vacío.
            if hasattr(self.currentView, 'winfo_exists') and self.currentView.winfo_exists():
                self.currentView.displayTitleDetails(None, [], False, False, [], [])
            return

        actorsData = self.titleModel.getActors(titleId)
        isLiked = self.titleModel.isLiked(userId, titleId)
        isWatchedTitle = self.titleModel.isWatched(userId, titleId, chapterId=None) # Para películas o series enteras.

        seasonsFullData = []
        if titleData.get("tipo", "").lower() == "serie": # Procesa temporadas y capítulos solo si es una serie.
            watchedChapterIdsSet = self.titleModel.getWatchedChaptersForTitle(userId, titleId)
            seasonNumbers = self.titleModel.getSeasons(titleId)
            for sNumStr in seasonNumbers:
                chapters = self.titleModel.getChapters(titleId, int(sNumStr))
                chaptersWithWatchStatus = []
                for chapDict in chapters:
                    # Asegura que cada capítulo tenga un ID único para el estado de "visto".
                    chapterUniqueId = chapDict.get('id_capitulo')
                    if chapterUniqueId is None: # Fallback si id_capitulo no está presente.
                        print(
                            f"Advertencia: Capítulo {chapDict.get('nombre')} no tiene 'id_capitulo'. Usando 'numero' como fallback para watch status si es necesario.")
                        chapterUniqueId = chapDict.get('numero')

                    chapDict['is_watched'] = (chapterUniqueId in watchedChapterIdsSet)
                    chapDict['id_capitulo'] = chapterUniqueId # Asegura que el ID usado esté en el dict.
                    chaptersWithWatchStatus.append(chapDict)
                seasonsFullData.append({'number': sNumStr, 'chapters': chaptersWithWatchStatus})

        self._cachedSeasonsData = seasonsFullData # Almacena los datos de temporadas para uso posterior.
        availableUserLists = self.listModel.getUserLists(userId) # Listas del usuario para el popup "Añadir a lista".

        if hasattr(self.currentView, 'winfo_exists') and self.currentView.winfo_exists():
            self.currentView.displayTitleDetails(
                titleData, actorsData, isLiked, isWatchedTitle, seasonsFullData, availableUserLists
            )
        else:
            print("DEBUG: currentView no existe al final de loadTitleDetailsData")


    def getCachedSeasonsData(self):
        # Devuelve los datos de temporadas y capítulos cacheados.
        return self._cachedSeasonsData

    def getCachedSeasonsDataWithUpdatedWatchStatus(self, titleId, chapterIdToggled, newWatchStatus):
        # Actualiza el estado de "visto" de un capítulo específico en la caché y devuelve los datos actualizados.
        # Esto evita recargar todos los datos de la BD solo para un cambio de estado.
        userId = self.appController.getCurrentUserId()
        if not self._cachedSeasonsData or userId is None:
            return self._cachedSeasonsData # Devuelve caché sin modificar si no hay datos o usuario.

        updatedSeasonsData = []
        for seasonData in self._cachedSeasonsData:
            updatedChapters = []
            for chapter in seasonData['chapters']:
                currentChapterId = chapter.get('id_capitulo')
                if currentChapterId == chapterIdToggled:
                    chapter['is_watched'] = newWatchStatus # Actualiza el estado del capítulo afectado.
                updatedChapters.append(chapter)
            updatedSeasonsData.append({'number': seasonData['number'], 'chapters': updatedChapters})

        self._cachedSeasonsData = updatedSeasonsData # Actualiza la caché interna.
        return self._cachedSeasonsData

    def handleToggleLike(self, titleId):
        # Maneja la acción de "Me Gusta" / "No me gusta" para un título.
        userId = self.appController.getCurrentUserId()
        if userId is None: return

        success = self.titleModel.toggleLike(userId, titleId)
        if hasattr(self.currentView, 'winfo_exists') and self.currentView.winfo_exists():
            if success:
                isNowLiked = self.titleModel.isLiked(userId, titleId) # Reconsulta el estado actual.
                self.currentView.updateLikeButtonState(isNowLiked)
            else:
                self.currentView.showMessage("Error", "No se pudo actualizar 'Me gusta'.", "error")

    def handleToggleWatchedTitle(self, titleId):
        # Maneja el estado "Visto" / "No visto" para un título completo (ej. película).
        userId = self.appController.getCurrentUserId()
        if userId is None: return

        success = self.titleModel.toggleWatched(userId, titleId, chapterId=None) # chapterId=None para título entero.
        if hasattr(self.currentView, 'winfo_exists') and self.currentView.winfo_exists():
            if success:
                isNowWatched = self.titleModel.isWatched(userId, titleId, chapterId=None)
                self.currentView.updateWatchedTitleButtonState(isNowWatched)
            else:
                self.currentView.showMessage("Error", "No se pudo actualizar estado 'Visto'.", "error")

    def handleToggleWatchedChapter(self, titleId, chapterId):
        # Maneja el estado "Visto" / "No visto" para un capítulo específico de una serie.
        userId = self.appController.getCurrentUserId()
        if userId is None: return

        # Obtiene el número de la temporada actual de la vista para refrescarla correctamente.
        currentSeasonNumStr = ""
        if hasattr(self.currentView, 'currentSeasonVar') and self.currentView.winfo_exists():
            currentSeasonNumStr = self.currentView.currentSeasonVar.get()
        elif hasattr(self.currentView, 'current_season_var') and self.currentView.winfo_exists(): # Compatibilidad
            currentSeasonNumStr = self.currentView.current_season_var.get()

        success = self.titleModel.toggleWatched(userId, titleId, chapterId)

        if hasattr(self.currentView, 'winfo_exists') and self.currentView.winfo_exists():
            if success:
                isNowWatched = self.titleModel.isWatched(userId, titleId, chapterId)
                self.currentView.updateWatchedChapterButtonState(chapterId, isNowWatched, currentSeasonNumStr)
            else:
                self.currentView.showMessage("Error", "No se pudo actualizar estado 'Visto' del capítulo.", "error")

    def handleAddTitleToList(self, titleId, listId):
        # Maneja la adición de un título a una de las listas del usuario.
        userId = self.appController.getCurrentUserId()
        if userId is None: return

        success = self.listModel.addTitleToList(listId, titleId)
        if hasattr(self.currentView, 'winfo_exists') and self.currentView.winfo_exists():
            if success:
                # Busca el nombre de la lista para un mensaje más amigable.
                listName = "la lista seleccionada"
                allLists = self.listModel.getUserLists(userId)
                for lst in allLists:
                    if lst['id_lista'] == listId:
                        listName = f"«{lst['nombre_lista']}»"
                        break
                self.currentView.showMessage("Éxito", f"Título añadido a {listName} correctamente.", "info")
            else:
                # El modelo puede devolver False si el título ya está en la lista o por otros errores.
                self.currentView.showMessage("Información", "El título ya está en esta lista o hubo un error.",
                                               "warning")

    def showHome(self):
        # Navega a la vista de inicio.
        self.appController.showView("InicioView", self)

    def showDetails(self, titleId):
        # Navega a la vista de detalles de un título.
        # Incluye una comprobación de control parental si el contenido está restringido y el usuario tiene PIN.
        userId = self.appController.getCurrentUserId()
        if not userId:
            self.appController.navigateToLogin()
            return

        classification = self.titleModel.getTitleClassification(titleId)
        userPin = self.userModel.getPin(userId)

        # Si el contenido es para adultos (R, TV-MA) y el usuario tiene un PIN, se solicita el PIN.
        if classification in ["R", "TV-MA"] and userPin:
            print(
                f"TITLE_CONTROLLER: Contenido '{titleId}' restringido ({classification}) y usuario tiene PIN. Pidiendo PIN.")
            self.appController.showPinEntryDialog(
                title="PIN Requerido",
                message="Introduce tu PIN de control parental para ver este contenido:",
                callbackOnSuccess=lambda: self._proceedToShowDetails(titleId) # Llama a mostrar detalles si el PIN es correcto.
            )
        else:
            # Si el contenido es restringido pero no hay PIN, o si no es restringido, se permite el acceso.
            if classification in ["R", "TV-MA"] and not userPin:
                print(
                    f"TITLE_CONTROLLER: Contenido '{titleId}' restringido ({classification}) pero usuario NO tiene PIN. Acceso permitido.")
            elif classification not in ["R", "TV-MA"]:
                print(f"TITLE_CONTROLLER: Contenido '{titleId}' no restringido ({classification}). Acceso permitido.")
            self._proceedToShowDetails(titleId)

    def _proceedToShowDetails(self, titleId):
        # Método auxiliar para mostrar la vista de detalles, llamado después de la lógica de control parental.
        print(f"TITLE_CONTROLLER: Procediendo a mostrar detalles para '{titleId}'")
        self.appController.showView("DetallesView", self, id_titulo=titleId)