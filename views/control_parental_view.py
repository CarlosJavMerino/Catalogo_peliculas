import tkinter as tk
# from tkinter import messagebox # Ya no se usa messagebox directamente aquí para show_message
                                 # Se utiliza showStyledError/Info de appController.
from .base_view import BaseView

class ControlParentalView(BaseView):
    # Vista para gestionar el PIN de control parental (modificar, eliminar).
    def __init__(self, parent, controller, origen_frame_name):
        # 'controller' es ParentalControlController.
        # 'origen_frame_name' es el nombre de la vista desde la que se accedió para poder volver.
        super().__init__(parent, controller.appController)

        self.controllerParental = controller # Instancia de ParentalControlController.
        self.originFrameName = origen_frame_name # Para el botón "Volver".

        self._crearInterfazPrincipalControlParental()

    def _crearInterfazPrincipalControlParental(self):
        # Construye los elementos principales de la interfaz de control parental.
        tk.Label(self.contenidoPrincipalFrame, text="CONTROL PARENTAL", font=("Helvetica", 28, "bold"),
                 fg="#E50914", bg="black").pack(pady=(30, 40)) # Título.

        # Botón para modificar/establecer el PIN.
        tk.Button(self.contenidoPrincipalFrame, text="✏️ Modificar PIN", font=("Helvetica", 14),
                  fg='white', bg='gray20', relief="flat", cursor="hand2", width=20, height=2,
                  command=self._abrirVentanaModificarPin).pack(pady=15)

        # Botón para eliminar el PIN.
        tk.Button(self.contenidoPrincipalFrame, text="🗑️ Eliminar PIN", font=("Helvetica", 14),
                  fg='white', bg='#E50914', relief="flat", cursor="hand2", width=20, height=2,
                  command=self._abrirVentanaConfirmarEliminarPin).pack(pady=15)

        # Lógica para el botón "Volver". Intenta navegar a la vista de origen.
        def _comandoVolverSimplificado():
            if self.originFrameName:
                # Casos especiales para navegación directa.
                if self.originFrameName == "InicioView":
                    self.appController.navigateToHome()
                    return

                try:
                    if self.originFrameName == "BusquedaView":
                        self.appController.navigateToSearch()
                        return
                    if self.originFrameName == "ListasView":
                        self.appController.navigateToMyLists()
                        return
                    if self.originFrameName == "TitulosListaView": # Vuelve a "Mis Listas" desde una lista específica.
                        self.appController.navigateToMyLists()
                        return

                except Exception as e: # Captura cualquier error durante el intento de navegación.
                    print(f"Error navegando de vuelta desde ControlParental a {self.originFrameName}: {e}")
                    pass # Si falla, se recurre a navigateToHome.

            self.appController.navigateToHome() # Fallback: si no hay origen o falla la navegación, va a Inicio.

        tk.Button(self.contenidoPrincipalFrame, text="⬅️ Volver", font=("Helvetica", 14),
                  fg='white', bg='gray30', relief="flat", cursor="hand2", width=20, height=2,
                  command=_comandoVolverSimplificado
                  ).pack(pady=(30, 15))

    def _abrirVentanaModificarPin(self):
        # Abre un diálogo (Toplevel) estilizado para que el usuario ingrese un nuevo PIN.
        ventanaPin = self.appController.createStyledToplevel(
            "Modificar PIN", 350, 200, # Título, ancho, alto.
            parentOverride=self.winfo_toplevel() # Hace el Toplevel modal a la ventana actual.
        )

        tk.Label(ventanaPin, text="Introduce el nuevo PIN (4 dígitos):", font=("Helvetica", 13), fg='white',
                 bg='black').pack(pady=(25, 10))
        entryNuevoPinWidget = tk.Entry(ventanaPin, font=("Helvetica", 12), show='*', width=20, bg="grey25",
                                       fg="white", insertbackground="white", relief="flat") # show='*' oculta la entrada.
        entryNuevoPinWidget.pack(pady=5, ipady=4)
        entryNuevoPinWidget.focus_set() # Pone el foco en el campo de entrada.

        def _guardar():
            # Valida el PIN ingresado y llama al controlador para guardarlo.
            nuevoPin = entryNuevoPinWidget.get().strip()
            if nuevoPin and nuevoPin.isdigit() and len(nuevoPin) == 4: # Validación básica del PIN.
                self.controllerParental.handleUpdatePin(nuevoPin)
                ventanaPin.destroy() # Cierra el diálogo.
            else:
                # Muestra un error estilizado si el PIN no es válido.
                self.appController.showStyledError(
                    "Error de PIN",
                    "El PIN debe ser de 4 dígitos numéricos.",
                    parentForDialog=ventanaPin # Mensaje modal al diálogo de PIN.
                )
                entryNuevoPinWidget.delete(0, tk.END) # Limpia el campo.
                entryNuevoPinWidget.focus_set()

        entryNuevoPinWidget.bind("<Return>", lambda event: _guardar()) # Guardar con Enter.

        tk.Button(ventanaPin, text="Guardar", font=("Helvetica", 12, "bold"), bg='#E50914', fg='white', relief="flat",
                  cursor="hand2", width=10, pady=3, command=_guardar).pack(pady=(20, 15))

    def _abrirVentanaConfirmarEliminarPin(self):
        # Abre un diálogo de confirmación estilizado antes de eliminar el PIN.
        ventanaConfirm = self.appController.createStyledToplevel(
            "Eliminar PIN", 380, 180,
            parentOverride=self.winfo_toplevel()
        )

        tk.Label(ventanaConfirm,
                 text="¿Estás seguro de que deseas eliminar el PIN?\nEsta acción no se puede deshacer.",
                 font=("Helvetica", 12), fg='white', bg='black', wraplength=340, justify="center").pack(pady=(25, 20))

        botonesFrame = tk.Frame(ventanaConfirm, bg='black') # Frame para los botones Sí/No.
        botonesFrame.pack(pady=10)

        callbackExecuted = False # Flag para evitar doble ejecución (ej. Enter y clic).

        def _confirmarEliminar():
            nonlocal callbackExecuted
            if callbackExecuted: return
            callbackExecuted = True
            self.controllerParental.handleDeletePin() # Llama al controlador para eliminar.
            ventanaConfirm.destroy()

        def _cancelarEliminar():
            nonlocal callbackExecuted
            if callbackExecuted: return
            callbackExecuted = True
            ventanaConfirm.destroy() # Simplemente cierra el diálogo.

        btnConfirm = tk.Button(botonesFrame, text="Sí, eliminar", font=("Helvetica", 11, "bold"), bg='#E50914',
                               fg='white',
                               relief="flat", cursor="hand2", width=12, pady=3, command=_confirmarEliminar)
        btnConfirm.pack(side='left', padx=10)

        btnCancel = tk.Button(botonesFrame, text="No, cancelar", font=("Helvetica", 11), bg='gray30', fg='white',
                              relief="flat",
                              cursor="hand2", width=12, pady=3, command=_cancelarEliminar)
        btnCancel.pack(side='right', padx=10)

        btnConfirm.focus_set() # Foco en el botón de confirmación.
        ventanaConfirm.bind("<Escape>", lambda e: _cancelarEliminar()) # Cerrar con Escape.

    def showMessage(self, title, message, type="info", parent=None):
        # Muestra mensajes utilizando los diálogos estilizados del AppController.
        # Esto asegura consistencia en la apariencia de los mensajes.
        _parentDialog = parent if parent and parent.winfo_exists() else self.winfo_toplevel()

        if type == "error":
            self.appController.showStyledError(title, message, parentForDialog=_parentDialog)
        elif type == "warning": # Podría tener su propio styledWarning o usar error.
            self.appController.showStyledError(title, f"Advertencia: {message}", parentForDialog=_parentDialog)
        else: # "info"
            self.appController.showStyledInfo(title, message, parentForDialog=_parentDialog)