# Charmaway — PAI-4 DevSecOps

[![CI](https://github.com/mjnizac/PAI-5-Charmaway/actions/workflows/ci.yml/badge.svg)](https://github.com/mjnizac/PAI-5-Charmaway/actions/workflows/ci.yml)
[![DevSecOps](https://github.com/mjnizac/PAI-5-Charmaway/actions/workflows/devsecops.yml/badge.svg)](https://github.com/mjnizac/PAI-5-Charmaway/actions/workflows/devsecops.yml)

Proyecto Django para la asignatura PAI-4. Incluye un pipeline DevSecOps completo con integración en DefectDojo.

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
2. Ejecutar desde `charmaway/`:
   ```bash
   cd charmaway/
   pytest
   ```

## Pipeline DevSecOps

El pipeline se activa en cada push a `develop` o `main` y ejecuta cuatro fases de seguridad. Los resultados se suben a DefectDojo automáticamente para acumular historial.

| Fase | Herramienta | Tipo | Engagement en DefectDojo |
|------|------------|------|--------------------------|
| 1 | pip-audit | SCA — dependencias con CVE | CI – SCA |
| 2 | Bandit | SAST — código inseguro en Python/Django | CI – SAST |
| 3 | Trivy | IaC — secrets expuestos, misconfigs | CI – IaC |
| 4 | OWASP ZAP | DAST — scan dinámico contra la app en ejecución | CI – DAST |

### Secrets necesarios en GitHub

Configurar en *Settings → Secrets and variables → Actions*:

| Secret | Descripción |
|--------|-------------|
| `DEFECTDOJO_URL` | URL base de la instancia DefectDojo (ej. `http://localhost:8080`) |
| `DEFECTDOJO_API_KEY` | Token de API de DefectDojo |

Si los secrets no están configurados, los pasos de subida a DefectDojo se omiten automáticamente (los scans igualmente se ejecutan y quedan como artefactos).

### CodeRabbit

Las PRs hacia `develop` y `main` reciben revisión automática por CodeRabbit. Requiere instalar la [GitHub App de CodeRabbit](https://github.com/apps/coderabbit-ai) en el repositorio. La configuración está en `.coderabbit.yaml`.
