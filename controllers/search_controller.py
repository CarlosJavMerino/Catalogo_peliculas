class SearchController:
    # Gestiona la lógica para la funcionalidad de búsqueda de títulos.
    # Interactúa con TitleModel para obtener filtros y resultados de búsqueda.
    def __init__(self, appController, titleModel):
        self.appController = appController # Controlador principal (No se usa directamente aquí, pero es un patrón común)
        self.titleModel = titleModel # Modelo para acceder a datos de títulos, géneros, años.
        self.currentView = None # Referencia a la BusquedaView.
        self.genreNameToIdMap = {} # Mapeo de nombres de género a sus IDs para la búsqueda.

    def setCurrentView(self, view):
        # Establece la vista actual (BusquedaView) que este controlador gestionará.
        self.currentView = view

    def loadInitialSearchFilters(self):
        # Carga las opciones de filtro (géneros, años, tipos) al iniciar la vista de búsqueda.
        if not self.currentView or not hasattr(self.currentView, 'setFilterOptions'):
            return

        genresDict = self.titleModel.getAllGenres() # Obtiene {nombre_genero: id_genero}
        self.genreNameToIdMap = genresDict # Guarda el mapeo para usarlo en la búsqueda.

        years = self.titleModel.getDistinctReleaseYears() # Obtiene lista de años de estreno.
        types = ["película", "serie"] # Tipos de contenido predefinidos.

        self.currentView.setFilterOptions(genresDict, years, types)

    def performSearch(self, searchTerm, genreName, contentTypeStr, yearStr):
        # Realiza una búsqueda de títulos basada en los criterios proporcionados.
        if not self.currentView or not hasattr(self.currentView, 'displaySearchResults'):
            return

        genreId = None
        # Convierte el nombre del género seleccionado a su ID si no es "Todos los Géneros".
        if genreName != "Todos los Géneros" and genreName in self.genreNameToIdMap:
            genreId = self.genreNameToIdMap[genreName]

        # Prepara los valores finales para tipo y año, usando None si se seleccionó "Todos".
        finalContentType = None if contentTypeStr == "Todos los Tipos" else contentTypeStr
        finalYear = None if yearStr == "Todos los Años" else yearStr

        results = self.titleModel.searchTitles(searchTerm, genreId, finalContentType, finalYear)
        self.currentView.displaySearchResults(results)

    def showSearch(self):
        # Solicita al controlador principal que muestre la vista de búsqueda.
        self.appController.showView("BusquedaView", self)