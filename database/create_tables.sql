-- database/create_tables.sql
-- Script de criação das tabelas (baseado no DER do Acervia)

CREATE DATABASE IF NOT EXISTS biblioteca_pessoal;
USE biblioteca_pessoal;

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT PRIMARY KEY AUTO_INCREMENT,
    nome_completo VARCHAR(255) NOT NULL,
    login VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    perfil ENUM('admin', 'operador') DEFAULT 'operador',
    ativo BOOLEAN DEFAULT TRUE,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS permissoes (
    id_permissao INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    cadastrar BOOLEAN DEFAULT FALSE,
    alterar BOOLEAN DEFAULT FALSE,
    excluir BOOLEAN DEFAULT FALSE,
    emprestimo BOOLEAN DEFAULT FALSE,
    gerenciar_localizacao BOOLEAN DEFAULT FALSE,
    gerenciar_usuarios BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS estantes (
    id_estante INT PRIMARY KEY AUTO_INCREMENT,
    nome_estante VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS prateleiras (
    id_prateleira INT PRIMARY KEY AUTO_INCREMENT,
    id_estante INT NOT NULL,
    nome_prateleira VARCHAR(100) NOT NULL,
    FOREIGN KEY (id_estante) REFERENCES estantes(id_estante) ON DELETE CASCADE,
    UNIQUE KEY unique_prateleira (id_estante, nome_prateleira)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS livros (
    id_livro INT PRIMARY KEY AUTO_INCREMENT,
    titulo VARCHAR(255) NOT NULL,
    -- Mantida apenas para compatibilidade com bancos criados pela versão antiga.
    autor VARCHAR(255) NULL,
    isbn VARCHAR(20) UNIQUE,
    ano_publicacao INT,
    genero VARCHAR(100),
    id_prateleira INT,
    foto_path VARCHAR(500),
    status ENUM('disponivel', 'em_uso', 'emprestado') DEFAULT 'disponivel',
    observacao TEXT,
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_usuario_cadastro INT,
    FOREIGN KEY (id_prateleira) REFERENCES prateleiras(id_prateleira) ON DELETE SET NULL,
    FOREIGN KEY (id_usuario_cadastro) REFERENCES usuarios(id_usuario) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Compatibilidade com bancos criados antes da separação dos autores.
ALTER TABLE livros MODIFY COLUMN autor VARCHAR(255) NULL;

CREATE TABLE IF NOT EXISTS autores (
    id_autor INT PRIMARY KEY AUTO_INCREMENT,
    nome_autor VARCHAR(255) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS livro_autores (
    id_livro INT NOT NULL,
    id_autor INT NOT NULL,
    PRIMARY KEY (id_livro, id_autor),
    FOREIGN KEY (id_livro) REFERENCES livros(id_livro) ON DELETE CASCADE,
    FOREIGN KEY (id_autor) REFERENCES autores(id_autor) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS exemplares (
    id_exemplar INT PRIMARY KEY AUTO_INCREMENT,
    id_livro INT NOT NULL,
    codigo_tombo VARCHAR(100) UNIQUE,
    id_prateleira INT,
    foto_path VARCHAR(500),
    status ENUM('disponivel', 'em_uso', 'emprestado') DEFAULT 'disponivel',
    observacao TEXT,
    FOREIGN KEY (id_livro) REFERENCES livros(id_livro) ON DELETE CASCADE,
    FOREIGN KEY (id_prateleira) REFERENCES prateleiras(id_prateleira) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS emprestimos (
    id_emprestimo INT PRIMARY KEY AUTO_INCREMENT,
    id_livro INT NOT NULL,
    data_emprestimo DATETIME DEFAULT CURRENT_TIMESTAMP,
    observacoes TEXT,
    data_devolucao DATETIME NULL,
    status ENUM('ativo', 'finalizado') DEFAULT 'ativo',
    FOREIGN KEY (id_livro) REFERENCES livros(id_livro) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Usuário administrador padrão (login: admin / senha: admin123)
INSERT INTO usuarios (nome_completo, login, senha, perfil, ativo)
VALUES ('Administrador', 'admin', 'admin123', 'admin', TRUE);

INSERT INTO permissoes (id_usuario, cadastrar, alterar, excluir, emprestimo, gerenciar_localizacao, gerenciar_usuarios)
VALUES (1, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE);

INSERT INTO estantes (nome_estante) VALUES ('Estante 1'), ('Estante 2'), ('Estante 3');
INSERT INTO prateleiras (id_estante, nome_prateleira) VALUES (1, 'Prateleira A'), (1, 'Prateleira B'), (2, 'Prateleira C');