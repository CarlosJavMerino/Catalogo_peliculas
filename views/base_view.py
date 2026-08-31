import tkinter as tk
from PIL import Image, ImageTk # Para manejar imágenes.
import requests # Para descargar imágenes de URLs.
from io import BytesIO # Para manejar datos binarios de imágenes.
import threading # Para cargar imágenes de forma asíncrona.
from queue import Queue, Empty # Cola para gestionar la actualización de imágenes en el hilo principal.
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


class BaseView(tk.Frame):
    # Clase base para todas las vistas de la aplicación.
    # Proporciona una barra de navegación común y funcionalidades compartidas como la carga asíncrona de imágenes.
    def __init__(self, parent, appControllerInstance):
        super().__init__(parent, bg='black')
        self.appController = appControllerInstance # Referencia al controlador principal de la aplicación.

        # Referencias a imágenes para evitar que el recolector de basura las elimine.
        self.logoImagenTkRefBase = None
        self.variableUsuarioMenuBase = None # Tkinter StringVar para el menú de usuario.

        # Diccionario para mantener referencias a las imágenes cargadas dinámicamente.
        # La clave puede ser una tupla (id_widget, url) para unicidad.
        self.imageReferencesDict = {}
        # Cola para pasar imágenes cargadas en hilos secundarios al hilo principal para su actualización en UI.
        self.imageLoadQueue = Queue()
        self._afterIdQueueCheck = None # ID para el método `after` que verifica la cola.

        self._crearBarraNavegacionBase()

        # Frame principal donde cada vista hija colocará su contenido específico.
        self.contenidoPrincipalFrame = tk.Frame(self, bg='black')
        self.contenidoPrincipalFrame.pack(fill="both", expand=True)

        self.checkImageQueue() # Inicia el proceso de verificación de la cola de imágenes.

    def _crearBarraNavegacionBase(self):
        # Crea la barra de navegación superior común a todas las vistas.
        barraNavegacion = tk.Frame(self, bg='black', height=60)
        barraNavegacion.pack(fill='x', side='top') # Se expande horizontalmente en la parte superior.

        # Intenta cargar el logo de Netflix.
        try:
            logo_path = resource_path("assets/Netflix-logo.png") # <--- MODIFICADO
            logoImagenPil = Image.open(logo_path).resize((180, 70))
            self.logoImagenTkRefBase = ImageTk.PhotoImage(logoImagenPil)
            logoLabel = tk.Label(barraNavegacion, image=self.logoImagenTkRefBase, bg="black", cursor="hand2")
            logoLabel.pack(side='left', padx=20, pady=5)
            logoLabel.bind("<Button-1>", lambda e: self.appController.navigateToHome()) # Clic en logo lleva a Inicio.
        except FileNotFoundError:
            resolved_logo_path = resource_path("assets/Netflix-logo.png")
            print(f"Error BaseView: No se encontró '{resolved_logo_path}'")
            logoLabelFallback = tk.Label(barraNavegacion, text="Netflix", fg="red", bg="black",
                                         font=("Arial", 20, "bold"), cursor="hand2")
            logoLabelFallback.pack(side='left', padx=20, pady=5)
            logoLabelFallback.bind("<Button-1>", lambda e: self.appController.navigateToHome())
        except Exception as e:
            # Fallback genérico por otros errores al cargar el logo.
            print(f"Error BaseView cargando logo: {e}")
            logoLabelFallback = tk.Label(barraNavegacion, text="Netflix App", fg="red", bg="black",
                                         font=("Arial", 20, "bold"), cursor="hand2")
            logoLabelFallback.pack(side='left', padx=20, pady=5)
            logoLabelFallback.bind("<Button-1>", lambda e: self.appController.navigateToHome())


        # Menú desplegable para opciones de usuario (Cerrar sesión, Control parental, Listas).
        opcionesUsuario = ["Listas", "Control parental", "Cerrar sesión"] # Ordenado para mejor UX.
        self.variableUsuarioMenuBase = tk.StringVar(value="👤") # Icono de usuario como texto inicial.
        menuUsuario = tk.OptionMenu(barraNavegacion, self.variableUsuarioMenuBase, *opcionesUsuario,
                                    command=self._accionUsuarioMenuBase)
        menuUsuario.config(bg="black", fg="white", font=("Helvetica", 12), indicatoron=False, relief="flat",
                           highlightthickness=0, activebackground="black", activeforeground="white")
        if menuUsuario["menu"]: # Configura el menú desplegable en sí.
            menuUsuario["menu"].config(bg="black", fg="white", relief="flat", font=("Helvetica", 11))
        menuUsuario.pack(side='right', padx=(10, 20)) # Alineado a la derecha.

        # Botón de Ayuda.
        tk.Button(barraNavegacion, text="❓", font=("Helvetica", 16), fg="white", bg="black",
                  borderwidth=0, relief="flat", cursor="hand2",
                  command=lambda: self.appController.navigateToHelp() # Navega a la vista de Ayuda.
                  ).pack(side='right', padx=5)

        # Botón de Búsqueda.
        tk.Button(barraNavegacion, text="🔍", font=("Helvetica", 16), fg="white", bg="black",
                  borderwidth=0, relief="flat", cursor="hand2",
                  command=lambda: self.appController.navigateToSearch() # Navega a la vista de Búsqueda.
                  ).pack(side='right', padx=5)

    def _accionUsuarioMenuBase(self, opcion):
        # Maneja la selección de una opción del menú de usuario.
        if self.variableUsuarioMenuBase:
            self.variableUsuarioMenuBase.set("👤") # Restablece el texto del OptionMenu al icono.

        if opcion == "Cerrar sesión":
            self.appController.logout()
        elif opcion == "Control parental":
            # Determina la vista actual para poder regresar a ella después de configurar el control parental.
            origen = self.__class__.__name__ if self else "InicioView" # Nombre de la clase de la vista actual.
            self.appController.navigateToParentalControl(originFrameName=origen)
        elif opcion == "Listas":
            self.appController.navigateToMyLists()

    def _requestImageLoadAsync(self, url, width, height, imageLabelWidget, imageKeyForDict):
        # Solicita la carga de una imagen desde una URL de forma asíncrona.
        # Muestra un placeholder mientras la imagen se descarga.
        if not url: # Si no hay URL, muestra "N/A" o limpia la imagen.
            if imageLabelWidget.winfo_exists():
                imageLabelWidget.config(text="N/A", image='', font=("Arial", 10), fg="white", bg='grey10')
            self.imageReferencesDict[imageKeyForDict] = None # Guarda None para esta clave.
            return
        try:
            # Crea y muestra una imagen placeholder.
            placeholderColorRgb = (26, 26, 26) # Gris oscuro.
            placeholderPil = Image.new("RGB", (width, height), placeholderColorRgb)
            placeholderTk = ImageTk.PhotoImage(placeholderPil)
            if imageLabelWidget.winfo_exists():
                imageLabelWidget.config(image=placeholderTk, bg='grey10', text="")
            self.imageReferencesDict[imageKeyForDict] = placeholderTk # Guarda referencia al placeholder.
        except Exception as e:
            # Error al crear el placeholder, muestra texto "Cargando...".
            print(f"Error creando placeholder para {url}: {e}")
            if imageLabelWidget.winfo_exists():
                imageLabelWidget.config(text="Cargando...", image='', font=("Arial", 10), fg="white", bg='grey10')
            if imageKeyForDict in self.imageReferencesDict: # Limpia si ya existía una referencia.
                del self.imageReferencesDict[imageKeyForDict]

        # Función que se ejecutará en un hilo separado para descargar y procesar la imagen.
        def _downloadAndProcessTask():
            try:
                response = requests.get(url, timeout=10) # Timeout de 10 segundos.
                response.raise_for_status() # Lanza excepción para errores HTTP.
                imgData = response.content
                # Redimensiona la imagen usando LANCZOS para mejor calidad.
                pilImage = Image.open(BytesIO(imgData)).resize((width, height), Image.LANCZOS)
                finalImgTk = ImageTk.PhotoImage(pilImage)
                # Si la vista principal todavía existe, añade la imagen cargada a la cola.
                if self.winfo_exists():
                    self.imageLoadQueue.put((imageLabelWidget, finalImgTk, imageKeyForDict, url))
            except requests.exceptions.Timeout:
                print(f"Timeout descargando imagen: {url}")
            except requests.exceptions.RequestException as e: # Errores de red, HTTP.
                print(f"Error de red descargando imagen ({url}): {e}")
            except Exception as e: # Otros errores durante el procesamiento.
                print(f"Error general procesando imagen en hilo ({url}): {e}")

        # Inicia el hilo de descarga. daemon=True permite que el programa termine aunque los hilos sigan activos.
        threading.Thread(target=_downloadAndProcessTask, daemon=True).start()

    def checkImageQueue(self):
        # Verifica periódicamente la cola de imágenes y actualiza los widgets Label en el hilo principal.
        try:
            if not self.imageLoadQueue.empty(): # Procesa solo si hay ítems y la vista existe.
                # Obtiene la imagen y el widget de la cola sin bloquear.
                imageLabelWidget, imageTkObject, imageKey, url = self.imageLoadQueue.get_nowait()
                # Verifica si el widget Label todavía existe antes de configurarlo.
                if imageLabelWidget.winfo_exists():
                    imageLabelWidget.config(image=imageTkObject, text="") # Actualiza la imagen.
                    self.imageReferencesDict[imageKey] = imageTkObject # Guarda la referencia final.
                else:
                    # Si el widget ya no existe, elimina la referencia para liberar memoria.
                    if imageKey in self.imageReferencesDict:
                        del self.imageReferencesDict[imageKey]
        except Empty:
            pass # Es normal que la cola esté vacía la mayoría del tiempo.
        except Exception as e:
            print(f"Error procesando cola de imágenes en BaseView: {e}")
        finally:
            # Programa la próxima verificación de la cola si la vista base aún existe.
            if self.winfo_exists():
                self._afterIdQueueCheck = self.after(100, self.checkImageQueue) # Verifica cada 100ms.

    def destroy(self):
        # Método de limpieza al destruir la vista.
        # Cancela la verificación periódica de la cola de imágenes.
        if self._afterIdQueueCheck:
            self.after_cancel(self._afterIdQueueCheck)
            self._afterIdQueueCheck = None

        # Vacía la cola de imágenes para evitar procesamientos pendientes.
        while not self.imageLoadQueue.empty():
            try:
                self.imageLoadQueue.get_nowait()
            except Empty:
                break

        # Limpia el diccionario de referencias a imágenes.
        self.imageReferencesDict.clear()

        # Limpia otras referencias para ayudar al recolector de basura.
        self.logoImagenTkRefBase = None
        self.variableUsuarioMenuBase = None
        super().destroy() # Llama al método destroy de la clase padre (tk.Frame).