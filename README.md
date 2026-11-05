# Proyecto Frases

Este proyecto constituye una tarea del módulo DSW - Desarrollo en Entorno Servidor.

## Fase 1

Se comienza creando una aplicación web que por código guarde las frases, usuarios y contraseñas y las guarde dentro de un fichero txt.

Para ello se utiliza:
- Python
- Flask

Se debe crear:
- frases.txt
- usuarios.txt

## Fase 2

Se emuló la conexión a una base de datos PostgreSQL, para ello se creó un .env donde se vincularon las variables de entorno al código.

Se debe crear:
- .env.
- script.sql (script para formular base de datos).
- crear_tablas.py (script para crear base de datos).

## Fase 3

Se utilizó bcrypt para encriptar las contraseña y mejorar la seguridad de los usuarios.

Se necesita:
- bcrypt

Se modificó:
- app.py
- crear_tablas.py
- script.sql

Los tres para añadir una nueva fila que almacenase los hashes en vez de las contraseñas.
