class ListController:
    # Gestiona la lógica de negocio para las listas de reproducción de los usuarios.
    # Interactúa con ListModel y TitleModel para obtener y modificar datos de listas.
    def __init__(self, appController, listModel, titleModel):
        self.appController = appController # Controlador principal de la aplicación.
        self.listModel = listModel # Modelo para operaciones de listas.
        self.titleModel = titleModel # Modelo para operaciones de títulos (usado indirectamente).
        self.currentView = None # Referencia a la vista actual que este controlador maneja.
        self.currentListIdForTitlesView = None # ID de la lista activa en la vista de títulos de lista.
        self.currentListNameForTitlesView = None # Nombre de la lista activa.

    def setCurrentView(self, view):
        # Establece la vista actual que este controlador va a gestionar.
        self.currentView = view
        # Si la vista es para mostrar títulos de una lista específica, se guardan sus detalles.
        if hasattr(view, 'id_lista') and hasattr(view, 'nombre_lista'):
            self.currentListIdForTitlesView = view.id_lista
            self.currentListNameForTitlesView = view.nombre_lista
        else:
            self.currentListIdForTitlesView = None
            self.currentListNameForTitlesView = None

    def loadUserLists(self):
        # Carga y muestra las listas del usuario actualmente logueado.
        # Verifica que la vista actual pueda mostrar listas y que haya un usuario logueado.
        if not self.currentView or not hasattr(self.currentView, 'displayUserLists'):
            return
        userId = self.appController.getCurrentUserId()
        if userId is None:
            self.appController.navigateToLogin() # Redirige a login si no hay usuario.
            return

        lists = self.listModel.getUserLists(userId)
        self.currentView.displayUserLists(lists)

    def handleCreateList(self, listName):
        # Maneja la solicitud de crear una nueva lista para el usuario actual.
        userId = self.appController.getCurrentUserId()
        if userId is None: return # No se puede crear lista sin usuario.

        newListId = self.listModel.createList(userId, listName)
        if newListId:
            self.currentView.showMessage("Éxito", f"Lista '{listName}' creada.", "info")
            self.loadUserLists() # Recarga las listas para mostrar la nueva.
        else:
            self.currentView.showMessage("Error", "No se pudo crear la lista.", "error")

    def handleDeleteList(self, listId):
        # Maneja la solicitud de eliminar una lista existente.
        userId = self.appController.getCurrentUserId() # Asegura que el usuario está logueado, aunque no se use directamente en deleteList.
        if userId is None: return

        success = self.listModel.deleteList(listId)
        if success:
            self.currentView.showMessage("Éxito", "Lista eliminada correctamente.", "info")
            self.loadUserLists() # Recarga para reflejar la eliminación.
        else:
            self.currentView.showMessage("Error", "No se pudo eliminar la lista.", "error")

    def loadTitlesForList(self, listId):
        # Carga y muestra los títulos contenidos en una lista específica.
        # Verifica que la vista actual pueda mostrar títulos y que la lista sea válida.
        if not self.currentView or not hasattr(self.currentView, 'displayTitlesInList'):
            return

        titles = self.listModel.getTitlesInList(listId)
        self.currentView.displayTitlesInList(titles)

    def handleRemoveTitleFromCurrentList(self, listId, titleId):
        # Maneja la solicitud de quitar un título de la lista que se está viendo actualmente.
        success = self.listModel.removeTitleFromList(listId, titleId)
        if success:
            self.currentView.showMessage("Éxito", "Título quitado de la lista.", "info")
            self.loadTitlesForList(listId) # Recarga los títulos de la lista para reflejar el cambio.
        else:
            self.currentView.showMessage("Error", "No se pudo quitar el título de la lista.", "error")

    def showMyLists(self):
        # Navega a la vista que muestra todas las listas del usuario.
        self.appController.showView("ListasView", self)

    def showTitlesInList(self, listId):
        # Navega a la vista que muestra los títulos de una lista específica.
        userId = self.appController.getCurrentUserId()
        if userId is None:
            self.appController.navigateToLogin()
            return

        # Intenta obtener el nombre de la lista para pasarlo a la vista.
        listName = "Lista" # Nombre por defecto.
        userLists = self.listModel.getUserLists(userId)
        for lst in userLists:
            if lst['id_lista'] == listId:
                listName = lst['nombre_lista']
                break

        self.appController.showView("TitulosListaView", self, id_lista=listId, nombre_lista=listName)