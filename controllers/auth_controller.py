class AuthController:
    # Gestiona la lógica de autenticación y registro de usuarios.
    # Interactúa con UserModel y AppController para el flujo de autenticación.
    def __init__(self, appController, userModel):
        self.appController = appController # Controlador principal de la aplicación.
        self.userModel = userModel # Modelo para operaciones de usuario (autenticación, registro).
        self.currentView = None # Referencia a la vista actual (LoginView o RegistroView).

    def setCurrentView(self, view):
        # Establece la vista actual que este controlador va a gestionar.
        self.currentView = view

    def handleLogin(self, email, password):
        # Procesa el intento de inicio de sesión del usuario.
        if not self.currentView: return # No puede operar sin una vista.

        authResult = self.userModel.authenticateUser(email, password)

        # Maneja el resultado de la autenticación.
        if authResult["estado"] == "ok":
            self.appController.setCurrentUser(authResult["id_usuario"], authResult["nombre_usuario"])
            self.currentView.clearFields()
            self.appController.navigateToHome()
        elif authResult["estado"] == "error_db":
            self.currentView.showMessage("Error de Base de Datos", authResult["mensaje"], "error")
        elif authResult["estado"] == "error_user":
             self.currentView.showMessage("Error de Autenticación", authResult["mensaje"], "error")
        elif authResult["estado"] == "error_password":
            self.currentView.showMessage("Error de Autenticación", authResult["mensaje"], "error")
        else:
            # Caso para errores no esperados devueltos por el modelo.
            self.currentView.showMessage("Error Desconocido", "Ocurrió un error inesperado.", "error")

    def handleRegistration(self, username, email, password):
        # Procesa el intento de registro de un nuevo usuario.
        if not self.currentView: return

        regResult = self.userModel.registerUser(username, email, password)

        # Maneja el resultado del registro.
        if regResult["estado"] == "ok":
            self.currentView.showMessage("Registro Exitoso", "Usuario registrado correctamente. Ahora puedes iniciar sesión.")
            self.currentView.clearFields()
            self.requestLoginView() # Navega a la vista de login tras registro exitoso.
        elif regResult["estado"] == "error_exists":
            self.currentView.showMessage("Error de Registro", regResult["mensaje"], "error")
        elif regResult["estado"] == "error_db":
            self.currentView.showMessage("Error de Base de Datos", regResult["mensaje"], "error")
        else:
            self.currentView.showMessage("Error Desconocido", "Ocurrió un error inesperado durante el registro.", "error")

    def requestLoginView(self):
        # Solicita al controlador principal que muestre la vista de login.
        self.appController.navigateToLogin()

    def requestRegistrationView(self):
        # Solicita al controlador principal que muestre la vista de registro.
        self.appController.navigateToRegistration()

    def showLogin(self):
        # Método para que AppController muestre la LoginView con este controlador.
        self.appController.showView("LoginView", self)

    def showRegistration(self):
        # Método para que AppController muestre la RegistroView con este controlador.
        self.appController.showView("RegistroView", self)