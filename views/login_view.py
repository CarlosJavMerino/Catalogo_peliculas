import tkinter as tk
from PIL import Image, ImageTk # Para manejo de imágenes de fondo y logo.
import re                      # Para validación de formato de correo.
import sys
import os

# --- INICIO FUNCIÓN resource_path ---
def resource_path(relative_path):
    """ Obtiene la ruta absoluta a un recurso, funciona para desarrollo y para PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
# --- FIN FUNCIÓN resource_path ---

class LoginView(tk.Frame):
    # Vista para el inicio de sesión de usuarios.
    # No hereda de BaseView porque es una pantalla previa a la navegación principal.
    def __init__(self, parent, controllerAuth):
        super().__init__(parent, bg='black') # 'parent' es el 'container' de App.

        self.appController = controllerAuth.appController # Acceso al AppController para navegación y diálogos.
        self.authController = controllerAuth # Controlador de autenticación.

        # Variables para la imagen de fondo.
        self.fondoOriginal = None
        self.fondoTk = None
        self.logoPhoto = None # Para el logo de Netflix en el formulario.

        # Configura grid para centrar el formulario de login.
        self.grid_rowconfigure(0, weight=1) # Fila superior expandible.
        self.grid_rowconfigure(1, weight=0) # Fila del formulario con tamaño fijo.
        self.grid_rowconfigure(2, weight=1) # Fila inferior expandible.
        self.grid_columnconfigure(0, weight=1) # Columna izquierda expandible.
        self.grid_columnconfigure(1, weight=0) # Columna del formulario con tamaño fijo.
        self.grid_columnconfigure(2, weight=1) # Columna derecha expandible.

        # Carga la imagen de fondo.
        try:
            fondo_path = resource_path("assets/10 may 2025, 17_02_28.png") # <--- MODIFICADO
            self.fondoOriginal = Image.open(fondo_path)
        except FileNotFoundError:
            # Modificamos el mensaje de error para incluir la ruta que intentó usar
            resolved_path = resource_path("assets/10 may 2025, 17_02_28.png")
            print(f"LOGIN_VIEW_STYLED ERROR: No se encontró la imagen de fondo. Intentó buscar en: '{resolved_path}'")
        except Exception as e:
            print(f"LOGIN_VIEW_STYLED ERROR: Cargando imagen de fondo: {e}")


        # Label para mostrar la imagen de fondo. Se coloca detrás de otros widgets.
        self.fondoLabel = tk.Label(self)
        self.fondoLabel.place(x=0, y=0, relwidth=1, relheight=1) # Ocupa todo el frame.

        # Frame para el formulario de login (campos, botones).
        self.formFrame = tk.Frame(self, bg='black') # Fondo negro semi-transparente o sólido.
        self.formFrame.grid(row=1, column=1, sticky="", pady=20) # Centrado en la pantalla.

        self._construirWidgetsEnFormFrame() # Crea los elementos del formulario.

        self.update_idletasks() # Asegura que las dimensiones iniciales estén disponibles.
        self.bind("<Configure>", self._onConfigureEvent) # Para redimensionar el fondo.

        # Redimensiona el fondo después de un breve retraso si las dimensiones iniciales no son válidas.
        if self.winfo_width() > 1 and self.winfo_height() > 1:
            self._redimensionarFondo(self.winfo_width(), self.winfo_height())
        else:
            self.after(50, self._redimensionarFondoInicialDelayed)

    def _onConfigureEvent(self, event):
        # Se llama cuando el tamaño de LoginView cambia. Redimensiona la imagen de fondo.
        if self.fondoOriginal:
            self._redimensionarFondo(event.width, event.height)

    def _redimensionarFondoInicialDelayed(self):
        # Intenta redimensionar el fondo después de que la ventana se haya mostrado.
        if self.winfo_width() > 1 and self.winfo_height() > 1 and self.fondoOriginal:
            self._redimensionarFondo(self.winfo_width(), self.winfo_height())

    def _redimensionarFondo(self, width, height):
        # Redimensiona la imagen de fondo original para ajustarse al tamaño actual de la vista.
        if not self.winfo_exists() or not self.fondoOriginal: return # Si la vista o imagen no existen.
        if width > 1 and height > 1: # Solo si las dimensiones son válidas.
            try:
                imgResized = self.fondoOriginal.resize((width, height), Image.LANCZOS) # LANCZOS para calidad.
                self.fondoTk = ImageTk.PhotoImage(imgResized)
                self.fondoLabel.config(image=self.fondoTk)
            except Exception as e:
                print(f"LOGIN_VIEW_STYLED ERROR: Excepción en _redimensionarFondo: {e}")

    def _construirWidgetsEnFormFrame(self):
        # Crea y organiza los widgets dentro del formFrame.
        try: # Carga el logo de Netflix.
            logo_path = resource_path("assets/Netflix-logo.png") # <--- MODIFICADO
            logoImgPil = Image.open(logo_path).resize((200, 100))
            self.logoPhoto = ImageTk.PhotoImage(logoImgPil)
            tk.Label(self.formFrame, image=self.logoPhoto, bg="black").pack(pady=(30, 25))
        except Exception as e: # Fallback si el logo no carga.
            resolved_logo_path = resource_path("assets/Netflix-logo.png")
            print(f"LOGIN_VIEW_STYLED ERROR: Cargando logo. Intentó buscar en '{resolved_logo_path}'. Error: {e}")
            tk.Label(self.formFrame, text="Netflix", bg="black", fg="red", font=("Arial", 24, "bold")).pack(
                pady=(30, 25))

        # Estilos comunes para labels y entries.
        labelFont = ("Helvetica", 12)
        entryFont = ("Helvetica", 12)
        entryWidth = 35 # Ancho en caracteres.
        entryBg = "grey20"
        entryFg = "white"
        entryRelief = "flat" # Sin borde visible.
        formPadx = 40 # Padding horizontal para los elementos del formulario.
        entryIpady = 6 # Padding interno vertical para entries (altura).
        entryPadyTop = (0, 8) # Padding vertical superior/inferior para entries.
        labelPadyTop = (10, 2)# Padding vertical para labels.

        # Campo de correo electrónico.
        tk.Label(self.formFrame, text="Correo electrónico", font=labelFont, fg=entryFg, bg="black").pack(fill="x",
                                                                                                        padx=formPadx,
                                                                                                        pady=labelPadyTop)
        self.entryCorreo = tk.Entry(self.formFrame, font=entryFont, width=entryWidth,
                                     bg=entryBg, fg=entryFg, insertbackground=entryFg, relief=entryRelief)
        self.entryCorreo.pack(pady=entryPadyTop, ipady=entryIpady, fill="x", padx=formPadx)
        self.entryCorreo.bind("<Return>", lambda e: self._onLoginAttempt()) # Login con Enter.

        # Campo de contraseña.
        tk.Label(self.formFrame, text="Contraseña", font=labelFont, fg=entryFg, bg="black").pack(fill="x",
                                                                                                padx=formPadx,
                                                                                                pady=labelPadyTop)
        self.entryContrasena = tk.Entry(self.formFrame, font=entryFont, show="*", width=entryWidth, # show="*" oculta.
                                         bg=entryBg, fg=entryFg, insertbackground=entryFg, relief=entryRelief)
        self.entryContrasena.pack(pady=entryPadyTop, ipady=entryIpady, fill="x", padx=formPadx)
        self.entryContrasena.bind("<Return>", lambda e: self._onLoginAttempt()) # Login con Enter.

        # Botón de iniciar sesión.
        tk.Button(self.formFrame, text="Iniciar sesión", font=(entryFont[0], entryFont[1], "bold"),
                  fg="white", bg="#e50914", command=self._onLoginAttempt,
                  relief="flat", activebackground="#b0070f", activeforeground="white", bd=0 # Estilo moderno.
                  ).pack(pady=30, ipady=10, fill="x", padx=formPadx)

        # Frame para el enlace de registro.
        enlacesFrame = tk.Frame(self.formFrame, bg="black")
        enlacesFrame.pack(pady=(10, 20), fill="x", padx=formPadx, side="bottom")

        # Enlace para ir a la vista de registro.
        lblRegistro = tk.Label(enlacesFrame, text="¿Primera vez? Regístrate ahora.", font=("Helvetica", 10),
                                fg="white", bg="black", cursor="hand2") # Cursor de mano.
        lblRegistro.pack(side="right") # Alineado a la derecha.
        lblRegistro.bind("<Button-1>", self._onGoToRegister) # Navega al hacer clic.

    def _onLoginAttempt(self):
        # Se llama al intentar iniciar sesión.
        correo = self.entryCorreo.get()
        contrasena = self.entryContrasena.get()

        # Validaciones básicas de los campos.
        if not correo or not contrasena:
            self.appController.showStyledError("Error de Ingreso", "Debes completar ambos campos.",
                                                  parentForDialog=self.winfo_toplevel())
            return
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', correo): # Valida formato de email.
            self.appController.showStyledError("Error de Formato", "Formato de correo no válido.",
                                                  parentForDialog=self.winfo_toplevel())
            return

        self.authController.handleLogin(correo, contrasena) # Llama al controlador para autenticar.

    def _onGoToRegister(self, event=None):
        # Navega a la vista de registro.
        if self.authController and hasattr(self.authController, 'requestRegistrationView'):
            self.authController.requestRegistrationView()
        else: # Fallback si el controlador no está disponible (improbable).
            self.appController.showStyledError("Error de Navegación",
                                                  "No se puede ir a la página de registro en este momento.",
                                                  parentForDialog=self.winfo_toplevel())

    def showMessage(self, title, message, type="info"):
        # Muestra mensajes usando los diálogos estilizados del AppController.
        parentDialog = self.winfo_toplevel() # Asegura que el diálogo sea modal a la ventana de login.

        if type == "error":
            self.appController.showStyledError(title, message, parentForDialog=parentDialog)
        elif type == "warning":
            self.appController.showStyledError(title, f"Advertencia: {message}", parentForDialog=parentDialog)
        else: # "info"
            self.appController.showStyledInfo(title, message, parentForDialog=parentDialog)

    def clearFields(self):
        # Limpia los campos de entrada después de un intento de login o navegación.
        self.entryCorreo.delete(0, tk.END)
        self.entryContrasena.delete(0, tk.END)
        self.entryCorreo.focus_set() # Pone el foco de nuevo en el campo de correo.

    def destroy(self):
        # Limpieza de recursos al destruir la vista.
        print(f"LOGIN_VIEW_STYLED: destroy llamado para {self} (ID: {id(self)})")
        # Libera referencias a imágenes para ayudar al recolector de basura.
        self.fondoOriginal = None
        self.fondoTk = None
        self.logoPhoto = None
        if hasattr(self, 'fondoLabel') and self.fondoLabel.winfo_exists():
            self.fondoLabel.config(image='') # Quita la imagen del label.
        super().destroy()