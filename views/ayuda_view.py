import tkinter as tk
from .base_view import BaseView # Importa la clase base para heredar la barra de navegación y funcionalidades comunes.

class AyudaView(BaseView):
    # Vista que muestra información de ayuda y solución de problemas comunes.
    # Hereda de BaseView para incluir la barra de navegación estándar.
    def __init__(self, parent, controllerApp):
        # El 'controllerApp' aquí es una instancia de la clase App principal,
        # ya que esta vista no tiene un controlador dedicado y usa métodos de App para la navegación.
        super().__init__(parent, controllerApp)

        self.contenidoPrincipalFrame.config(bg='black') # Asegura fondo negro para el contenido.

        self._mostrarPantallaAyuda()

    def _mostrarPantallaAyuda(self):
        # Construye y muestra los elementos de la interfaz de la pantalla de ayuda.

        # Título principal de la sección de ayuda.
        titulo = tk.Label(
            self.contenidoPrincipalFrame,
            text="AYUDA",
            font=("Helvetica", 32, "bold"),
            fg="#E50914", # Color rojo característico.
            bg='black'
        )
        titulo.pack(pady=(20, 30)) # Espaciado vertical.

        # Texto con la información de ayuda.
        textoAyuda = (
            "Solución de Problemas Comunes / Consejos:\n\n"
            "¿Problemas para iniciar sesión?\nVerifica que tu usuario y contraseña sean correctos.\n\n"
            "Conexión a Internet:\nAsegúrate de tener una conexión a internet estable para cargar el contenido y las imágenes.\n\n"
            "Aplicación no responde:\nSi la aplicación no responde, intenta cerrarla y volverla a abrir.\n\n"
            "Contacto:\nSi necesitas más ayuda o quieres reportar un problema, "
            "puedes contactarnos en NetflixAppSupport@ejemplo.com"
        )

        # Calcula el ancho del texto para que se ajuste al frame.
        # Se usa un try-except por si el frame aún no tiene dimensiones al crearse.
        try:
            # Ajusta el wraplength al 80% del ancho del frame de contenido si ya está disponible.
            wraplen = self.contenidoPrincipalFrame.winfo_width() * 0.8 if self.contenidoPrincipalFrame.winfo_width() > 1 else 750
        except tk.TclError:
            wraplen = 750 # Fallback a un valor fijo si winfo_width() falla (ej. ventana no visible aún).

        # Etiqueta para mostrar el texto de ayuda.
        descripcion = tk.Label(
            self.contenidoPrincipalFrame,
            text=textoAyuda,
            font=("Helvetica", 14),
            wraplength=wraplen, # Permite que el texto se ajuste automáticamente.
            justify="center", # Justificación del texto.
            fg="white",
            bg='black'
        )
        descripcion.pack(padx=20, pady=10) # Espaciado horizontal y vertical.