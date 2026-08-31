import tkinter as tk
from PIL import Image, ImageTk # Para manejo de imágenes.
import re                      # Para validaciones de formato (email, contraseña).
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

class RegistroView(tk.Frame):
    # Vista para el registro de nuevos usuarios.
    # Similar a LoginView en estructura y manejo de fondo, no hereda de BaseView.
    def __init__(self, parent, controllerAuth):
        super().__init__(parent, bg='black')
        self.appController = controllerAuth.appController
        self.authController = controllerAuth

        # Variables para la imagen de fondo y logo.
        self.fondoOriginal = None
        self.fondoTk = None
        self.logoPhoto = None

        # Configuración de grid para centrar el formulario.
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)

        # Carga la imagen de fondo.
        try:
            fondo_path = resource_path("assets/Formas rojas sobre fondo negro.png") # <--- MODIFICADO
            self.fondoOriginal = Image.open(fondo_path)
        except FileNotFoundError:
            resolved_path = resource_path("assets/Formas rojas sobre fondo negro.png")
            print(f"REGISTRO_VIEW ERROR: No se encontró '{resolved_path}'")
        except Exception as e:
            print(f"REGISTRO_VIEW ERROR: Cargando imagen de fondo: {e}")


        # Label para la imagen de fondo.
        self.fondoLabel = tk.Label(self)
        self.fondoLabel.place(x=0, y=0, relwidth=1, relheight=1)

        self._crearYPosicionarFormFrame() # Crea el frame del formulario.
        self._construirWidgetsEnFormFrame() # Añade los widgets al formulario.

        self.update_idletasks()
        self.bind("<Configure>", self._onConfigureEvent) # Para redimensionar fondo.

        # Redimensiona el fondo inicialmente o tras un retraso.
        if self.winfo_width() > 1 and self.winfo_height() > 1:
            self._redimensionarFondo(self.winfo_width(), self.winfo_height())
        else:
            self.after(50, self._redimensionarFondoInicialDelayed)

    def _crearYPosicionarFormFrame(self):
        # Crea el frame que contendrá los elementos del formulario de registro.
        self.formFrame = tk.Frame(self, bg='black') # Considerar un alpha para transparencia si el diseño lo requiere.
        self.formFrame.grid(row=1, column=1, sticky="", pady=20) # Centrado.

    def _onConfigureEvent(self, event):
        # Redimensiona el fondo cuando cambia el tamaño de la vista.
        if self.fondoOriginal:
            self._redimensionarFondo(event.width, event.height)

    def _redimensionarFondoInicialDelayed(self):
        # Intento de redimensionar el fondo después de que la ventana sea visible.
        if self.winfo_width() > 1 and self.winfo_height() > 1 and self.fondoOriginal:
            self._redimensionarFondo(self.winfo_width(), self.winfo_height())

    def _redimensionarFondo(self, width, height):
        # Lógica para redimensionar la imagen de fondo.
        if not self.winfo_exists() or not self.fondoOriginal: return
        if width > 1 and height > 1:
            try:
                imagenRedimensionada = self.fondoOriginal.resize((width, height), Image.LANCZOS)
                self.fondoTk = ImageTk.PhotoImage(imagenRedimensionada)
                self.fondoLabel.config(image=self.fondoTk)
            except Exception as e:
                print(f"REGISTRO_VIEW ERROR: Excepción en _redimensionarFondo: {e}")

    def _construirWidgetsEnFormFrame(self):
        # Crea y añade los widgets (logo, labels, entries, botones) al formulario.
        try: # Logo.
            logo_path = resource_path("assets/Netflix-logo.png") # <--- MODIFICADO
            logoImgPil = Image.open(logo_path).resize((200, 100))
            self.logoPhoto = ImageTk.PhotoImage(logoImgPil)
            tk.Label(self.formFrame, image=self.logoPhoto, bg="black").pack(pady=(30, 20))
        except Exception as e: # Fallback para el logo.
            resolved_logo_path = resource_path("assets/Netflix-logo.png")
            print(f"REGISTRO_VIEW ERROR: Cargando logo. Intentó buscar en '{resolved_logo_path}'. Error: {e}")
            tk.Label(self.formFrame, text="Netflix Logo", bg="black", fg="red", font=("Arial", 24, "bold")).pack(
                pady=(30, 20))

        # Estilos comunes para los widgets del formulario.
        labelFont = ("Helvetica", 12)
        entryFont = ("Helvetica", 12)
        entryWidth = 35
        entryBg = "grey20"
        entryFg = "white"
        entryRelief = "flat"
        formPadx = 40
        entryIpady = 6
        entryPadyTop = (0, 8)
        labelPadyTop = (8, 2) # Un poco menos de padding superior para labels que en login.

        # Campo de correo electrónico.
        tk.Label(self.formFrame, text="Correo electrónico", font=labelFont, fg=entryFg, bg="black").pack(fill="x",
                                                                                                        padx=formPadx,
                                                                                                        pady=labelPadyTop)
        self.entryCorreo = tk.Entry(self.formFrame, font=entryFont, width=entryWidth, bg=entryBg, fg=entryFg,
                                     insertbackground=entryFg, relief=entryRelief)
        self.entryCorreo.pack(pady=entryPadyTop, ipady=entryIpady, fill="x", padx=formPadx)
        # Pasa el foco al siguiente campo al presionar Enter.
        self.entryCorreo.bind("<Return>", lambda e: self.entryUsuario.focus_set())

        # Campo de nombre de usuario.
        tk.Label(self.formFrame, text="Nombre de usuario", font=labelFont, fg=entryFg, bg="black").pack(fill="x",
                                                                                                         padx=formPadx,
                                                                                                         pady=labelPadyTop)
        self.entryUsuario = tk.Entry(self.formFrame, font=entryFont, width=entryWidth, bg=entryBg, fg=entryFg,
                                      insertbackground=entryFg, relief=entryRelief)
        self.entryUsuario.pack(pady=entryPadyTop, ipady=entryIpady, fill="x", padx=formPadx)
        self.entryUsuario.bind("<Return>", lambda e: self.entryContraseña.focus_set())

        # Campo de contraseña.
        tk.Label(self.formFrame, text="Contraseña", font=labelFont, fg=entryFg, bg="black").pack(fill="x",
                                                                                                 padx=formPadx,
                                                                                                 pady=labelPadyTop)
        self.entryContraseña = tk.Entry(self.formFrame, font=entryFont, show="*", width=entryWidth, bg=entryBg,
                                         fg=entryFg, insertbackground=entryFg, relief=entryRelief)
        self.entryContraseña.pack(pady=entryPadyTop, ipady=entryIpady, fill="x", padx=formPadx)
        self.entryContraseña.bind("<Return>",
                                   lambda e: self.entryConfirmarContraseña.focus_set())

        # Campo de confirmar contraseña.
        tk.Label(self.formFrame, text="Confirmar Contraseña", font=labelFont, fg=entryFg, bg="black").pack(fill="x",
                                                                                                             padx=formPadx,
                                                                                                             pady=labelPadyTop)
        self.entryConfirmarContraseña = tk.Entry(self.formFrame, font=entryFont, show="*", width=entryWidth,
                                                   bg=entryBg, fg=entryFg, insertbackground=entryFg,
                                                   relief=entryRelief)
        self.entryConfirmarContraseña.pack(pady=entryPadyTop, ipady=entryIpady, fill="x", padx=formPadx)
        # Intenta registrar al presionar Enter en el último campo.
        self.entryConfirmarContraseña.bind("<Return>",
                                             lambda e: self._onRegisterAttempt())

        # Botón de registrar.
        tk.Button(self.formFrame, text="Registrar", font=(entryFont[0], entryFont[1], "bold"), fg="white",
                  bg="#e50914",
                  command=self._onRegisterAttempt, relief="flat", bd=0, activebackground="#b0070f"
                  ).pack(pady=25, ipady=10, fill="x", padx=formPadx)

        # Frame para el enlace de inicio de sesión.
        enlacesFrame = tk.Frame(self.formFrame, bg="black")
        enlacesFrame.pack(pady=(10, 20), fill="x", padx=formPadx, side="bottom")
        # Enlace para ir a la vista de login.
        enlace = tk.Label(enlacesFrame, text="¿Ya tienes una cuenta? Inicia sesión", font=("Helvetica", 10),
                          fg="white", bg="black", cursor="hand2")
        enlace.pack(side="right")
        enlace.bind("<Button-1>", self._onGoToLogin) # Navega al hacer clic.

    def _onRegisterAttempt(self):
        # Se llama al intentar registrar un nuevo usuario.
        correo = self.entryCorreo.get()
        usuario = self.entryUsuario.get()
        contraseña = self.entryContraseña.get()
        confirmar = self.entryConfirmarContraseña.get()

        parentDialogForError = self.winfo_toplevel() # Para que los diálogos de error sean modales a esta vista.

        # Validaciones de los campos.
        if not all([correo, usuario, contraseña, confirmar]): # Todos los campos son obligatorios.
            self.appController.showStyledError("Error de Registro", "Todos los campos son obligatorios.",
                                                  parentForDialog=parentDialogForError)
            return
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', correo): # Validación de formato de email.
            self.appController.showStyledError("Error de Formato", "Correo no válido.",
                                                  parentForDialog=parentDialogForError)
            return
        if contraseña != confirmar: # Las contraseñas deben coincidir.
            self.appController.showStyledError("Error de Contraseña", "Las contraseñas no coinciden.",
                                                  parentForDialog=parentDialogForError)
            return
        # Validación de la fortaleza de la contraseña (ejemplo: mínimo 8 caracteres, letras y números).
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', contraseña):
            self.appController.showStyledError("Error de Contraseña",
                                                  "La contraseña debe tener al menos 8 caracteres,\nincluyendo letras y números.",
                                                  parentForDialog=parentDialogForError)
            return

        self.authController.handleRegistration(usuario, correo, contraseña) # Llama al controlador.

    def _onGoToLogin(self, event=None):
        # Navega a la vista de inicio de sesión.
        self.authController.requestLoginView()

    def showMessage(self, title, message, type="info"):
        # Muestra mensajes usando los diálogos estilizados del AppController.
        parentDialog = self.winfo_toplevel()

        if type == "error":
            self.appController.showStyledError(title, message, parentForDialog=parentDialog)
        elif type == "warning":
            self.appController.showStyledError(title, f"Advertencia: {message}", parentForDialog=parentDialog)
        else: # "info"
            self.appController.showStyledInfo(title, message, parentForDialog=parentDialog)

    def clearFields(self):
        # Limpia todos los campos de entrada.
        self.entryCorreo.delete(0, tk.END)
        self.entryUsuario.delete(0, tk.END)
        self.entryContraseña.delete(0, tk.END)
        self.entryConfirmarContraseña.delete(0, tk.END)
        self.entryCorreo.focus_set() # Pone el foco en el primer campo.

    def destroy(self):
        # Limpieza de recursos al destruir la vista.
        print(f"REGISTRO_VIEW: destroy llamado para {self} (ID: {id(self)})")
        self.fondoOriginal = None
        self.fondoTk = None
        self.logoPhoto = None
        if hasattr(self, 'fondoLabel') and self.fondoLabel.winfo_exists():
            self.fondoLabel.config(image='') # Limpia la imagen del label.
        super().destroy()