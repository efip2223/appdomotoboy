import psycopg2
from psycopg2.extras import DictCursor
import streamlit as st
import hashlib

def obter_conexao():
    return psycopg2.connect(st.secrets["postgres"]["url"])

def gerar_hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def criar_tabela():
    conn = obter_conexao()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        nome VARCHAR(100) NOT NULL,
        senha VARCHAR(100) NOT NULL,
        perfil VARCHAR(20) NOT NULL
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estabelecimentos (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(100) NOT NULL
    );
    """)
    
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
    
    cursor.execute("SELECT COUNT(*) FROM usuarios;")
    if cursor.fetchone()[0] == 0:
        senha_segura = gerar_hash_senha("admin123")
        cursor.execute(
            "INSERT INTO usuarios (username, nome, senha, perfil) VALUES (%s, %s, %s, %s);",
            ("admin", "Administrador", senha_segura, "admin")
        )
        
    conn.commit()
    cursor.close()
    conn.close()

def autenticar_usuario(username, senha):
    conn = obter_conexao()
    cursor = conn.cursor(cursor_factory=DictCursor)
    senha_criptografada = gerar_hash_senha(senha)
    u_clean = str(username).strip().lower()
    
    cursor.execute("SELECT * FROM usuarios WHERE LOWER(TRIM(username)) = %s AND senha = %s;", (u_clean, senha_criptografada))
    usuario = cursor.fetchone()
    
    if not usuario:
        cursor.execute("SELECT * FROM usuarios WHERE LOWER(TRIM(username)) = %s AND senha = %s;", (u_clean, senha))
        usuario = cursor.fetchone()
        
    cursor.close()
    conn.close()
    return usuario

def cadastrar_entregas(bairro, valor, status_pagamento, estabelecimento, data, usuario):
    conn = obter_conexao()
    cursor = conn.cursor()
    u_clean = str(usuario).strip().lower()
    
    cursor.execute(
        "INSERT INTO entregas (bairro, valor, status, estabelecimento, data, usuario) VALUES (%s, %s, %s, %s, %s, %s);",
        (bairro, valor, status_pagamento, estabelecimento, data, u_clean)
    )
    conn.commit()
    cursor.close()
    conn.close()
    st.cache_data.clear()

@st.cache_data(ttl=60)
def listar_entregas(username=None):
    conn = obter_conexao()
    cursor = conn.cursor()
    if username:
        u_clean = str(username).strip().lower()
        cursor.execute("SELECT id, bairro, valor, status, estabelecimento, data, usuario FROM entregas WHERE LOWER(TRIM(usuario)) = %s ORDER BY id DESC;", (u_clean,))
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
    st.cache_data.clear()

def deletar_entrega_por_id(id_entrega, username):
    conn = obter_conexao()
    cursor = conn.cursor()
    u_clean = str(username).strip().lower()
    cursor.execute("DELETE FROM entregas WHERE id = %s AND LOWER(TRIM(usuario)) = %s;", (id_entrega, u_clean))
    conn.commit()
    cursor.close()
    conn.close()
    st.cache_data.clear()

@st.cache_data(ttl=60)
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
    st.cache_data.clear()

def deletar_estabelecimento(id_):
    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM estabelecimentos WHERE id = %s;", (id_,))
    conn.commit()
    cursor.close()
    conn.close()
    st.cache_data.clear()

@st.cache_data(ttl=60)
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
    senha_criptografada = gerar_hash_senha(senha)
    u_clean = str(username).strip().lower()
    cursor.execute("INSERT INTO usuarios (username, nome, senha, perfil) VALUES (%s, %s, %s, %s);", (u_clean, nome, senha_criptografada, perfil))
    conn.commit()
    cursor.close()
    conn.close()
    st.cache_data.clear()

def deletar_usuario(id_):
    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = %s;", (id_,))
    conn.commit()
    cursor.close()
    conn.close()
    st.cache_data.clear()
