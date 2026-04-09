# PGPI-G1.7
Proyecto grupal para PGPI curso 2025/2026.

## Mockups
Puede encontrarlos [aquí](https://marvelapp.com/prototype/agedh8d)

## Para ejecutar el proyecto:

### Base de Datos (PostgreSQL)

1. **Instalar PostgreSQL**
   - Descargar e instalar desde: [https://www.postgresql.org/download/windows/](https://www.postgresql.org/download/windows/)  
   - Durante la instalación:
     - Mantener el puerto por defecto (`5432`).

2. **Abrir SQL Shell (psql) o pgAdmin**

3. **Crear base de datos `charmaway`**  
   ```bash
   psql -U postgres
   CREATE DATABASE charmaway;
   CREATE USER charmaway_user WITH PASSWORD 'charmaway_password';
   GRANT ALL PRIVILEGES ON DATABASE charmaway TO charmaway_user;
   ALTER USER charmaway_user CREATEDB;
   \c charmaway
   GRANT ALL PRIVILEGES ON SCHEMA public TO charmaway_user;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO charmaway_user;
   \q
   ```
   
### Proyecto
1. Crear y acceder a un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate (Linux/MacOS)
   venv\Scripts\activate (Windows)
   ```
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Acceder a la carpeta del proyecto:
   ```bash
   cd charmaway/
   ```
4. Aplicar migraciones:
   ```bash
   python manage.py migrate
   ```
5. Aplicar seeders (datos):
   ```bash
   python seed_all.py
   ```
5. Ejecutar la aplicación:
   ```bash
   python manage.py runserver
   ```

### Stripe:   

1. Para que stripe funcione y procese los pagos es necesario tener una cuenta de stripe.

2. Después es importante acceder a nuestro dashboard de stripe para obtener tanto nuestor publishable token como nuestro private/secret token.

3. Usa el .env.example como .env.
   ```bash
   mv .env.example .env
   ```

4. Sustituye los campos requeridos con tus tokens.

5. Para obtener el webhook token, debes instalar el cli de stripe.

6. Una vez descargado y puesto en nuestro path, debemos ejecutar en una pantalla cmd.
   ```bash
   stripe listen --forward-to localhost:<PUERTO>/webhook
   ```

    Siendo PUERTO el puerto donde esté escuchando nuestra aplicación, en nuestro caso por defecto es el 8000.

7. Se mostrará este mensaje o uno similar:
  Ready! Your webhook signing secret is whsec_ABC123...
  whsec_ABC123... será el token que debe sustituirse en el .env.

8.Nuestro servicio estará escuchando y podrá probarse con una tarjeta de prueba:
  ```
    Tarjeta de prueba -> 4242 4242 4242 4242 11/44 111
  ```

9. Podremos ver las llamadas que nos llegan al webhook desde el cmd donde ejecutamos nuestro comando.

10. En nuestro dashboard de Stripe aparecerán también dichos movimientos.

### Tests:
1. Para que django los detecte, los tests de cada módulo tienen que estar en un archivo llamado explícitamente 'tests.py' dentro de cada uno de los módulos correspondientes.
2. Para ejecutar los tests:
   ```bash
   pytest
   ```
