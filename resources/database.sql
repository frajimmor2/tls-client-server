-- Drop databases if they exist
DROP DATABASE IF EXISTS serverdb;
DROP DATABASE IF EXISTS saltdb;

-- Create databases
CREATE DATABASE serverdb;
CREATE DATABASE saltdb;

-- Drop user if exists and create new one
DROP USER IF EXISTS 'serverdb_user'@'localhost';
DROP USER IF EXISTS 'saltdb_user'@'localhost';

CREATE USER 'serverdb_user'@'localhost' IDENTIFIED BY 'serverdb_password';
CREATE USER 'saltdb_user'@'localhost' IDENTIFIED BY 'salt_password';

-- Set privileges over databases
GRANT ALL PRIVILEGES ON serverdb.* TO 'serverdb_user'@'localhost';
GRANT ALL PRIVILEGES ON saltdb.* TO 'saltdb_user'@'localhost';

-- Seleccionar y crear tabla de usuarios en serverdb
USE serverdb;
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) UNIQUE NOT NULL,
    password LONGBLOB NOT NULL
);

-- Inserción de usuarios predefinidos
INSERT INTO users (id, username, password)
VALUES
    (1, 'usuario1', 0xf5938d242e58b30b026b145fe8acd0dfe7402df129fc6bc3bd00994e58c478d6),
    (2, 'usuario2', 0x326b149218443b0cc723d3e064d77eb86b67d4f0c5d81f911824578a92838f73);

-- Seleccionar y crear tabla de salts en saltdb
USE saltdb;
CREATE TABLE IF NOT EXISTS salts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    salt LONGBLOB NOT NULL
);

-- Inserción de salts correspondientes
INSERT INTO salts (id, salt)
VALUES
    (1, 0xb6db31c0e3dfb2fbb79c6bc19b0a83d4),
    (2, 0x202c56a0942b1c72d7ea747b1fd4d82f);

-- Apply changes
FLUSH PRIVILEGES;