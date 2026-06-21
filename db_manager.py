import psycopg2
from psycopg2.extras import DictCursor
import streamlit as st
import hashlib  # Biblioteca nativa para segurança de senhas

def obter_conexao():
    # Puxa a URL de conexão direto e seguro dos Secrets do Streamlit
    return psycopg2.connect(st.secrets["postgres"]["url"])

def gerar_hash_senha(senha):
    # Transforma a senha em um código seguro de 64 caracteres (SHA-256)
    return hashlib.sha256(senha.encode()).hexdigest()

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
        # O admin padrão agora nasce com a senha criptografada por segurança
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
    # Criptografa a senha digitada para comparar com o código salvo no banco
    senha_criptografada = gerar_hash_senha(senha)
    cursor.execute("SELECT * FROM usuarios WHERE username = %s AND senha = %s;", (username, senha_criptografada))
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
    # Limpa o cache para que a nova entrega apareça imediatamente na tela
    st.cache_data.clear()

# Cache de 60 segundos para evitar viagens internacionais desnecessárias a cada clique
@st.cache_data(ttl=60)
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
    # Limpa o cache para atualizar o status alterado instantaneamente na tela
    st.cache_data.clear()

# ── NOVA FUNÇÃO DE EXCLUSÃO INTEGRADA AO POSTGRES ─────────────────────────────
def deletar_entrega_por_id(id_entrega, username):
    conn = obter_conexao()
    cursor = conn.cursor()
    
    # Deleta usando segurança por ID e por Usuário dono do registro no Postgres
    cursor.execute("DELETE FROM entregas WHERE id = %s AND usuario = %s;", (id_entrega, username))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    # Zera o cache na hora para sumir do gráfico instantaneamente!
    st.cache_data.clear()

# Cache para listar estabelecimentos de forma ultra rápida
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
    # Limpa o cache para atualizar a lista de estabelecimentos
    st.cache_data.clear()

def deletar_estabelecimento(id_):
    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM estabelecimentos WHERE id = %s;", (id_,))
    conn.commit()
    cursor.close()
    conn.close()
    # Limpa o cache para remover o estabelecimento sumir da lista na hora
    st.cache_data.clear()

# Cache para carregar a lista de usuários instantaneamente
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
    # Protege a senha de novos usuários criados no sistema
    senha_criptografada = gerar_hash_senha(senha)
    cursor.execute("INSERT INTO usuarios (username, nome, senha, perfil) VALUES (%s, %s, %s, %s);", (username, nome, senha_criptografada, perfil))
    conn.commit()
    cursor.close()
    conn.close()
    # Limpa o cache para que o novo usuário apareça na lista administrativa
    st.cache_data.clear()

def deletar_usuario(id_):
    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = %s;", (id_,))
    conn.commit()
    cursor.close()
    conn.close()
    # Limpa o cache após deletar um usuário
    st.cache_data.clear()
