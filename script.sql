DROP TABLE IF EXISTS accesos CASCADE;
DROP TABLE IF EXISTS frases CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;

CREATE TABLE usuarios (
    user_id SERIAL PRIMARY KEY,
    user_name VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) DEFAULT '',
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE frases (
    frase_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES usuarios(user_id) ON DELETE CASCADE,
    frase VARCHAR(100) NOT NULL
);

CREATE TABLE accesos (
    acceso_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES usuarios(user_id) ON DELETE CASCADE,
    fecha_inicio TIMESTAMP NOT NULL,
    fecha_fin TIMESTAMP,
    tipo_fin VARCHAR(20)
);