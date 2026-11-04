CREATE TABLE usuarios (
    usuario VARCHAR(50) PRIMARY KEY,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE frases (
    id SERIAL PRIMARY KEY,
    frase VARCHAR(255) NOT NULL,
    usuario VARCHAR(50) REFERENCES usuarios(usuario)
);
