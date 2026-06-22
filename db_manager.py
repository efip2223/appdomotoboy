import psycopg2
from psycopg2.extras import DictCursor
import streamlit as st
import hashlib


# ─── Conexão ────────────────────────────────────────────────────────────────

def obter_conexao():
    return psycopg2.connect(st.secrets["postgres"]["url"])


def gerar_hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()


# ─── Setup inicial (roda uma única vez via @st.cache_resource) ───────────────

@st.cache_resource
def criar_tabela():
    """Cria as tabelas e o admin padrão. Executa apenas uma vez por processo."""
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
        nome VARCHAR(100) UNIQUE NOT NULL
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
            ("admin", "Administrador", senha_segura, "admin"),
        )

    conn.commit()
    cursor.close()
    conn.close()


# ─── Cache granular (invalida só o necessário) ───────────────────────────────

def _invalidar_cache_entregas(username: str):
    """Invalida apenas o cache de entregas do usuário afetado."""
    listar_entregas.clear(username=username)


def _invalidar_cache_estabelecimentos():
    listar_estabelecimentos.clear()


def _invalidar_cache_usuarios():
    listar_usuarios.clear()


# ─── Usuários ────────────────────────────────────────────────────────────────

def autenticar_usuario(username: str, senha: str):
    conn = obter_conexao()
    cursor = conn.cursor(cursor_factory=DictCursor)
    senha_hash = gerar_hash_senha(senha)
    u_clean = username.strip().lower()

    cursor.execute(
        "SELECT * FROM usuarios WHERE LOWER(TRIM(username)) = %s AND senha = %s;",
        (u_clean, senha_hash),
    )
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()
    return usuario


def obter_usuario_por_username(username: str):
    conn = obter_conexao()
    cursor = conn.cursor(cursor_factory=DictCursor)
    u_clean = username.strip().lower()
    cursor.execute(
        "SELECT * FROM usuarios WHERE LOWER(TRIM(username)) = %s;", (u_clean,)
    )
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()
    return usuario


@st.cache_data(ttl=120)
def listar_usuarios():
    conn = obter_conexao()
    cursor = conn.cursor(cursor_factory=DictCursor)
    cursor.execute("SELECT id, username, nome, perfil FROM usuarios ORDER BY nome ASC;")
    dados = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(u) for u in dados]


def cadastrar_usuario(username: str, nome: str, senha: str, perfil: str):
    conn = obter_conexao()
    cursor = conn.cursor()
    senha_hash = gerar_hash_senha(senha)
    u_clean = username.strip().lower()
    cursor.execute(
        "INSERT INTO usuarios (username, nome, senha, perfil) VALUES (%s, %s, %s, %s);",
        (u_clean, nome, senha_hash, perfil),
    )
    conn.commit()
    cursor.close()
    conn.close()
    _invalidar_cache_usuarios()


def deletar_usuario(id_: int):
    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = %s;", (id_,))
    conn.commit()
    cursor.close()
    conn.close()
    _invalidar_cache_usuarios()


# ─── Entregas ────────────────────────────────────────────────────────────────

@st.cache_data(ttl=30)
def listar_entregas(username: str | None = None):
    conn = obter_conexao()
    cursor = conn.cursor()
    if username:
        u_clean = username.strip().lower()
        cursor.execute(
            "SELECT id, bairro, valor, status, estabelecimento, data, usuario "
            "FROM entregas WHERE LOWER(TRIM(usuario)) = %s ORDER BY id DESC;",
            (u_clean,),
        )
    else:
        cursor.execute(
            "SELECT id, bairro, valor, status, estabelecimento, data, usuario "
            "FROM entregas ORDER BY id DESC;"
        )
    dados = cursor.fetchall()
    cursor.close()
    conn.close()
    return dados


def cadastrar_entregas(
    bairro: str,
    valor: float,
    status_pagamento: str,
    estabelecimento: str,
    data: str,
    usuario: str,
):
    conn = obter_conexao()
    cursor = conn.cursor()
    u_clean = usuario.strip().lower()
    cursor.execute(
        "INSERT INTO entregas (bairro, valor, status, estabelecimento, data, usuario) "
        "VALUES (%s, %s, %s, %s, %s, %s);",
        (bairro, valor, status_pagamento, estabelecimento, data, u_clean),
    )
    conn.commit()
    cursor.close()
    conn.close()
    _invalidar_cache_entregas(u_clean)


def atualizar_status(id_: int, status: str):
    conn = obter_conexao()
    cursor = conn.cursor(cursor_factory=DictCursor)
    # Descobre o usuário dono da entrega para invalidar só o cache dele
    cursor.execute("SELECT usuario FROM entregas WHERE id = %s;", (id_,))
    row = cursor.fetchone()
    cursor.execute("UPDATE entregas SET status = %s WHERE id = %s;", (status, id_))
    conn.commit()
    cursor.close()
    conn.close()
    if row:
        _invalidar_cache_entregas(row["usuario"])


def deletar_entrega_por_id(id_entrega: int, username: str):
    conn = obter_conexao()
    cursor = conn.cursor()
    u_clean = username.strip().lower()
    cursor.execute(
        "DELETE FROM entregas WHERE id = %s AND LOWER(TRIM(usuario)) = %s;",
        (id_entrega, u_clean),
    )
    conn.commit()
    cursor.close()
    conn.close()
    _invalidar_cache_entregas(u_clean)


def deletar_todas_entregas_usuario(username: str):
    conn = obter_conexao()
    cursor = conn.cursor()
    u_clean = username.strip().lower()
    cursor.execute(
        "DELETE FROM entregas WHERE LOWER(TRIM(usuario)) = %s;", (u_clean,)
    )
    conn.commit()
    cursor.close()
    conn.close()
    _invalidar_cache_entregas(u_clean)


# ─── Estabelecimentos ────────────────────────────────────────────────────────

@st.cache_data(ttl=120)
def listar_estabelecimentos():
    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM estabelecimentos ORDER BY nome ASC;")
    dados = cursor.fetchall()
    cursor.close()
    conn.close()
    return dados


def cadastrar_estabelecimento(nome: str) -> bool:
    """Retorna True se inserido, False se já existia (deduplicação)."""
    conn = obter_conexao()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO estabelecimentos (nome) VALUES (%s) ON CONFLICT (nome) DO NOTHING RETURNING id;",
            (nome.strip(),),
        )
        inserido = cursor.fetchone() is not None
        conn.commit()
    except Exception:
        conn.rollback()
        inserido = False
    finally:
        cursor.close()
        conn.close()
    if inserido:
        _invalidar_cache_estabelecimentos()
    return inserido


def deletar_estabelecimento(id_: int):
    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM estabelecimentos WHERE id = %s;", (id_,))
    conn.commit()
    cursor.close()
    conn.close()
    _invalidar_cache_estabelecimentos()
