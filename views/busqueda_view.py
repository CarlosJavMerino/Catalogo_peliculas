import tkinter as tk
from tkinter import ttk
from .base_view import BaseView # Herencia para barra de navegación y carga de imágenes.

class BusquedaView(BaseView):
    # Vista para la funcionalidad de búsqueda de títulos.
    # Permite buscar por término, género, tipo y año.
    def __init__(self, parent, controller):
        # 'controller' es SearchController. 'appController' se obtiene de él.
        appController = controller.appController
        super().__init__(parent, appController)
        self.controller = controller # Instancia de SearchController.

        self._crearFiltrosBusquedaEnContenido()
        self._crearAreaResultadosEnContenido()

    def _crearFiltrosBusquedaEnContenido(self):
        # Crea la sección superior con el título y los campos de filtro.
        tk.Label(self.contenidoPrincipalFrame, text="Buscar Títulos", fg="#E50914", bg="black",
                 font=("Segoe UI", 36, "bold")).pack(pady=(20, 15))

        filtrosContainer = tk.Frame(self.contenidoPrincipalFrame, bg="black")
        filtrosContainer.pack(pady=10) # Contenedor para los widgets de filtro.

        # Campo de entrada para el término de búsqueda.
        self.busquedaEntry = tk.Entry(filtrosContainer, font=("Segoe UI", 14), width=40,
                                       bg="grey25", fg="white", insertbackground="white", relief="flat")
        self.busquedaEntry.grid(row=0, column=0, padx=10, ipady=4) # ipady para altura interna.
        self.busquedaEntry.bind("<Return>", lambda e: self._onSearchButtonClick()) # Buscar al presionar Enter.

        # Dropdown para seleccionar género.
        self.generoVar = tk.StringVar()
        self.generoDropdown = ttk.Combobox(filtrosContainer, textvariable=self.generoVar, state="readonly",
                                          width=20, style="TCombobox") # Usa estilo personalizado de App.
        self.generoDropdown.grid(row=0, column=1, padx=5, ipady=1)

        # Dropdown para seleccionar tipo de contenido (película/serie).
        self.tipoVar = tk.StringVar()
        self.tipoDropdown = ttk.Combobox(filtrosContainer, textvariable=self.tipoVar, state="readonly",
                                        width=20, style="TCombobox")
        self.tipoDropdown.grid(row=0, column=2, padx=5, ipady=1)

        # Dropdown para seleccionar año de estreno.
        self.añoVar = tk.StringVar()
        self.añoDropdown = ttk.Combobox(filtrosContainer, textvariable=self.añoVar, state="readonly",
                                        width=20, style="TCombobox")
        self.añoDropdown.grid(row=0, column=3, padx=5, ipady=1)

        # Botón para iniciar la búsqueda.
        tk.Button(filtrosContainer, text="Buscar", command=self._onSearchButtonClick, bg="#E50914", fg="white",
                  font=("Segoe UI", 12, "bold"), height=1, width=12, relief="flat"
                  ).grid(row=0, column=4, padx=10, ipady=1)

    def _crearAreaResultadosEnContenido(self):
        # Crea el área scrollable donde se mostrarán los resultados de la búsqueda.
        canvasResultadosOuter = tk.Frame(self.contenidoPrincipalFrame, bg="black")
        canvasResultadosOuter.pack(fill="both", expand=True, padx=20, pady=10)

        self.canvasResultados = tk.Canvas(canvasResultadosOuter, bg="black", highlightthickness=0)
        # Scrollbar vertical para el canvas.
        scrollbar = ttk.Scrollbar(canvasResultadosOuter, orient="vertical", command=self.canvasResultados.yview,
                                  style="TScrollbar")
        self.canvasResultados.configure(yscrollcommand=scrollbar.set)

        # Frame interno dentro del canvas que contendrá los resultados.
        self.resultadosContainerFrame = tk.Frame(self.canvasResultados, bg="black")
        # Añade el frame de resultados al canvas.
        self.resultadosWindowId = self.canvasResultados.create_window((0, 0), window=self.resultadosContainerFrame, anchor="nw")

        # Configura el canvas para que se actualice su región de scroll cuando cambie el tamaño del frame interno.
        self.resultadosContainerFrame.bind("<Configure>",
                                           lambda e: self.canvasResultados.configure(
                                               scrollregion=self.canvasResultados.bbox("all")))
        # Configura el frame interno para que su ancho se ajuste al del canvas.
        self.canvasResultados.bind("<Configure>",
                                   lambda e: self.canvasResultados.itemconfig(self.resultadosWindowId, width=e.width))
        # Permite scroll con la rueda del mouse.
        self.canvasResultados.bind("<MouseWheel>",
                                   lambda event: self.canvasResultados.yview_scroll(int(-1 * (event.delta / 120)),
                                                                                    "units"))

        self.canvasResultados.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def setFilterOptions(self, genresMap, yearsList, typesList):
        # Pobla los dropdowns de filtro con los datos obtenidos del controlador.
        # genresMap es un diccionario {nombre_genero: id_genero}.
        if hasattr(self, 'generoDropdown') and self.generoDropdown.winfo_exists():
            self.generoDropdown['values'] = ["Todos los Géneros"] + list(genresMap.keys())
            self.generoVar.set("Todos los Géneros") # Valor por defecto.
        if hasattr(self, 'añoDropdown') and self.añoDropdown.winfo_exists():
            self.añoDropdown['values'] = ["Todos los Años"] + yearsList
            self.añoVar.set("Todos los Años")
        if hasattr(self, 'tipoDropdown') and self.tipoDropdown.winfo_exists():
            self.tipoDropdown['values'] = ["Todos los Tipos"] + typesList
            self.tipoVar.set("Todos los Tipos")

    def _onSearchButtonClick(self):
        # Se llama al hacer clic en "Buscar" o presionar Enter en el campo de búsqueda.
        # Recoge los valores de los filtros y llama al método del controlador para realizar la búsqueda.
        searchTerm = self.busquedaEntry.get()
        genreName = self.generoVar.get()
        contentType = self.tipoVar.get()
        year = self.añoVar.get()
        self.controller.performSearch(searchTerm, genreName, contentType, year)

    def displaySearchResults(self, results):
        # Muestra los resultados de la búsqueda en el área designada.
        # Limpia los resultados anteriores.
        for widget in self.resultadosContainerFrame.winfo_children():
            widget.destroy()

        if not results:
            tk.Label(self.resultadosContainerFrame, text="No se encontraron resultados.",
                     fg="gray", bg="black", font=("Segoe UI", 14)).pack(pady=20)
        else:
            # Itera sobre los resultados y crea un widget para cada título.
            for idx, tituloData in enumerate(results):
                itemFrame = tk.Frame(self.resultadosContainerFrame, bg="#1c1c1c", padx=10, pady=10)
                itemFrame.pack(fill="x", pady=5, padx=5) # Cada resultado en un frame.

                # Label para la imagen del título.
                imgLabel = tk.Label(itemFrame, bg='grey10', width=100, height=150, # Dimensiones fijas para la imagen.
                                    text="...", fg="grey50", font=("Arial", 12)) # Placeholder textual.
                imgLabel.pack(side="left", padx=(0, 10))
                imgUrl = tituloData.get("imagen_url")
                # Clave única para el diccionario de referencias de imágenes en BaseView.
                uniqueKey = (id(imgLabel), imgUrl if imgUrl else f"no_url_busq_{idx}")
                self._requestImageLoadAsync(imgUrl, 100, 150, imgLabel, uniqueKey) # Carga asíncrona.
                # Clic en la imagen navega a los detalles del título.
                imgLabel.bind("<Button-1>", lambda e, idT=tituloData["id_titulo"]: self.appController.navigateToDetails(idT))

                # Frame para la información textual del título (nombre, sinopsis).
                infoFrame = tk.Frame(itemFrame, bg="#1c1c1c")
                infoFrame.pack(side="left", fill="both", expand=True)

                tituloLabelWidget = tk.Label(infoFrame, text=tituloData["nombre"], fg="white", bg="#1c1c1c",
                                         font=("Segoe UI", 16, "bold"), cursor="hand2", anchor="w")
                tituloLabelWidget.pack(fill="x")
                tituloLabelWidget.bind("<Button-1>", lambda e, idT=tituloData["id_titulo"]: self.appController.navigateToDetails(idT))

                sinopsis = tituloData.get("sinopsis", "Sinopsis no disponible.")
                # Ajusta el wraplength de la sinopsis dinámicamente si es posible.
                try:
                    wraplen = self.winfo_width() * 0.6 if self.winfo_width() > 1 else 600
                except tk.TclError: # Puede ocurrir si la ventana no está completamente renderizada.
                    wraplen = 600 # Fallback a un valor fijo.
                tk.Label(infoFrame, text=sinopsis, fg="#cccccc", bg="#1c1c1c", wraplength=wraplen,
                         justify="left", font=("Segoe UI", 11), anchor="w").pack(fill="x", pady=(5, 0))

        self.resultadosContainerFrame.update_idletasks() # Asegura que el frame interno tenga el tamaño correcto.
        if self.canvasResultados.winfo_exists(): # Comprobar que el canvas existe
            self.canvasResultados.config(scrollregion=self.canvasResultados.bbox("all")) # Actualiza la región de scroll.
            self.canvasResultados.yview_moveto(0) # Vuelve al inicio del scroll.

    def showMessage(self, title, message, type="info", parent=None):
        # Muestra mensajes utilizando los diálogos estilizados del AppController.
        # El argumento 'parent' permite especificar un Toplevel padre para el diálogo,
        # si no, se usa el Toplevel de la vista actual.
        _parentDialog = parent if parent and parent.winfo_exists() else self.winfo_toplevel()

        if type == "error":
            self.appController.showStyledError(title, message, parentForDialog=_parentDialog)
        elif type == "warning":
            self.appController.showStyledError(title, f"Advertencia: {message}", parentForDialog=_parentDialog)
        else:
            self.appController.showStyledInfo(title, message, parentForDialog=_parentDialog)

    def destroy(self):
        # Limpieza adicional si es necesario antes de llamar al destroy de la clase base.
        super().destroy()