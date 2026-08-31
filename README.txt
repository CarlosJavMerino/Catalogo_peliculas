Aquí tienes el README.md completo, integrando tanto la descripción técnica y
funcional del proyecto como la guía de instalación y configuración:

🎬 Netflix Desktop Clone (Python & Tkinter)

Una aplicación de escritorio interactiva inspirada en la interfaz y experiencia
de usuario de Netflix, desarrollada en Python utilizando Tkinter para la
interfaz gráfica y MySQL para la persistencia de datos. El proyecto sigue una
arquitectura limpia basada en el patrón de diseño MVC
(Modelo-Vista-Controlador).

📌 ¿Qué hace la aplicación?

La aplicación permite a los usuarios registrarse, explorar un catálogo de
películas y series, interactuar con el contenido, gestionar listas de
reproducción personalizadas y proteger contenido para adultos mediante un
sistema de control parental.

🚀 Funcionalidades Principales

1. 🔐 Autenticación y Gestión de Usuarios

  - Registro seguro: Creación de nuevas cuentas con validación de formato de
    correo, contraseñas seguras y encriptación mediante bcrypt.
  - Inicio de sesión: Validación contra base de datos con manejo de sesiones
    activas.
  - Diseño temático: Pantallas de bienvenida y autenticación con fondo dinámico
    e identidad visual oficial.

2. 🏠 Pantalla de Inicio y Motor de Recomendaciones

  - Filas de contenido dinámico: Carruseles horizontales desplazables que
    clasifican Películas Populares y Series Populares por valoración.
  - Sistema de recomendaciones personalizadas: Algoritmo que analiza los géneros
    de los títulos marcados con "Me gusta" por el usuario y le sugiere contenido
    afín que aún no ha visto.
  - Carga asíncrona de imágenes: Descarga y renderizado de pósters mediante
    hilos (multi-threading) y colas (Queue), asegurando una navegación fluida
    sin congelamientos de pantalla (UI freezing).

3. 🔍 Búsqueda Avanzada y Filtros

  - Búsqueda en tiempo real por texto/nombre del título.
  - Filtros combinados por Género, Tipo de contenido (Película o Serie) y Año de
    estreno.

4. 📄 Ficha Detallada de Títulos y Gestión de Capítulos

  - Visualización completa de sinopsis, año, duración, calificación por edades y
    reparto de actores.
  - Interacciones del usuario:
      - Dar / quitar "Me gusta" ❤️.
      - Marcar películas o títulos completos como "Visto" ✔️.
      - Añadir el título a cualquiera de sus listas personalizadas.
  - Gestor de Series: Selector dinámico de temporadas y desglose de capítulos
    con seguimiento individual del estado de visualización (visto/no visto) con
    almacenamiento en caché local.

5. 📑 Listas de Reproducción Personalizadas ("Mis Listas")

  - Crear nuevas listas con nombres personalizados.
  - Añadir o eliminar títulos de las listas.
  - Visualizar el catálogo específico dentro de cada lista o borrar listas
    completas.

6. 🛡️ Control Parental

  - Configuración, modificación y eliminación de un código PIN numérico de 4
    dígitos.
  - Bloqueo automático de contenido: Los títulos con clasificaciones para
    adultos (R, TV-MA) solicitan obligatoriamente el PIN antes de permitir el
    acceso a su ficha de detalles.

7. 🎨 Experiencia Visual y Componentes Personalizados

  - Tema oscuro (Dark Mode) con la paleta de colores característica de Netflix
    (#E50914).
  - Diálogos modales personalizados (errores, confirmaciones, advertencias e
    ingreso de PIN) que reemplazan las ventanas estándar del sistema operativo
    para mantener una estética homogénea.

🛠️ Tecnologías y Arquitectura Utilizadas

  - Lenguaje: Python 3.x
  - GUI: tkinter & ttk (estilizado con temas y componentes personalizados).
  - Base de Datos: MySQL (conector oficial mysql-connector-python).
  - Seguridad: bcrypt (hashing seguro de contraseñas con salt).
  - Manejo de Imágenes & Red: Pillow (PIL), requests, threading, queue.
  - Patrón de Diseño: MVC (Model-View-Controller) para desacoplar la lógica de
    negocio, el acceso a datos y las interfaces gráficas.

📦 Instalación y Puesta en Marcha

Sigue estos pasos detallados para configurar la base de datos y ejecutar la
aplicación en tu entorno local.

📋 Prerrequisitos

Antes de comenzar, asegúrate de contar con el siguiente software:

  - MySQL Server (versión 8.0 o superior recomendada).
    Si no lo tienes instalado, puedes descargarlo desde el sitio oficial de
    MySQL Community Server.

⚙️ Pasos de Instalación

1. 📥 Descarga de Archivos

Asegúrate de tener en la misma carpeta o directorio de trabajo los siguientes
archivos del proyecto:

  - NetflixAppDemo.exe (Ejecutable principal de la aplicación).
  - netflix - Base de datos.sql (Script con el esquema y los datos iniciales).

2. 🗄️ Configuración de la Base de Datos

Abre tu terminal o consola de comandos y sigue estas instrucciones para crear la
base de datos e importar la estructura:

1.  Accede a MySQL con privilegios de administrador:

    mysql -u root -p

    (Introduce tu contraseña de root cuando el sistema la solicite).

2.  Crea la base de datos del proyecto:

    CREATE DATABASE Netflix;

3.  Crea el usuario y asigna permisos (opcional si usas las credenciales por
    defecto):

    CREATE USER 'tu_usuario'@'localhost' IDENTIFIED BY 'tu_contraseña';
    GRANT ALL PRIVILEGES ON Netflix.* TO 'tu_usuario'@'localhost';
    FLUSH PRIVILEGES;

4.  Sal de la consola de MySQL:

    EXIT;

5.  Importa el esquema y los datos iniciales ejecutando el siguiente comando en
    tu terminal:

    mysql -u tu_usuario -p Netflix < "netflix - Base de datos.sql"

    💡 Nota: Si utilizas el usuario root, ejecuta:

    mysql -u root -p Netflix < "netflix - Base de datos.sql"

3. ▶️ Ejecución de la Aplicación

Una vez configurada la base de datos:

1.  Haz doble clic sobre el archivo NetflixAppDemo.exe (o ejecútalo desde tu
    terminal).
2.  ¡Listo! Ya puedes registrar una nueva cuenta o iniciar sesión para comenzar
    a explorar el catálogo.
