import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog, messagebox
from models.user_model import UserModel
from models.title_model import TitleModel
from models.list_model import ListModel
from controllers.auth_controller import AuthController
from controllers.title_controller import TitleController
from controllers.search_controller import SearchController
from controllers.list_controller import ListController
from controllers.parental_control_controller import ParentalControlController
from views.login_view import LoginView
from views.registro_view import RegistroView
from views.inicio_view import InicioView
from views.detalles_view import DetallesView
from views.busqueda_view import BusquedaView
from views.listas_view import ListasView
from views.lista_titulo_view import TitulosListaView
from views.control_parental_view import ControlParentalView
from views.ayuda_view import AyudaView


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Netflix")
        self.configure(bg='black')
        self.state("zoomed")

        self.currentUserId = None
        self.currentUsername = None
        self.currentViewInstance = None

        self.container = tk.Frame(self, bg='black')
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.viewClasses = {
            "LoginView": LoginView,
            "RegistroView": RegistroView,
            "InicioView": InicioView,
            "DetallesView": DetallesView,
            "BusquedaView": BusquedaView,
            "ListasView": ListasView,
            "TitulosListaView": TitulosListaView,
            "ControlParentalView": ControlParentalView,
            "AyudaView": AyudaView
        }

        self._configureTtkStyles()
        self._initializeModels()
        self._initializeControllers()

        self.navigateToLogin()

    def _configureTtkStyles(self):
        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except tk.TclError:
            print("Tema 'clam' no disponible, usando 'default'.")
            style.theme_use('default')

        comboboxFont = ("Segoe UI", 11)
        style.configure("TCombobox",
                        fieldbackground="black",
                        background="grey15",
                        foreground="white",
                        arrowcolor="white",
                        selectbackground='black',
                        selectforeground='white',
                        font=comboboxFont,
                        padding=(5, 3))
        style.map("TCombobox",
                  fieldbackground=[("readonly", "black"), ("disabled", "grey5")],
                  foreground=[("readonly", "white"), ("disabled", "grey40")],
                  arrowcolor=[("readonly", "white"), ("disabled", "grey40")],
                  background=[("readonly", "grey15"), ("disabled", "grey10")])

        style.configure("TScrollbar",
                        gripcount=0,
                        background="grey25",
                        troughcolor="black",
                        bordercolor="black",
                        darkcolor="black",
                        lightcolor="black",
                        arrowcolor="white",
                        width=14
                        )
        style.map("TScrollbar",
                  background=[('active', 'grey35'), ('!active', 'grey25')],
                  arrowcolor=[('pressed', '#E50914'), ('disabled', 'grey40'), ('!pressed', 'white')],
                  )

    def _initializeModels(self):
        self.userModel = UserModel()
        self.titleModel = TitleModel()
        self.listModel = ListModel()

    def _initializeControllers(self):
        self.authController = AuthController(self, self.userModel)
        self.titleController = TitleController(self, self.titleModel, self.userModel, self.listModel)
        self.searchController = SearchController(self, self.titleModel)
        self.listController = ListController(self, self.listModel, self.titleModel)
        self.parentalControlController = ParentalControlController(self, self.userModel)

    def showView(self, viewClassNameStr, controllerInstance, **viewArgs):
        if self.currentViewInstance:
            print(
                f"APP: Destruyendo vista anterior: {self.currentViewInstance.__class__.__name__} (ID: {id(self.currentViewInstance)})")
            self.currentViewInstance.destroy()
            self.currentViewInstance = None

        print(
            f"APP: Container ({self.container}) info antes de crear {viewClassNameStr}: W={self.container.winfo_width()}, H={self.container.winfo_height()}, Mapped={self.container.winfo_ismapped()}")

        ViewClass = self.viewClasses.get(viewClassNameStr)
        if not ViewClass:
            print(f"Error APP: Clase de Vista '{viewClassNameStr}' no encontrada en el mapeo.")
            self.title(f"Error - Vista {viewClassNameStr} no encontrada")
            return

        print(f"APP: Creando vista: {viewClassNameStr} con controlador {controllerInstance.__class__.__name__}")
        try:
            self.currentViewInstance = ViewClass(self.container, controllerInstance, **viewArgs)
            print(
                f"APP: Vista creada: {self.currentViewInstance.__class__.__name__} (ID: {id(self.currentViewInstance)}), parent: {self.currentViewInstance.master}")
        except Exception as e:
            print(f"APP: ERROR AL CREAR VISTA {viewClassNameStr}: {e}")
            messagebox.showerror("Error Crítico de UI", f"No se pudo crear la vista {viewClassNameStr}.\n{e}")
            if viewClassNameStr != "LoginView":
                self.navigateToLogin()
            return

        self.currentViewInstance.grid(row=0, column=0, sticky="nsew")
        print(f"APP: Vista {viewClassNameStr} colocada con grid.")
        self.currentViewInstance.tkraise()
        print(f"APP: Vista {viewClassNameStr} tkraised.")

        self.currentViewInstance.update_idletasks()
        print(
            f"APP (después de update_idletasks de la instancia): {viewClassNameStr} info: W={self.currentViewInstance.winfo_width()}, H={self.currentViewInstance.winfo_height()}, Mapped={self.currentViewInstance.winfo_ismapped()}")

        self.update()
        print(
            f"APP (después de self.update()): {viewClassNameStr} info: W={self.currentViewInstance.winfo_width()}, H={self.currentViewInstance.winfo_height()}, Mapped={self.currentViewInstance.winfo_ismapped()}")

        if hasattr(controllerInstance, 'setCurrentView'):
            controllerInstance.setCurrentView(self.currentViewInstance)
        elif hasattr(controllerInstance, 'set_current_view'):  # Por si acaso algun controlador usa snake_case
            controllerInstance.set_current_view(self.currentViewInstance)

        if viewClassNameStr == "InicioView" and hasattr(controllerInstance, "loadHomeContent"):
            controllerInstance.loadHomeContent()
        elif viewClassNameStr == "DetallesView" and hasattr(controllerInstance,
                                                            "loadTitleDetailsData") and "id_titulo" in viewArgs:
            controllerInstance.loadTitleDetailsData(viewArgs["id_titulo"])
        elif viewClassNameStr == "BusquedaView" and hasattr(controllerInstance, "loadInitialSearchFilters"):
            controllerInstance.loadInitialSearchFilters()
        elif viewClassNameStr == "ListasView" and hasattr(controllerInstance, "loadUserLists"):
            controllerInstance.loadUserLists()
        elif viewClassNameStr == "TitulosListaView" and hasattr(controllerInstance,
                                                                "loadTitlesForList") and "id_lista" in viewArgs:
            controllerInstance.loadTitlesForList(viewArgs["id_lista"])

    def navigateToLogin(self):
        self.showView("LoginView", self.authController)

    def navigateToRegistration(self):
        self.showView("RegistroView", self.authController)

    def navigateToHome(self):
        if not self.currentUserId:
            self.navigateToLogin()
            return
        self.showView("InicioView", self.titleController)

    def navigateToDetails(self, titleId):
        if not self.currentUserId:
            self.navigateToLogin()
            return
        self.titleController.showDetails(titleId)

    def navigateToSearch(self):
        if not self.currentUserId:
            self.navigateToLogin()
            return
        self.showView("BusquedaView", self.searchController)

    def navigateToMyLists(self):
        if not self.currentUserId:
            self.navigateToLogin()
            return
        self.showView("ListasView", self.listController)

    def navigateToTitlesInList(self, listId):
        if not self.currentUserId:
            self.navigateToLogin()
            return
        self.listController.showTitlesInList(listId)

    def navigateToParentalControl(self, originFrameName=None):
        if not self.currentUserId:
            self.navigateToLogin()
            return
        origin = originFrameName
        if not origin and self.currentViewInstance:
            origin = self.currentViewInstance.__class__.__name__
        elif not origin:
            origin = "InicioView"  # Fallback

        self.parentalControlController.showParentalControl(origin)

    def navigateToHelp(self):
        # AyudaView no tiene un controlador dedicado actualmente, pasa 'self' (App instance)
        self.showView("AyudaView", self)

    def setCurrentUser(self, userId, username):
        self.currentUserId = userId
        self.currentUsername = username
        print(f"Usuario logueado: {self.currentUsername} (ID: {self.currentUserId})")

    def getCurrentUserId(self):
        return self.currentUserId

    def getCurrentUsername(self):
        return self.currentUsername

    def logout(self):
        print("APP: Iniciando logout...")
        self.currentUserId = None
        self.currentUsername = None
        print("APP: Usuario deslogueado (ID y username borrados). Navegando a login...")
        self.navigateToLogin()

    def createStyledToplevel(self, titleStr, widthVal, heightVal, parentOverride=None):
        parentWindow = parentOverride
        if parentWindow is None:
            currentTopLevel = self.winfo_toplevel()
            # Asegurarse de que currentTopLevel no sea el mismo self si self es la ventana principal
            parentWindow = currentTopLevel if currentTopLevel and currentTopLevel.winfo_exists() and currentTopLevel != self else self

        dialog = tk.Toplevel(parentWindow)
        dialog.title(titleStr)
        dialog.configure(bg='black')

        # Hacer el diálogo modal a su ventana padre.
        # Evitar hacer transient(self) si parentWindow es diferente de self.
        if parentWindow != self and isinstance(parentWindow, tk.Toplevel):
            dialog.transient(parentWindow)
        elif parentWindow == self:  # Solo hacer transient a self si es el padre directo
            dialog.transient(self)

        dialog.grab_set()  # Captura el foco
        dialog.resizable(False, False)

        # Centrar el diálogo
        screenWidth = self.winfo_screenwidth()
        screenHeight = self.winfo_screenheight()

        # Determinar la posición x, y para centrar el Toplevel
        # Si el parentOverride es la ventana principal (self) o no se especificó y terminó siendo self
        if parentWindow == self or not isinstance(parentWindow,
                                                  tk.Toplevel) or parentWindow == dialog:  # El último caso es para evitar errores si algo sale mal
            x = (screenWidth // 2) - (widthVal // 2)
            y = (screenHeight // 2) - (heightVal // 2)
        else:  # Si el parentOverride es otro Toplevel, centrar relativo a él
            parentWindow.update_idletasks()  # Asegurar que las dimensiones del padre son actuales
            parentX = parentWindow.winfo_x()
            parentY = parentWindow.winfo_y()
            parentWidth = parentWindow.winfo_width()
            parentHeight = parentWindow.winfo_height()

            x = parentX + (parentWidth // 2) - (widthVal // 2)
            y = parentY + (parentHeight // 2) - (heightVal // 2)

            # Asegurar que el diálogo no se salga de la pantalla
            if x + widthVal > screenWidth: x = screenWidth - widthVal
            if y + heightVal > screenHeight: y = screenHeight - heightVal
            if x < 0: x = 0
            if y < 0: y = 0

        dialog.geometry(f'{widthVal}x{heightVal}+{x}+{y}')
        return dialog

    def showStyledInfo(self, title, message, parentForDialog=None):
        width = 380
        height = 160

        dialog = self.createStyledToplevel(title, width, height, parentOverride=parentForDialog)

        contentFrame = tk.Frame(dialog, bg='black')
        contentFrame.pack(expand=True, fill="both", padx=20, pady=(20, 0))  # Menos padding inferior

        tk.Label(contentFrame, text=message, font=("Helvetica", 12),
                 fg='white', bg='black', wraplength=width - 60,  # Ancho de texto
                 justify="center").pack(pady=(0, 20))

        btnFrame = tk.Frame(dialog, bg='black')  # Frame para el botón
        btnFrame.pack(pady=(0, 20))  # Padding inferior para el frame del botón

        button = tk.Button(btnFrame, text="Aceptar", font=("Helvetica", 11, "bold"),
                           bg='#E50914', fg='white', relief="flat", width=10, pady=3,
                           command=dialog.destroy)
        button.pack()

        dialog.bind("<Return>", lambda e: dialog.destroy())  # Enter para cerrar
        dialog.bind("<Escape>", lambda e: dialog.destroy())  # Escape para cerrar
        button.focus_set()

    def showStyledError(self, title, message, parentForDialog=None):
        width = 380
        height = 160

        dialog = self.createStyledToplevel(title, width, height, parentOverride=parentForDialog)

        contentFrame = tk.Frame(dialog, bg='black')
        contentFrame.pack(expand=True, fill="both", padx=20, pady=(20, 0))

        tk.Label(contentFrame, text=message, font=("Helvetica", 12),
                 fg='white', bg='black', wraplength=width - 60,
                 justify="center").pack(pady=(0, 20))

        btnFrame = tk.Frame(dialog, bg='black')
        btnFrame.pack(pady=(0, 20))

        button = tk.Button(btnFrame, text="Aceptar", font=("Helvetica", 11, "bold"),
                           bg='#E50914', fg='white', relief="flat", width=10, pady=3,
                           command=dialog.destroy)
        button.pack()

        dialog.bind("<Return>", lambda e: dialog.destroy())
        dialog.bind("<Escape>", lambda e: dialog.destroy())
        button.focus_set()

    def showPinEntryDialog(self, title, message, callbackOnSuccess, showEntry=True):
        if not self.currentUserId:  # No se puede verificar PIN sin usuario
            return

        width = 350
        height = 180 if showEntry else 150  # Menor si no hay campo de entrada

        pinDialog = self.createStyledToplevel(title, width, height)

        tk.Label(pinDialog, text=message, font=("Helvetica", 12),
                 fg='white', bg='black', wraplength=width - 40).pack(pady=(20, 10))

        entryPin = None
        if showEntry:
            entryPin = tk.Entry(pinDialog, font=("Helvetica", 12), show="*", width=15,
                                bg="grey25", fg="white", insertbackground="white", relief="flat")
            entryPin.pack(pady=5, ipady=4)
            entryPin.focus_set()

        callbackExecuted = False  # Para evitar doble ejecución

        def _onConfirmPin():
            nonlocal callbackExecuted
            if callbackExecuted: return

            if not showEntry:  # Si es solo un mensaje informativo con botón "Entendido"
                callbackExecuted = True
                pinDialog.destroy()
                if callbackOnSuccess: callbackOnSuccess()
                return

            # Lógica para verificar el PIN
            enteredPin = entryPin.get()
            correctPin = self.userModel.getPin(self.currentUserId)

            if correctPin and enteredPin == correctPin:
                callbackExecuted = True
                pinDialog.destroy()
                if callbackOnSuccess: callbackOnSuccess()
            elif not correctPin and showEntry:  # Intentando verificar PIN pero no hay uno configurado
                # Usar el propio showStyledError para consistencia
                self.showStyledError("Error", "No hay PIN de control parental configurado.", parentForDialog=pinDialog)
            else:  # PIN incorrecto
                self.showStyledError("Error", "PIN incorrecto.", parentForDialog=pinDialog)
                if entryPin:  # Si el entry existe (debería si showEntry es True)
                    entryPin.delete(0, tk.END)
                    entryPin.focus_set()

        if showEntry and entryPin:
            entryPin.bind("<Return>", lambda event: _onConfirmPin())  # Confirmar con Enter

        def _onCancelPin():
            nonlocal callbackExecuted
            if callbackExecuted: return
            callbackExecuted = True
            pinDialog.destroy()  # Simplemente cierra el diálogo

        buttonsFrame = tk.Frame(pinDialog, bg='black')
        buttonsFrame.pack(pady=(15, 10))

        confirmButtonText = "Aceptar" if showEntry else "Entendido"

        btnConfirm = tk.Button(buttonsFrame, text=confirmButtonText, font=("Helvetica", 11, "bold"),
                               bg='#E50914', fg='white', relief="flat", width=10 if showEntry else 12,
                               command=_onConfirmPin)
        btnConfirm.pack(side="left" if showEntry else "none", padx=10)

        if showEntry:
            btnCancel = tk.Button(buttonsFrame, text="Cancelar", font=("Helvetica", 11),
                                  bg='gray30', fg='white', relief="flat", width=8,
                                  command=_onCancelPin)
            btnCancel.pack(side="left", padx=10)
            # Foco en el campo de entrada si existe, sino en el botón de confirmar
            if entryPin:
                entryPin.focus_set()
            else:
                btnConfirm.focus_set()
        else:  # Si no hay entry, el foco va al único botón
            btnConfirm.focus_set()

        pinDialog.bind("<Escape>",
                       lambda e: _onCancelPin() if showEntry else _onConfirmPin())  # Escape: cancela o cierra

    def showStyledConfirm(self, title, message, yesCallback, noCallback=None, parentForDialog=None, yesText="Sí",
                          noText="No", focusYes=True):
        width = 380
        # Ajustar altura basada en la longitud del mensaje para evitar que se corte
        height = 190 if len(message) > 110 else 170  # Aumentado un poco para mensajes más largos

        dialog = self.createStyledToplevel(title, width, height, parentOverride=parentForDialog)

        contentFrame = tk.Frame(dialog, bg='black')
        contentFrame.pack(expand=True, fill="both", padx=20, pady=(20, 0))  # Padding superior para contenido

        tk.Label(contentFrame, text=message, font=("Helvetica", 12),
                 fg='white', bg='black', wraplength=width - 50,  # wraplength ajustado
                 justify="center").pack(pady=(0, 20))  # Padding inferior antes de botones

        btnFrame = tk.Frame(dialog, bg='black')
        btnFrame.pack(pady=(5, 20))  # Padding vertical para el frame de botones

        callbackExecuted = False  # Flag para evitar doble ejecución

        def _onYes():
            nonlocal callbackExecuted
            if callbackExecuted: return
            callbackExecuted = True
            dialog.destroy()
            if yesCallback:
                yesCallback()

        def _onNo():
            nonlocal callbackExecuted
            if callbackExecuted: return
            callbackExecuted = True
            dialog.destroy()
            if noCallback:
                noCallback()
            # Si no hay noCallback, el diálogo simplemente se cierra.

        buttonYes = tk.Button(btnFrame, text=yesText, font=("Helvetica", 11, "bold"),
                              bg='#E50914', fg='white', relief="flat", width=10, pady=4,  # pady para altura botón
                              command=_onYes)
        buttonYes.pack(side="left", padx=15)  # Espaciado entre botones

        buttonNo = tk.Button(btnFrame, text=noText, font=("Helvetica", 11),
                             bg='gray30', fg='white', relief="flat", width=10, pady=4,
                             command=_onNo)
        buttonNo.pack(side="left", padx=15)

        # Manejo de eventos de teclado
        dialog.bind("<Escape>", lambda e: _onNo())  # Escape siempre es "No" o "Cancelar"

        if focusYes:
            buttonYes.focus_set()
            # Si "Sí" tiene el foco, Enter presiona "Sí"
            dialog.bind("<Return>", lambda e, b=buttonYes: b.invoke())
        else:
            buttonNo.focus_set()
            # Si "No" tiene el foco, Enter presiona "No"
            dialog.bind("<Return>", lambda e, b=buttonNo: b.invoke())


if __name__ == "__main__":
    app = App()
    app.mainloop()