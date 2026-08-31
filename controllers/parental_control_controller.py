class ParentalControlController:
    # Gestiona la lógica relacionada con el control parental, como la configuración y validación del PIN.
    def __init__(self, appController, userModel):
        self.appController = appController # Controlador principal de la aplicación.
        self.userModel = userModel # Modelo para acceder y modificar datos del PIN del usuario.
        self.currentView = None # Referencia a la ControlParentalView.
        self.originFrameNameOnShow = None # Nombre de la vista desde la que se accedió al control parental.

    def setCurrentView(self, view):
        # Establece la vista actual (ControlParentalView) y recupera el nombre del frame de origen.
        self.currentView = view
        if hasattr(view, 'origen_frame_name'):
            self.originFrameNameOnShow = view.origen_frame_name
        elif hasattr(view, 'originFrameName'): # Compatibilidad con diferentes nombres de atributo.
             self.originFrameNameOnShow = view.originFrameName

    def handleUpdatePin(self, newPin):
        # Maneja la solicitud de actualizar o establecer un nuevo PIN para el usuario.
        userId = self.appController.getCurrentUserId()
        if userId is None: return # Requiere un usuario logueado.

        success = self.userModel.updatePin(userId, newPin)
        if success:
            self.currentView.showMessage("Éxito", "PIN modificado correctamente.", "info")
        else:
            self.currentView.showMessage("Error", "No se pudo modificar el PIN.", "error")

    def handleDeletePin(self):
        # Maneja la solicitud de eliminar el PIN de control parental del usuario.
        userId = self.appController.getCurrentUserId()
        if userId is None: return

        success = self.userModel.deletePin(userId)
        if success:
            self.currentView.showMessage("Éxito", "PIN eliminado correctamente.", "info")
        else:
            self.currentView.showMessage("Error", "No se pudo eliminar el PIN.", "error")

    def showParentalControl(self, originFrameName="InicioView"):
        # Muestra la vista de control parental.
        # Primero verifica si el usuario está logueado y si tiene un PIN configurado.
        userId = self.appController.getCurrentUserId()
        if userId is None:
            self.appController.navigateToLogin()
            return

        userHasPin = self.userModel.getPin(userId) is not None

        # Si el usuario tiene un PIN, se solicita antes de mostrar la configuración.
        if userHasPin:
            self.appController.showPinEntryDialog(
                title="Acceso a Control Parental",
                message="Introduce tu PIN de control parental para continuar:",
                callbackOnSuccess=lambda: self._proceedToShowParentalControl(originFrameName)
            )
        else:
            # Si no hay PIN, se muestra directamente la configuración (para establecer uno).
            self._proceedToShowParentalControl(originFrameName)

    def _proceedToShowParentalControl(self, originFrameName):
        # Auxiliar para mostrar la vista de control parental después de la validación del PIN (si aplica).
        self.appController.showView("ControlParentalView", self, origen_frame_name=originFrameName)