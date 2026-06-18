-- DROP DATABASE IF EXISTS devlog;
 
CREATE DATABASE IF NOT EXISTS devlog
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
 
USE devlog;
 
-- DROP TABLE IF EXISTS funcoe;
CREATE TABLE IF NOT EXISTS funcoes(
    id_funcao BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(20) NOT NULL UNIQUE,
    status ENUM('Ativo', 'Inativo') DEFAULT 'Ativo',
    descricao VARCHAR(255),
    gerenciar_usuarios BOOLEAN DEFAULT 0,
    gerenciar_linguagens BOOLEAN DEFAULT 0,
    gerenciar_recursos BOOLEAN DEFAULT 0,
    gerenciar_funcoes BOOLEAN DEFAULT 0,
 
    -- log
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    alterado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);
 
-- DROP TABLE IF EXISTS usuario;
CREATE TABLE IF NOT EXISTS usuario(
    id_cliente BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
 
    funcao_id BIGINT UNSIGNED NOT NULL,
 
    -- log
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    alterado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
 
    -- relacionamento
    CONSTRAINT fk_usuario_funcao
    FOREIGN KEY (funcao_id) REFERENCES funcoes (id_funcao)
);
 
-- DROP TABLE IF EXISTS linguagens;
CREATE TABLE IF NOT EXISTS linguagens(
    id_linguagens BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(20) NOT NULL UNIQUE,
    status ENUM('Quero estudar', 'Estudando', 'Concluido') DEFAULT 'Quero estudar',
    nivel ENUM('Iniciante', 'Intermediário', 'Avançado') DEFAULT 'Iniciante',
    notas VARCHAR(255),
 
    -- log
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    alterado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);
 
-- DROP TABLE IF EXISTS recursos;
CREATE TABLE IF NOT EXISTS recursos(
    id_recurso BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(100) NOT NULL,
    tipo ENUM('Site', 'Vídeo', 'Livro', 'Outro', 'Curso', 'Documentação') DEFAULT 'Site',
    url VARCHAR(255),
    linguagem VARCHAR(20),
    nota VARCHAR(255),
 
    -- log
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    alterado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);
