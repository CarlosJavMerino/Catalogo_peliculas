import tkinter as tk
from tkinter import ttk
from .base_view import BaseView # Herencia para UI base y carga de imágenes.

class DetallesView(BaseView):
    # Vista para mostrar información detallada de un título (película o serie).
    # Incluye sinopsis, reparto, calificación, y si es una serie, temporadas y capítulos.
    def __init__(self, parent, controllerTitle, id_titulo):
        # 'controllerTitle' es TitleController.
        # 'id_titulo' es el ID del título cuyos detalles se van a mostrar.
        super().__init__(parent, controllerTitle.appController)

        self.titleController = controllerTitle # Instancia de TitleController.
        self.idTitulo = id_titulo # ID del título actual.

        # Canvas principal para el scroll vertical de toda la página de detalles.
        self.mainCanvasDetalles = tk.Canvas(self.contenidoPrincipalFrame, bg="black", highlightthickness=0)
        scroll_y = ttk.Scrollbar(self.contenidoPrincipalFrame, orient="vertical", command=self.mainCanvasDetalles.yview,
                                 style="TScrollbar")
        self.mainCanvasDetalles.configure(yscrollcommand=scroll_y.set)

        # Frame interno scrollable que contendrá todos los elementos de la vista de detalles.
        self.scrollableFrameDetalles = tk.Frame(self.mainCanvasDetalles, bg="black")
        self.scrollableWindowIdDetalles = self.mainCanvasDetalles.create_window((0, 0),
                                                                                window=self.scrollableFrameDetalles,
                                                                                anchor="nw")

        # Vinculación de eventos para el manejo del scroll y redimensionamiento.
        self.scrollableFrameDetalles.bind("<Configure>", lambda e: self.mainCanvasDetalles.configure(
            scrollregion=self.mainCanvasDetalles.bbox("all")))
        self.mainCanvasDetalles.bind("<Configure>", lambda e: self.mainCanvasDetalles.itemconfig(
            self.scrollableWindowIdDetalles, width=e.width))
        self.mainCanvasDetalles.bind("<MouseWheel>", self._onMousewheelMainCanvasDetalles) # Scroll con rueda.

        self.mainCanvasDetalles.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

    def _onMousewheelMainCanvasDetalles(self, event):
        # Maneja el evento de la rueda del mouse para el scroll vertical del canvas principal.
        if self.mainCanvasDetalles.winfo_exists(): # Comprueba si el widget aún existe.
            self.mainCanvasDetalles.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def displayTitleDetails(self, titleData, actorsData, isLiked, isWatchedTitle, seasonsData, availableLists):
        # Muestra todos los detalles del título en la interfaz.
        # Limpia el contenido anterior.
        for widget in self.scrollableFrameDetalles.winfo_children():
            widget.destroy()

        if not titleData: # Si no hay datos del título (ej. error al cargar).
            tk.Label(self.scrollableFrameDetalles, text="Detalles del título no disponibles.",
                     fg="white", bg="black", font=("Helvetica", 16)).pack(pady=50)
            self.scrollableFrameDetalles.update_idletasks()
            if self.mainCanvasDetalles.winfo_exists():
                self.mainCanvasDetalles.config(scrollregion=self.mainCanvasDetalles.bbox("all"))
            return

        # Frame principal para organizar el contenido de los detalles.
        detailsContentFrame = tk.Frame(self.scrollableFrameDetalles, bg="black")
        detailsContentFrame.pack(pady=20, padx=30, fill="x")

        # Fila superior: imagen de portada a la izquierda, información principal a la derecha.
        topRowFrame = tk.Frame(detailsContentFrame, bg="black")
        topRowFrame.pack(fill="x", pady=(0, 20))

        # Label para la imagen de portada.
        self.coverLabelWidget = tk.Label(topRowFrame, bg="grey10", width=220, height=330, text="Cargando...",
                                         fg="grey50", font=("Arial", 12)) # Placeholder.
        self.coverLabelWidget.pack(side="left", anchor="nw", padx=(0, 25))

        coverImageUrl = titleData.get("imagen_url")
        coverImageKey = ("cover_img", coverImageUrl if coverImageUrl else f"no_url_cover_det_{self.idTitulo}")
        self._requestImageLoadAsync(coverImageUrl, 220, 330, self.coverLabelWidget, coverImageKey) # Carga asíncrona.

        # Frame para la información a la derecha de la portada.
        infoRightFrame = tk.Frame(topRowFrame, bg="black")
        infoRightFrame.pack(side="left", fill="x", expand=True, anchor="nw")

        # Nombre del título.
        tk.Label(infoRightFrame, text=titleData.get("nombre", "Título Desconocido"), font=("Helvetica", 28, "bold"),
                 fg="white", bg="black", anchor="w", justify="left").pack(fill="x", pady=(0, 5))

        # Información breve: año, duración, tipo.
        infoTxt = f"{titleData.get('año_estreno', 'N/A')} · {titleData.get('duración', 'N/A')} min · {titleData.get('tipo', 'N/A').capitalize()}"
        tk.Label(infoRightFrame, text=infoTxt, font=("Helvetica", 13),
                 fg="gray85", bg="black", anchor="w").pack(fill="x")

        # Clasificación y valoración.
        tk.Label(infoRightFrame,
                 text=f"Clasificación: {titleData.get('clasificacion', 'N/A')} · Valoración: {titleData.get('calificación', 'N/A')}/10",
                 font=("Helvetica", 13), fg="gray85", bg="black", anchor="w").pack(fill="x", pady=(2, 15))

        # Sinopsis.
        tk.Label(infoRightFrame, text="Sinopsis", font=("Helvetica", 16, "bold"),
                 fg="white", bg="black", anchor="w").pack(fill="x", pady=(10, 2))
        sinopsisText = titleData.get("sinopsis", "No disponible.")
        try: # Calcula el wraplength para la sinopsis.
            infoRightFrame.update_idletasks() # Asegura que el frame tenga dimensiones.
            sinopsisWraplength = max(200, infoRightFrame.winfo_width() - 20) if infoRightFrame.winfo_width() > 20 else 500
        except tk.TclError:
            sinopsisWraplength = 500 # Fallback.
        tk.Label(infoRightFrame, text=sinopsisText, font=("Helvetica", 12),
                 fg="white", bg="black", wraplength=sinopsisWraplength, justify="left", anchor="w").pack(fill="x",
                                                                                                         pady=(2, 15))
        # Reparto.
        tk.Label(infoRightFrame, text="Reparto", font=("Helvetica", 16, "bold"),
                 fg="white", bg="black", anchor="w").pack(fill="x", pady=(10, 2))
        actorNames = [actor['nombre'] for actor in actorsData] if actorsData else ["No hay información."]
        tk.Label(infoRightFrame, text=", ".join(actorNames), font=("Helvetica", 12),
                 fg="white", bg="black", wraplength=sinopsisWraplength, justify="left", anchor="w").pack(fill="x",
                                                                                                         pady=(2, 15))
        # Frame para botones de acción (Visto, Añadir a lista, Me gusta).
        actionsFrame = tk.Frame(infoRightFrame, bg="black")
        actionsFrame.pack(fill="x", pady=(15, 10), anchor="w")

        # Botón "Marcar como visto" (para el título completo, ej. película).
        vistoText = "✔ Visto" if isWatchedTitle else "Marcar como visto"
        vistoBg = "red" if isWatchedTitle else "#222222" # Rojo si está visto.
        self.btnVistoTitulo = tk.Button(actionsFrame, text=vistoText, font=("Helvetica", 11),
                                        bg=vistoBg, fg="white", relief="flat", padx=12, pady=6,
                                        command=lambda: self.titleController.handleToggleWatchedTitle(self.idTitulo))
        self.btnVistoTitulo.pack(side="left", padx=(0, 8))

        # Botón "Añadir a lista".
        tk.Button(actionsFrame, text="Añadir a lista", font=("Helvetica", 11),
                  bg="#222222", fg="white", relief="flat", padx=12, pady=6,
                  command=lambda: self.showAddToListPopup(availableLists) # Abre popup para seleccionar lista.
                  ).pack(side="left", padx=8)

        # Botón "Me gusta".
        likeText = "❤️ Me gusta" if isLiked else "🤍 Me gusta" # Cambia icono y texto.
        likeBg = "red" if isLiked else "#222222"
        self.btnMegusta = tk.Button(actionsFrame, text=likeText, font=("Helvetica", 11),
                                    bg=likeBg, fg="white", relief="flat", padx=12, pady=6,
                                    command=lambda: self.titleController.handleToggleLike(self.idTitulo))
        self.btnMegusta.pack(side="left", padx=8)

        # Si el título es una serie, muestra la sección de temporadas y capítulos.
        if titleData.get("tipo", "").lower() == "serie":
            self._displaySeriesSection(seasonsData)

        # Botón para volver a la página de inicio.
        tk.Button(self.scrollableFrameDetalles, text="⟵ Volver a Inicio", font=("Helvetica", 12),
                  bg="#333333", fg="white", relief="flat", padx=12, pady=6,
                  command=self.appController.navigateToHome # Llama al método de navegación del AppController.
                  ).pack(pady=(30, 20), anchor="w", padx=30)

        self.scrollableFrameDetalles.update_idletasks()
        if self.mainCanvasDetalles.winfo_exists():
            self.mainCanvasDetalles.config(scrollregion=self.mainCanvasDetalles.bbox("all"))
            self.mainCanvasDetalles.yview_moveto(0) # Scroll al inicio.

    def _displaySeriesSection(self, seasonsData):
        # Muestra la sección para seleccionar temporadas y ver capítulos de una serie.
        seriesFrame = tk.Frame(self.scrollableFrameDetalles, bg="black")
        seriesFrame.pack(fill="x", padx=30, pady=(20, 0))

        tk.Label(seriesFrame, text="Temporadas y Capítulos", font=("Helvetica", 18, "bold"),
                 fg="white", bg="black").pack(anchor="w", pady=(0, 10))

        if not seasonsData: # Si no hay datos de temporadas.
            tk.Label(seriesFrame, text="No hay información de temporadas para esta serie.",
                     font=("Helvetica", 11), fg="gray70", bg="black").pack(anchor="w", pady=8)
            return

        # Frame para el selector de temporada (Label + Combobox).
        seasonSelectorFrame = tk.Frame(seriesFrame, bg="black")
        seasonSelectorFrame.pack(fill="x", pady=(0, 10))
        tk.Label(seasonSelectorFrame, text="Temporada:", font=("Helvetica", 12),
                 fg="white", bg="black").pack(side="left", padx=(0, 10))

        seasonNumbers = [s['number'] for s in seasonsData] # Lista de números de temporada.
        self.currentSeasonVar = tk.StringVar(value=seasonNumbers[0] if seasonNumbers else "") # Valor inicial.

        # Combobox para seleccionar la temporada.
        self.seasonCombobox = ttk.Combobox(seasonSelectorFrame, values=seasonNumbers,
                                           textvariable=self.currentSeasonVar, width=5,
                                           font=("Helvetica", 11), style="TCombobox", state="readonly")
        self.seasonCombobox.pack(side="left")
        self.seasonCombobox.bind("<<ComboboxSelected>>", self._onSeasonSelected) # Evento al seleccionar.

        # Frame donde se mostrarán los capítulos de la temporada seleccionada.
        self.chaptersDisplayFrame = tk.Frame(seriesFrame, bg="black")
        self.chaptersDisplayFrame.pack(fill="x", expand=True, pady=(5, 0))

        if seasonNumbers: # Si hay temporadas, puebla los capítulos de la primera.
            self._populateChaptersForSeason(self.currentSeasonVar.get(), seasonsData)

    def _onSeasonSelected(self, event=None):
        # Se llama cuando se selecciona una nueva temporada en el Combobox.
        selectedSeasonNum = self.currentSeasonVar.get()
        # Obtiene los datos de todas las temporadas (cacheados en el controlador) para no recargar de BD.
        allSeasonsData = self.titleController.getCachedSeasonsData()
        if allSeasonsData:
            self._populateChaptersForSeason(selectedSeasonNum, allSeasonsData)

    def _populateChaptersForSeason(self, seasonNumStr, allSeasonsData):
        # Muestra los capítulos para la temporada seleccionada.
        # Limpia los capítulos anteriores.
        for widget in self.chaptersDisplayFrame.winfo_children():
            widget.destroy()

        # Encuentra los datos de la temporada seleccionada dentro de allSeasonsData.
        targetSeasonData = None
        for season in allSeasonsData:
            if str(season['number']) == seasonNumStr:
                targetSeasonData = season
                break
        chapters = targetSeasonData.get('chapters', []) if targetSeasonData else []

        if not chapters: # Si no hay capítulos para esta temporada.
            tk.Label(self.chaptersDisplayFrame, text="No hay capítulos para esta temporada.",
                     font=("Helvetica", 11), fg="gray70", bg="black").pack(pady=8)
            return

        # Itera sobre los capítulos y crea un widget para cada uno.
        for chapterData in chapters:
            isWatched = chapterData.get('is_watched', False) # Estado "visto" del capítulo.
            chapFrame = tk.Frame(self.chaptersDisplayFrame, bg="#1c1c1c", pady=6, padx=8) # Frame para cada capítulo.
            chapFrame.pack(fill="x", pady=3)
            # Información del capítulo (número, nombre, duración).
            tk.Label(chapFrame,
                     text=f"{chapterData['numero']}. {chapterData['nombre']} ({chapterData.get('duración', 'N/A')} min)",
                     font=("Helvetica", 11), fg="white", bg="#1c1c1c", anchor="w").pack(side="left", fill="x",
                                                                                        expand=True)
            # Botón para marcar/desmarcar capítulo como visto.
            watchBtnText = "✔ Visto" if isWatched else "Marcar"
            watchBtnBg = "red" if isWatched else "#333333"
            chapterIdForToggle = chapterData.get('id_capitulo') # ID del capítulo para el toggle.
            # El comando del botón llama al controlador para cambiar el estado.
            # Se verifica que chapterIdForToggle no sea None antes de llamar.
            btnCap = tk.Button(chapFrame, text=watchBtnText, font=("Helvetica", 9),
                               bg=watchBtnBg, fg="white", relief="flat", padx=8, pady=3,
                               command=lambda chId=chapterIdForToggle:
                               self.titleController.handleToggleWatchedChapter(self.idTitulo, chId)
                               if chId is not None else None)
            btnCap.pack(side="right", padx=5)

    def updateLikeButtonState(self, isLiked):
        # Actualiza la apariencia del botón "Me gusta" según el estado.
        likeText = "❤️ Me gusta" if isLiked else "🤍 Me gusta"
        likeBg = "red" if isLiked else "#222222"
        if hasattr(self, 'btnMegusta') and self.btnMegusta.winfo_exists():
            self.btnMegusta.config(text=likeText, bg=likeBg)

    def updateWatchedTitleButtonState(self, isWatched):
        # Actualiza la apariencia del botón "Marcar como visto" para el título completo.
        vistoText = "✔ Visto" if isWatched else "Marcar como visto"
        vistoBg = "red" if isWatched else "#222222"
        if hasattr(self, 'btnVistoTitulo') and self.btnVistoTitulo.winfo_exists():
            self.btnVistoTitulo.config(text=vistoText, bg=vistoBg)

    def updateWatchedChapterButtonState(self, chapterId, isWatched, seasonNumberStrToRefresh):
        # Actualiza la lista de capítulos después de que el estado "visto" de un capítulo cambia.
        # Obtiene los datos de temporada actualizados del controlador (que maneja la caché).
        allSeasonsData = self.titleController.getCachedSeasonsDataWithUpdatedWatchStatus(
            self.idTitulo, chapterId, isWatched
        )
        # Vuelve a poblar los capítulos de la temporada actual para reflejar el cambio.
        if allSeasonsData and hasattr(self, 'chaptersDisplayFrame') and self.chaptersDisplayFrame.winfo_exists():
            self._populateChaptersForSeason(seasonNumberStrToRefresh, allSeasonsData)

    def showAddToListPopup(self, availableLists):
        # Muestra un popup para que el usuario seleccione una lista a la cual añadir el título actual.
        if not availableLists: # Si el usuario no tiene listas creadas.
            self.appController.showStyledInfo(
                "Sin listas",
                "No tienes listas creadas aún.\nPuedes crear una desde 'Mis Listas'.",
                parentForDialog=self.winfo_toplevel() # Modal a la ventana de detalles.
            )
            return

        # Crea el Toplevel estilizado a través del AppController.
        popup = self.appController.createStyledToplevel(
            "Añadir a lista", 350, 220, # Título, ancho, alto.
            parentOverride=self.winfo_toplevel()
        )

        tk.Label(popup, text="Selecciona una lista:", bg="black", fg="white", font=("Helvetica", 13)).pack(
            pady=(20, 10))

        # Prepara las opciones para el OptionMenu.
        optionsDict = {lst['nombre_lista']: lst['id_lista'] for lst in availableLists if
                       'nombre_lista' in lst and 'id_lista' in lst} # {nombre: id}

        if not optionsDict: # Caso improbable si availableLists no estaba vacío pero no tenía el formato esperado.
            tk.Label(popup, text="No hay listas válidas disponibles.", bg="black", fg="gray70",
                     font=("Helvetica", 11)).pack(pady=10)
            tk.Button(popup, text="Cerrar", command=popup.destroy, bg="#333", fg="white", relief="flat", width=10,
                      pady=4, font=("Helvetica", 10)).pack(pady=(10, 15))
            return

        self.selectedListVarPopup = tk.StringVar(value=next(iter(optionsDict.keys()), "")) # Selecciona la primera lista por defecto.

        # OptionMenu para seleccionar la lista.
        listOptionMenu = tk.OptionMenu(popup, self.selectedListVarPopup, *optionsDict.keys())
        listOptionMenu.config(bg="#222", fg="white", font=("Helvetica", 12), relief="flat", width=20,
                              highlightthickness=0, activebackground="#333", activeforeground="white")
        if listOptionMenu["menu"]: # Estilo del menú desplegable.
            listOptionMenu["menu"].config(bg="#222", fg="white", font=("Helvetica", 11), relief="flat")
        listOptionMenu.pack(pady=8, ipady=3)

        callbackExecuted = False # Para evitar doble ejecución.

        def _onAddConfirm():
            # Se llama al confirmar la adición del título a la lista.
            nonlocal callbackExecuted
            if callbackExecuted: return
            callbackExecuted = True

            selectedListName = self.selectedListVarPopup.get()
            if not selectedListName: # Si no se seleccionó ninguna lista.
                # Usa el showMessage local, que a su vez podría llamar a appController.showStyledError
                self.showMessage("Sin selección", "Por favor, selecciona una lista.", "warning", parent=popup)
                callbackExecuted = False # Permite reintentar.
                return
            selectedListId = optionsDict.get(selectedListName) # Obtiene el ID de la lista seleccionada.
            if selectedListId is not None:
                self.titleController.handleAddTitleToList(self.idTitulo, selectedListId) # Llama al controlador.
            popup.destroy()

        # Botón de Aceptar.
        btnAccept = tk.Button(popup, text="Aceptar", command=_onAddConfirm, bg="red", fg="white",
                              font=("Helvetica", 12, "bold"),
                              relief="flat", width=10, pady=4)
        btnAccept.pack(pady=(15, 20))

        popup.bind("<Return>", lambda event: _onAddConfirm())
        listOptionMenu.focus_set()

    def showMessage(self, title, message, type="info", parent=None):
        # Wrapper para mostrar mensajes usando los diálogos estilizados del AppController.
        _parentDialog = parent if parent and parent.winfo_exists() else self.winfo_toplevel()

        if type == "error":
            self.appController.showStyledError(title, message, parentForDialog=_parentDialog)
        elif type == "warning":
            self.appController.showStyledError(title, f"Advertencia: {message}", parentForDialog=_parentDialog)
        else:
            self.appController.showStyledInfo(title, message, parentForDialog=_parentDialog)

    def destroy(self):
        # Limpieza específica de DetallesView si fuera necesaria.
        super().destroy()