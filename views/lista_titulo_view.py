import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk  # Para manejo de imágenes.
import requests
from io import BytesIO
from .base_view import BaseView  # Herencia para UI base.

class TitulosListaView(BaseView):
    # Vista para mostrar los títulos contenidos en una lista de reproducción específica del usuario.
    # Permite ver los títulos y quitarlos de la lista.
    def __init__(self, parent, controller, id_lista, nombre_lista):
        appController = controller.appController
        super().__init__(parent, appController)
        self.controller = controller
        self.idLista = id_lista
        self.nombreLista = nombre_lista
        self.imageReferences = []
        self._crearAreaTitulosEnContenido()

    def _crearAreaTitulosEnContenido(self):
        # Construye la interfaz principal para mostrar los títulos de la lista.
        # Título de la vista, muestra el nombre de la lista actual.
        tk.Label(self.contenidoPrincipalFrame, text=f"Títulos en: {self.nombreLista}", fg="#E50914", bg="black",
                 font=("Segoe UI", 26, "bold")).pack(pady=(20, 15))

        # Botón para volver a la vista de "Mis Listas".
        tk.Button(self.contenidoPrincipalFrame, text="← Volver a Mis Listas", font=("Helvetica", 12),
                  fg="white", bg="gray30", relief="flat", cursor="hand2",
                  command=lambda: self.appController.navigateToMyLists()  # Navega a la vista de listas.
                  ).pack(pady=(0, 15), anchor="w", padx=25)

        # Frame exterior para el canvas scrollable de resultados.
        resultadosOuterFrame = tk.Frame(self.contenidoPrincipalFrame, bg="black")
        resultadosOuterFrame.pack(fill="both", expand=True, padx=20, pady=10)

        # Canvas para permitir el scroll de los títulos si exceden el espacio visible.
        self.canvasTitulos = tk.Canvas(resultadosOuterFrame, bg="black", highlightthickness=0)
        scrollbar = ttk.Scrollbar(resultadosOuterFrame, orient="vertical", command=self.canvasTitulos.yview,
                                  style="TScrollbar")
        self.canvasTitulos.configure(yscrollcommand=scrollbar.set)

        # Frame interno dentro del canvas que contendrá los elementos de los títulos.
        self.titulosContainerFrame = tk.Frame(self.canvasTitulos, bg="black")
        self.canvasWindowId = self.canvasTitulos.create_window((0, 0), window=self.titulosContainerFrame,
                                                               anchor="nw")

        # Vinculación de eventos para el scroll y redimensionamiento.
        self.titulosContainerFrame.bind("<Configure>", lambda e: self.canvasTitulos.configure(
            scrollregion=self.canvasTitulos.bbox("all")) if self.canvasTitulos.winfo_exists() else None)
        self.canvasTitulos.bind("<Configure>",
                                lambda e: self.canvasTitulos.itemconfig(self.canvasWindowId,
                                                                        width=e.width) if self.canvasTitulos.winfo_exists() else None)
        self.canvasTitulos.bind("<MouseWheel>",
                                lambda event: self.canvasTitulos.yview_scroll(int(-1 * (event.delta / 120)),
                                                                              "units") if self.canvasTitulos.winfo_exists() else None)

        self.canvasTitulos.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def displayTitlesInList(self, titlesData):
        # Muestra los títulos de la lista.
        # Limpia los resultados anteriores y las referencias a imágenes.
        for widget in self.titulosContainerFrame.winfo_children():
            widget.destroy()
        self.imageReferences.clear()

        if not titlesData:
            tk.Label(self.titulosContainerFrame, text="Esta lista está vacía.",
                     fg="gray", bg="black", font=("Segoe UI", 14)).pack(pady=30)
            return

        # Itera sobre los datos de los títulos y crea un widget para cada uno.
        for idx, tituloData in enumerate(titlesData):  # idx añadido por si se usa para claves únicas
            itemFrame = tk.Frame(self.titulosContainerFrame, bg="#1c1c1c", padx=10, pady=10)
            itemFrame.pack(fill="x", pady=5, padx=5)  # Frame para cada título.

            imgUrl = tituloData.get("imagen_url")

            imgLabel = tk.Label(itemFrame, bg='grey10', width=100, height=150,
                                text="...", fg="grey50", font=("Arial", 12))
            uniqueKey = (id(imgLabel), imgUrl if imgUrl else f"no_url_listatitulo_{idx}_{self.idLista}")
            self._requestImageLoadAsync(imgUrl, 100, 150, imgLabel, uniqueKey)

            imgLabel.pack(side="left", padx=(0, 10))
            # Clic en la imagen navega a los detalles del título.
            imgLabel.bind("<Button-1>",
                          lambda e, idT=tituloData["id_titulo"]: self.appController.navigateToDetails(idT))

            # Frame para la información textual (nombre, sinopsis) y botón de quitar.
            infoFrame = tk.Frame(itemFrame, bg="#1c1c1c")
            infoFrame.pack(side="left", fill="both", expand=True)

            tituloLabelTextWidget = tk.Label(infoFrame, text=tituloData["nombre"], fg="white", bg="#1c1c1c",
                                             font=("Segoe UI", 16, "bold"), cursor="hand2", anchor="w")
            tituloLabelTextWidget.pack(fill="x")
            tituloLabelTextWidget.bind("<Button-1>",  # Clic en el nombre también navega a detalles.
                                       lambda e, idT=tituloData["id_titulo"]: self.appController.navigateToDetails(idT))

            sinopsis = tituloData.get("sinopsis", "Sinopsis no disponible.")
            try:  # Ajusta el wraplength de la sinopsis.
                wraplen = self.winfo_width() * 0.7 if self.winfo_width() > 1 else 700
            except tk.TclError:
                wraplen = 700  # Fallback.
            tk.Label(infoFrame, text=sinopsis, fg="#cccccc", bg="#1c1c1c", wraplength=wraplen, justify="left",
                     font=("Segoe UI", 11), anchor="w").pack(fill="x", pady=(5, 0))

            # Botón para quitar el título de esta lista.
            btnEliminar = tk.Button(itemFrame, text="❌ Quitar", font=("Helvetica", 10), fg="white", bg="#50070a",
                                    borderwidth=0, relief="flat", cursor="hand2", padx=8, pady=4,
                                    command=lambda idT=tituloData["id_titulo"],
                                                   nomT=tituloData["nombre"]: self._confirmRemoveTitle(idT, nomT))
            btnEliminar.pack(side="right", padx=5, pady=5, anchor="center")  # Se alinea a la derecha del itemFrame.

        self.titulosContainerFrame.update_idletasks()  # Actualiza layout.
        if self.canvasTitulos.winfo_exists():
            self.canvasTitulos.config(scrollregion=self.canvasTitulos.bbox("all"))  # Actualiza scroll.
            self.canvasTitulos.yview_moveto(0)

    def _confirmRemoveTitle(self, titleId, titleName):
        # Muestra un diálogo de confirmación estilizado antes de quitar un título de la lista.
        def _doRemove():
            # Esta función se llamará si el usuario confirma la acción.
            self.controller.handleRemoveTitleFromCurrentList(self.idLista, titleId)

        self.appController.showStyledConfirm(
            title="Confirmar Quitar",
            message=f"¿Quitar '{titleName}' de esta lista?",
            yesCallback=_doRemove,
            noCallback=None,  # No se necesita acción especial si eligen "No"
            parentForDialog=self.winfo_toplevel(),  # Modal a la ventana actual
            yesText="Quitar",
            noText="Cancelar"
        )

    def _loadImageFromUrl(self, url, width, height):
        if not url: return None
        try:
            response = requests.get(url, timeout=5)  # Timeout corto.
            response.raise_for_status()
            imgData = response.content
            pilImage = Image.open(BytesIO(imgData)).resize((width, height), Image.LANCZOS)
            imgTk = ImageTk.PhotoImage(pilImage)
            self.imageReferences.append(imgTk)  # Guarda referencia para evitar GC.
            return imgTk
        except Exception as e:
            print(f"Error cargando imagen en TitulosListaView ({url}): {e}")
            # Crea un placeholder si la carga falla.
            placeholder = Image.new("RGB", (width, height), (30, 30, 30))  # Gris oscuro
            imgTk = ImageTk.PhotoImage(placeholder)
            self.imageReferences.append(imgTk)
            return imgTk

    def showMessage(self, title, message, type="info", parent=None):
        _parentDialog = parent if parent and parent.winfo_exists() else self.winfo_toplevel()

        if type == "error":
            self.appController.showStyledError(title, message, parentForDialog=_parentDialog)
        elif type == "warning":
            self.appController.showStyledError(title, f"Advertencia: {message}", parentForDialog=_parentDialog)
        else:  # "info"
            self.appController.showStyledInfo(title, message, parentForDialog=_parentDialog)

    def destroy(self):
        # Limpia referencias a imágenes antes de destruir la vista.
        self.imageReferences.clear()
        super().destroy()