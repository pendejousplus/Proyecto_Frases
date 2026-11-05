# 📝 Proyecto Frases — Aplicación Web Full-Stack con Flask

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white)
![Security](https://img.shields.io/badge/Auth-Bcrypt%20%2B%20WTForms-success)
![Server](https://img.shields.io/badge/Deploy-Nginx%20%2B%20Gunicorn-green?logo=nginx&logoColor=white)

Aplicación web desarrollada para el módulo **DSW (Desarrollo Web en Entorno Servidor)** de 2º de DAW. El proyecto muestra la evolución completa de una plataforma web desde un prototipo basado en ficheros locales hasta una arquitectura de producción desplegada en servidores VPS con base de datos relacional remota, hashing criptográfico de contraseñas, validación estricta en servidor y auditoría de sesiones.

---

## 🏗️ Arquitectura del Sistema en Producción

La aplicación se despliega separando el servidor de aplicaciones (VPS 1) del servidor de base de datos (VPS 2):

```text
[ Cliente / Navegador ]
          │
          ▼ (HTTP Puerto 5010)
[ Nginx (Proxy Inverso) ] ──(Redirección interna 127.0.0.1:8010)──> [ Servidor WSGI Gunicorn ]
                                                                                │
                                                                                ▼
                                                                     [ Aplicación Flask ]
                                                                                │
                                                                                ▼ (TCP/IP Puerto 5432)
                                                                  [ PostgreSQL Remoto (VPS 2) ]
```

---

## Evolución del Proyecto (Fases de Desarrollo)

### Fase 1: Prototipo Inicial con Persistencia en Ficheros
Desarrollo de la lógica base de autenticación, sesiones de usuario y almacenamiento de frases utilizando lectura y escritura de ficheros de texto plano en el servidor.
* **Tecnologías:** Python, Flask (`session`, `request`, `render_template`).
* **Archivos implementados:** `app.py`, `usuarios.txt`, `frases.txt`, `templates/login.html`, `templates/frases.html`.

### Fase 2: Migración a Base de Datos Relacional (PostgreSQL) y Variables de Entorno
Sustitución del sistema de ficheros por una base de datos **PostgreSQL** alojada en un servidor remoto. Desacoplamiento de las credenciales sensibles mediante variables de entorno para proteger la seguridad del repositorio.
* **Tecnologías:** `psycopg2-binary`, `python-dotenv`, PostgreSQL.
* **Archivos añadidos/modificados:**
  * `.env`: Almacenamiento privado de credenciales de conexión (excluido de Git).
  * `script.sql`: Definición DDL de las tablas relacionales (`usuarios` y `frases`) con claves primarias autoincrementales (`SERIAL`) y claves foráneas (`FOREIGN KEY`).
  * `crear_tablas.py`: Script de automatización para inicializar el esquema en el servidor remoto.

### Fase 3: Seguridad Criptográfica con Bcrypt
Eliminación del almacenamiento de contraseñas en texto plano. Implementación de hashing adaptativo con semilla aleatoria (*salt*) mediante **bcrypt** durante el registro y verificación segura en el inicio de sesión.
* **Tecnologías:** `bcrypt`.
* **Archivos modificados:** `app.py`, `script.sql`, `crear_tablas.py`.
* **Cambios clave:** Se añadió una nueva **columna** `password_hash VARCHAR(255)` en la tabla `usuarios` para almacenar el hash codificado, verificando las credenciales con `bcrypt.checkpw()`.

### Fase 4: Validación de Datos en el Servidor (Backend & Frontend)
Implementación de reglas estrictas de validación en el servidor para evitar la inserción de datos malformados o inyecciones, complementada con retroalimentación visual de errores y requisitos en la interfaz.
* **Tecnologías:** `Flask-WTF`, `WTForms`, `email-validator`.
* **Archivos modificados/añadidos:** `app.py`, `templates/frases.html`, `templates/login.html` (y scripts de laboratorio `validacion_datos.py`, `templates/registro.html`, `templates/resultado.html`).
* **Reglas aplicadas:**
  * **Usuario:** Obligatorio, entre 5 y 20 caracteres exclusivamente alfanuméricos (`Regexp`).
  * **Contraseña:** Obligatoria, mínimo 8 caracteres y confirmación idéntica (`EqualTo`).
  * **Frase:** Obligatoria, longitud restringida entre 10 y 100 caracteres (`Length`).

### Fase 5: Control de Inactividad y Auditoría de Accesos para Administrador
Incorporación de expiración automática de sesión por tiempo de inactividad configurable desde `.env` y creación de un sistema de registro de auditoría en base de datos.
* **Archivos modificados:** `app.py`, `script.sql`, `crear_tablas.py`, `templates/frases.html`, `templates/login.html`, `.env`.
* **Funcionalidades:**
  * **Cierre por inactividad:** Si el usuario supera el límite configurado en `TIEMPO_SESION` sin interactuar, el sistema invalida la sesión automáticamente, registra el motivo de salida como `inactividad` y redirige al login.
  * **Panel de Auditoría (`admin`):** El usuario administrador visualiza las frases globales de todos los autores (mediante consultas `INNER JOIN`) y una tabla detallada con el historial de sesiones (`fecha_inicio`, `fecha_fin` y si el cierre fue `voluntaria` o por `inactividad`).

---

## Modelo de Base de Datos

El esquema relacional consta de tres tablas conectadas mediante claves foráneas con borrado en cascada (`ON DELETE CASCADE`):

* **`usuarios`**: `user_id` (PK), `user_name` (UNIQUE), `password`, `password_hash`.
* **`frases`**: `frase_id` (PK), `user_id` (FK -> `usuarios`), `frase`.
* **`accesos`**: `acceso_id` (PK), `user_id` (FK -> `usuarios`), `fecha_inicio`, `fecha_fin`, `tipo_fin`.

---

## Estructura del Repositorio

```text
proyecto_frases/
├── app.py                  # Aplicación principal Flask (Rutas, Auth, Sesiones, Consultas)
├── crear_tablas.py         # Script de inicialización de tablas en PostgreSQL
├── script.sql              # Esquema SQL de las tablas usuarios, frases y accesos
├── validacion_datos.py     # Script de práctica tutorizada de validación con WTForms
├── requirements.txt        # Dependencias del entorno virtual Python
├── .env.example            # Plantilla de variables de entorno
├── .gitignore              # Exclusión de entorno virtual y credenciales (.env)
└── templates/
    ├── login.html          # Vista de inicio de sesión y registro con guías de validación
    ├── frases.html         # Panel de usuario y tabla de auditoría para el rol admin
```

---

## Instalación y Despliegue Local / VPS

1. **Clonar el repositorio y acceder al directorio:**
   ```bash
   git clone [https://github.com/pendejousplus/Proyecto_Frases.git](https://github.com/pendejousplus/Proyecto_Frases.git)
   cd TU_REPOSITORIO
   ```

2. **Crear y activar el entorno virtual:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar las variables de entorno:**
   Crea un archivo `.env` a partir de `.env.example` con tus credenciales reales:
   ```ini
   DB_HOST=127.0.0.1
   DB_PORT=5432
   DB_NAME=nombre_bd
   DB_USER=usuario_bd
   DB_PASSWORD=tu_password
   SECRET_KEY=clave_secreta_segura
   TIEMPO_SESION=60
   ```

5. **Inicializar la base de datos en PostgreSQL:**
   ```bash
   python3 crear_tablas.py
   ```

6. **Ejecutar el servidor de producción con Gunicorn:**
   ```bash
   gunicorn -w 2 -b 127.0.0.1:8010 app:app --daemon
   ```