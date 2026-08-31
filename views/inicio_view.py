import tkinter as tk
from tkinter import ttk
from .base_view import BaseView  # Para la barra de navegación y carga de imágenes.

class InicioView(BaseView):
    # Vista principal de la aplicación después del login.
    # Muestra categorías de títulos (ej. Populares, Recomendados) en filas horizontales con scroll.
    def __init__(self, parent, controller):
        # 'controller' es TitleController.
        appController = controller.appController
        super().__init__(parent, appController)
        self.controller = controller  # Instancia de TitleController.

        self.screenWidth = self.winfo_screenwidth()  # Ancho de la pantalla para calcular tamaños relativos.

        # Canvas principal para permitir el scroll vertical de todo el contenido de la página de inicio.
        self.mainCanvasInicio = tk.Canvas(self.contenidoPrincipalFrame, bg='black', highlightthickness=0)

        # scrollbar_y = tk.Scrollbar(self.contenidoPrincipalFrame, orient="vertical",
        #                            command=self.mainCanvasInicio.yview)
        scrollbar_y = ttk.Scrollbar(self.contenidoPrincipalFrame, orient="vertical",
                                    command=self.mainCanvasInicio.yview, style="TScrollbar")

        self.mainCanvasInicio.configure(yscrollcommand=scrollbar_y.set)

        # Frame interno dentro del canvas que contendrá todas las filas de categorías.
        self.scrollableContentFrameInicio = tk.Frame(self.mainCanvasInicio, bg='black')
        # Añade el frame scrollable al canvas.
        self.mainCanvasInicio.create_window((0, 0), window=self.scrollableContentFrameInicio, anchor="nw",
                                            tags="sw_frame_inicio")  # Tag para referenciarlo.

        # Vincula eventos para gestionar el scroll y el redimensionamiento.
        self.scrollableContentFrameInicio.bind("<Configure>", self._onScrollableFrameConfigureInicio)
        self.mainCanvasInicio.bind("<Configure>", self._onMainCanvasConfigureInicio)
        self.mainCanvasInicio.bind("<MouseWheel>", self._onMousewheelMainCanvasInicio)  # Scroll con rueda del mouse.

        self.mainCanvasInicio.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")

    def _onScrollableFrameConfigureInicio(self, event):
        # Actualiza la región de scroll del canvas principal cuando cambia el tamaño del frame interno.
        if self.mainCanvasInicio.winfo_exists():
            self.mainCanvasInicio.configure(scrollregion=self.mainCanvasInicio.bbox("all"))

    def _onMainCanvasConfigureInicio(self, event):
        # Ajusta el ancho del frame interno al ancho del canvas principal cuando este se redimensiona.
        if self.mainCanvasInicio.winfo_exists():
            self.mainCanvasInicio.itemconfig("sw_frame_inicio", width=event.width)

    def _onMousewheelMainCanvasInicio(self, event):
        # Maneja el evento de la rueda del mouse para el scroll vertical del canvas principal.
        if self.mainCanvasInicio.winfo_exists():
            self.mainCanvasInicio.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def displayCategories(self, categoriesData):
        # Muestra las categorías y sus títulos en la vista.
        # Limpia el contenido anterior.
        for widget in self.scrollableContentFrameInicio.winfo_children():
            widget.destroy()

        if not categoriesData:
            tk.Label(self.scrollableContentFrameInicio, text="No hay contenido para mostrar.",
                     fg="gray", bg="black", font=("Helvetica", 16)).pack(pady=50)
            return

        # Itera sobre los datos de categorías y renderiza una fila para cada una.
        for category in categoriesData:
            self._renderCategoryRow(self.scrollableContentFrameInicio, category['title'], category['items'])

        # Actualiza para asegurar que las dimensiones son correctas antes de configurar el scroll.
        self.scrollableContentFrameInicio.update_idletasks()
        if self.mainCanvasInicio.winfo_exists():
            self.mainCanvasInicio.config(scrollregion=self.mainCanvasInicio.bbox("all"))
            self.mainCanvasInicio.yview_moveto(0)  # Vuelve al inicio del scroll.

    def _renderCategoryRow(self, parentFrameForRow, categoryTitleText, itemsData):
        # Renderiza una fila de categoría, que incluye un título y un canvas horizontal para los ítems.
        frameCategoriaOuter = tk.Frame(parentFrameForRow, bg='black')
        frameCategoriaOuter.pack(fill='x', pady=(20, 15))  # Espaciado entre filas de categorías.

        # Título de la categoría (ej. "Películas Populares").
        tk.Label(frameCategoriaOuter, text=categoryTitleText, font=("Helvetica", 18, "bold"), fg="white",
                 bg="black").pack(anchor="w", padx=25, pady=(0, 10))  # Alineado a la izquierda.

        # Frame para el canvas de scroll horizontal y los botones de scroll (izquierda/derecha).
        frameScrollHorizontal = tk.Frame(frameCategoriaOuter, bg='black')
        frameScrollHorizontal.pack(fill='x')

        # Calcula dimensiones para las miniaturas basadas en el ancho de la pantalla.
        miniaturaWidth = int(self.screenWidth * 0.12)  # 12% del ancho de pantalla.
        miniaturaHeight = int(miniaturaWidth * 1.5)  # Proporción 2:3 típica de pósters.
        canvasHeight = miniaturaHeight + 45  # Altura del canvas, incluye espacio para el nombre del título debajo.

        # Canvas para el scroll horizontal de las miniaturas.
        canvasCategoria = tk.Canvas(frameScrollHorizontal, bg='black', height=canvasHeight,
                                    highlightthickness=0)

        # Frame interno dentro del canvas horizontal que contendrá las miniaturas.
        frameMiniaturasInterno = tk.Frame(canvasCategoria, bg='black')
        canvasCategoria.create_window((0, 0), window=frameMiniaturasInterno, anchor="nw")

        # Función para el scroll horizontal del canvas de categoría.
        def _scrollCategoriaHorizontal(canvas, direction):
            if canvas.winfo_exists():
                scroll_amount = 2
                canvas.xview_scroll(direction * scroll_amount, "units")

        btnIzq = tk.Button(frameScrollHorizontal, text="◀", font=("Helvetica", 20), fg="white", bg="black",
                           relief="flat", bd=0, command=lambda c=canvasCategoria: _scrollCategoriaHorizontal(c, -1))
        btnIzq.pack(side="left", padx=(10, 0), fill="y")

        canvasCategoria.pack(side="left", fill="x", expand=True)  # El canvas se expande para llenar el espacio.

        btnDer = tk.Button(frameScrollHorizontal, text="▶", font=("Helvetica", 20), fg="white", bg="black",
                           relief="flat", bd=0, command=lambda c=canvasCategoria: _scrollCategoriaHorizontal(c, 1))
        btnDer.pack(side="right", padx=(0, 10), fill="y")

        # Permite scroll horizontal con la rueda del mouse sobre el canvas de categoría.
        canvasCategoria.bind("<MouseWheel>", lambda event, c=canvasCategoria: _scrollCategoriaHorizontal(c, int(-1 * (
                    event.delta / 60))))

        if not itemsData:  # Si no hay ítems en la categoría.
            tk.Label(frameMiniaturasInterno, text="No hay títulos.", fg="gray70", bg="black",
                     font=("Helvetica", 11)).pack(padx=20, pady=canvasHeight // 3)
        else:
            # Itera sobre los ítems y crea una miniatura para cada uno.
            for itemIdx, item in enumerate(itemsData):
                contenedorItem = tk.Frame(frameMiniaturasInterno, bg='black')  # Contenedor para imagen y título.
                contenedorItem.pack(side='left', padx=8, pady=(5, 0))  # Se empaquetan a la izquierda.

                # Label para la imagen (miniatura).
                labelImagen = tk.Label(contenedorItem, bg='grey10',
                                       width=miniaturaWidth, height=miniaturaHeight,  # Dimensiones calculadas.
                                       text="...", fg="grey50", font=("Arial", 12))
                labelImagen.pack()

                imageUrl = item.get("imagen_url")
                uniqueImageKey = (id(labelImagen),
                                  imageUrl if imageUrl else f"no_url_inicio_{itemIdx}_{categoryTitleText}")  # Clave única.
                self._requestImageLoadAsync(imageUrl, miniaturaWidth, miniaturaHeight, labelImagen, uniqueImageKey)

                # Clic en la imagen navega a los detalles del título.
                labelImagen.bind("<Button-1>",
                                 lambda e, itemId=item["id_titulo"]: self.appController.navigateToDetails(itemId))

                # Nombre del título debajo de la miniatura.
                tituloItemText = item.get("nombre", "Sin título")
                tk.Label(contenedorItem, text=tituloItemText, font=("Helvetica", 10), fg="white",
                         bg="black", wraplength=miniaturaWidth - 5, justify="center").pack(pady=(3, 0), fill='x')

        # Actualiza el frame de miniaturas para que el canvas de categoría calcule su scrollregion.
        frameMiniaturasInterno.update_idletasks()
        if canvasCategoria.winfo_exists():
            canvasCategoria.config(scrollregion=canvasCategoria.bbox("all"))

    def destroy(self):
        # Limpieza específica de InicioView si fuera necesaria.
        super().destroy()