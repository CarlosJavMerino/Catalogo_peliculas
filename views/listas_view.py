import tkinter as tk
from .base_view import BaseView  # Herencia para UI base.

class ListasView(BaseView):
    # Vista para mostrar y gestionar las listas de reproducción del usuario.
    # Permite crear nuevas listas, ver el contenido de listas existentes y eliminarlas.
    def __init__(self, parent, controllerList):
        super().__init__(parent, controllerList.appController)
        self.listController = controllerList  # Instancia de ListController.
        self._crearContenidoPrincipalListas()

    def _crearContenidoPrincipalListas(self):
        # Construye la interfaz principal de la vista de listas.
        contenidoFrameListas = tk.Frame(self.contenidoPrincipalFrame, bg='black')
        contenidoFrameListas.pack(expand=True, fill='both', pady=20)

        tk.Label(contenidoFrameListas, text="MIS LISTAS", fg='#E50914', bg='black',
                 font=("Helvetica", 28, "bold")).pack(pady=(20, 30))

        # Contenedor para los botones que representan cada lista del usuario.
        self.contenedorBotonesListas = tk.Frame(contenidoFrameListas, bg='black')
        self.contenedorBotonesListas.pack(pady=10, padx=40, fill="x")  # Se expande horizontalmente.

        # Botón para crear una nueva lista.
        botonCrear = tk.Button(contenidoFrameListas, text="➕ Crear nueva lista", font=("Helvetica", 14, "bold"),
                               fg='white', bg='#E50914', relief="flat", cursor="hand2",
                               command=self._abrirVentanaCrearLista,  # Abre popup para nombrar la lista.
                               width=25, pady=8)
        botonCrear.pack(side='bottom', pady=(10, 25))  # Se ubica en la parte inferior.

    def displayUserLists(self, listsData):
        # Muestra las listas del usuario.
        # Limpia las listas mostradas anteriormente.
        for widget in self.contenedorBotonesListas.winfo_children():
            widget.destroy()

        if not listsData:
            tk.Label(self.contenedorBotonesListas, text="No tienes ninguna lista creada.",
                     font=("Helvetica", 14), fg="gray60", bg="black").pack(pady=20)
            return

        # Itera sobre los datos de las listas y crea un conjunto de widgets para cada una.
        for lista in listsData:
            idLista = lista['id_lista']
            nombreLista = lista['nombre_lista']

            # Frame para agrupar el botón de la lista y el botón de eliminar.
            filaLista = tk.Frame(self.contenedorBotonesListas, bg='black')
            filaLista.pack(fill='x', pady=8, padx=10)  # Ocupa todo el ancho disponible.
            filaLista.columnconfigure(0, weight=1)  # El botón de la lista se expande.

            # Botón con el nombre de la lista, al hacer clic navega a TitulosListaView.
            tk.Button(filaLista, text=nombreLista, font=("Helvetica", 13),
                      fg='white', bg='gray25', width=30, height=2, relief="flat", anchor='w', cursor="hand2", padx=15,
                      command=lambda listId=idLista: self.appController.navigateToTitlesInList(listId)
                      ).grid(row=0, column=0, sticky="ew", padx=(0, 10))  # "ew" para expandir horizontalmente.

            # Botón para eliminar la lista.
            tk.Button(filaLista, text="🗑️ Eliminar", font=("Helvetica", 10, "bold"),
                      fg='white', bg='#50070a', relief="flat", cursor="hand2",
                      command=lambda listId=idLista, listName=nombreLista: self._confirmarEliminarLista(listId,
                                                                                                        listName)
                      ).grid(row=0, column=1, padx=(5, 0))  # Se coloca a la derecha del nombre.

    def _confirmarEliminarLista(self, listId, listName):
        def _doDelete():
            # Esta función se llamará si el usuario confirma la acción.
            self.listController.handleDeleteList(listId)

        self.appController.showStyledConfirm(
            title="Confirmar Eliminación",
            message=f"¿Estás seguro de que quieres eliminar la lista '{listName}'?",
            yesCallback=_doDelete,
            noCallback=None,
            parentForDialog=self.winfo_toplevel(),  # Modal a la ventana principal de la app.
            yesText="Eliminar",
            noText="Cancelar"
        )

    def _abrirVentanaCrearLista(self):
        # Abre un Toplevel estilizado para que el usuario ingrese el nombre de la nueva lista.
        ventanaPopup = self.appController.createStyledToplevel(
            "Crear nueva lista", 350, 200,  # Título, ancho, alto.
            parentOverride=self.winfo_toplevel()  # Modal a la ventana principal.
        )

        tk.Label(ventanaPopup, text="Nombre de la lista:", font=("Helvetica", 13), fg='white', bg='black').pack(
            pady=(25, 10))
        entryNombreListaWidget = tk.Entry(ventanaPopup, font=("Helvetica", 12), width=25, bg="grey25", fg="white",
                                          insertbackground="white", relief="flat")
        entryNombreListaWidget.pack(pady=5, ipady=4)
        entryNombreListaWidget.focus_set()  # Foco en el campo de entrada.

        callbackExecuted = False  # Para evitar doble ejecución.

        def _confirmarCreacion():
            nonlocal callbackExecuted
            if callbackExecuted: return

            nombre = entryNombreListaWidget.get().strip()  # Obtiene y limpia el nombre.
            if nombre:  # Si el nombre no está vacío.
                callbackExecuted = True  # Marcar como ejecutado antes de la acción
                self.listController.handleCreateList(nombre)  # Llama al controlador.
                ventanaPopup.destroy()
            else:
                # Muestra error si el nombre está vacío.
                # Usar self.showMessage que ya está configurado para diálogos estilizados
                self.showMessage("Error", "El nombre de la lista no puede estar vacío.",
                                 "error", parent=ventanaPopup)  # parent=ventanaPopup hace el error modal al popup
                # No marcar callbackExecuted como True aquí, permitir reintento
                entryNombreListaWidget.focus_set()

        entryNombreListaWidget.bind("<Return>", lambda event: _confirmarCreacion())

        # Botón para confirmar la creación.
        btnCrear = tk.Button(ventanaPopup, text="Crear Lista", font=("Helvetica", 12, "bold"), bg='#E50914',
                             fg='white',
                             relief="flat", cursor="hand2", width=12, pady=4, command=_confirmarCreacion)
        btnCrear.pack(pady=(20, 15))

    def showMessage(self, title, message, type="info", parent=None):
        # Wrapper para mostrar mensajes usando los diálogos estilizados del AppController.
        _parentDialog = parent if parent and parent.winfo_exists() else self.winfo_toplevel()

        if type == "error":
            self.appController.showStyledError(title, message, parentForDialog=_parentDialog)
        elif type == "warning":
            self.appController.showStyledError(title, f"Advertencia: {message}", parentForDialog=_parentDialog)
        else:  # "info"
            self.appController.showStyledInfo(title, message, parentForDialog=_parentDialog)