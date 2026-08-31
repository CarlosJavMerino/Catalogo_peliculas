# Instalación de la Aplicación "Netflix"

Sigue estos pasos para instalar y ejecutar la aplicación "Netflix" en tu sistema.

## Prerrequisitos

1.  **Instala MySQL Server:**
    *   Si no tienes MySQL Server instalado, descárgalo e instálalo desde [https://dev.mysql.com/downloads/mysql/](https://dev.mysql.com/downloads/mysql/).

## Pasos de Instalación

1.  **Descarga el ejecutable:**
    *   Descarga el archivo `NetflixAppDemo.exe`.

2.  **Descarga la base de datos:**
    *   Descarga el archivo `netflix - Base de datos.sql`.

3.  **Crea la base de datos e importa los datos:**
    *   Inicia sesión en MySQL como usuario `root`:
        ```bash
        mysql -u root -p
        ```
    *   Ingresa la contraseña del usuario `root`.
    *   Crea la base de datos:
        ```sql
        CREATE DATABASE Netflix;
        ```
    *   Crea un usuario con los permisos necesarios (reemplaza `tu_usuario` y `tu_contraseña`):
        ```sql
        CREATE USER 'tu_usuario'@'localhost' IDENTIFIED BY 'tu_contraseña';
        GRANT ALL PRIVILEGES ON Netflix.* TO 'tu_usuario'@'localhost';
        FLUSH PRIVILEGES;
        ```
    *   Sal de la consola de MySQL:
        ```sql
        exit
        ```
    *   Importa el archivo `netflix - Base de datos.sql` a la base de datos que creaste (reemplaza `tu_usuario` y `netflix_db.sql` con los nombres correctos):
        ```bash
        mysql -u tu_usuario -p Netflix < netflix - Base de datos.sql
        ```
    *   Ingresa la contraseña del usuario `tu_usuario`.

4.  **Ejecuta la aplicación:**
    *   Ejecuta el archivo `NetflixAppDemo.exe`.