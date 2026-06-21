import psycopg2
from psycopg2.extras import DictCursor
import streamlit as st

def obter_conexao():
    # Puxa a URL de conexão direto e seguro dos Secrets do Streamlit
    return psycopg2.connect(st.secrets["postgres"]["url"])

def criar_tabela():
    conn = obter_conexao()
    cursor = conn.cursor()
    
    # 1. Tabela de Usuários
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        nome VARCHAR(100) NOT NULL,
        senha VARCHAR(100) NOT NULL,
        perfil VARCHAR(20) NOT NULL
    );
    """)
    
    # 2. Tabela de Estabelecimentos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estabelecimentos (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(100) NOT NULL
    );
    """)
    
    # 3. Tabela de Entregas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS entregas (
        id SERIAL PRIMARY KEY,
        bairro VARCHAR(100) NOT NULL,
        valor NUMERIC(10, 2) NOT NULL,
        status VARCHAR(20) NOT NULL,
        estabelecimento VARCHAR(100) NOT NULL,
        data VARCHAR(20) NOT NULL,
        usuario VARCHAR(50) NOT NULL
    );
    """)
    
    # Cria um usuário administrador padrão caso o banco esteja totalmente vazio
    cursor.execute("SELECT COUNT(*) FROM usuarios;")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO usuarios (username, nome, senha, perfil) VALUES (%s, %s, %s, %s);",
            ("admin", "Administrador", "admin123", "admin")
        )
        
    conn.commit()
    cursor.close()
    conn.close()

def autenticar_usuario(username, senha):
    conn = obter_conexao()
    cursor = conn.cursor(cursor_factory=DictCursor)
    cursor.execute("SELECT * FROM usuarios WHERE username = %s AND senha = %s;", (username, senha))
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()
    return usuario

def cadastrar_entregas(bairro, valor, status_pagamento, estabelecimento, data, usuario):
    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO entregas (bairro, valor, status, estabelecimento, data, usuario) VALUES (%s, %s, %s, %s, %s, %s);",
        (bairro, valor, status_pagamento, estabelecimento, data, usuario)
    )
    conn.commit()
    cursor.close()
    conn.close()

def listar_entregas(username=None):
    conn = obter_conexao()
    cursor = conn.cursor()
    if username:
        cursor.execute("SELECT id, bairro, valor, status, estabelecimento, data, usuario FROM entregas WHERE usuario = %s ORDER BY id DESC;", (username,))
    else:
        cursor.execute("SELECT id, bairro, valor, status, estabelecimento, data, usuario FROM entregas ORDER BY id DESC;")
    dados = cursor.fetchall()
    cursor.close()
    conn.close()
    return dados

def atualizar_status(id_, status):
    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("UPDATE entregas SET status = %s WHERE id = %s;", (status, id_))
    conn.commit()
    cursor.close()
    conn.close()

def listar_estabelecimentos():
    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM estabelecimentos ORDER BY nome ASC;")
    dados = cursor.fetchall()
    cursor.close()
    conn.close()
    return dados

def cadastrar_estabelecimento(nome):
    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO estabelecimentos (nome) VALUES (%s);", (nome,))
    conn.commit()
    cursor.close()
    conn.close()

def deletar_estabelecimento(id_):
    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM estabelecimentos WHERE id = %s;", (id_,))
    conn.commit()
    cursor.close()
    conn.close()

def listar_usuarios():
    conn = obter_conexao()
    cursor = conn.cursor(cursor_factory=DictCursor)
    cursor.execute("SELECT id, username, nome, perfil FROM usuarios ORDER BY nome ASC;")
    dados = cursor.fetchall()
    cursor.close()
    conn.close()
    return dados

def cadastrar_usuario(username, nome, senha, perfil):
    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios (username, nome, senha, perfil) VALUES (%s, %s, %s, %s);", (username, nome, senha, perfil))
    conn.commit()
    cursor.close()
    conn.close()

def deletar_usuario(id_):
    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = %s;", (id_,))
    conn.commit()
    cursor.close()
    conn.close()

def deletar_entrega_por_id(id_entrega, username):
    import sqlite3
    conn = sqlite3.connect('velox.db')
    cursor = conn.cursor()
    
    try:
        # Tenta deletar usando a coluna padrão 'id'
        cursor.execute("DELETE FROM entregas WHERE id = ? AND usuario = ?", (id_entrega, username))
    except sqlite3.OperationalError:
        # Se der erro de coluna, tenta usando 'id_entrega' (comum em algumas versões do seu db)
        cursor.execute("DELETE FROM entregas WHERE id_entrega = ? AND usuario = ?", (id_entrega, username))
        
    conn.commit()
    conn.close()
