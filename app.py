import streamlit as st
from datetime import date, timedelta
import db_manager as database
import pandas as pd
import plotly.express as px
from streamlit_cookies_controller import CookieController

# ─── Setup (uma única vez por processo) ─────────────────────────────────────
database.criar_tabela()

st.set_page_config(
    page_title="Velox — Entregas",
    layout="wide",
)

# ─── Cores ──────────────────────────────────────────────────────────────────
C_BG        = "#0d1117"
C_SURFACE   = "#161b22"
C_SURFACE2  = "#1c2330"
C_BORDER    = "#21262d"
C_ACCENT    = "#2f81f7"
C_GREEN     = "#3fb950"
C_GREEN_DIM = "#1a4a23"
C_AMBER     = "#d29922"
C_RED       = "#f85149"
C_RED_DIM   = "rgba(248,81,73,0.12)"
C_TEXT      = "#e6edf3"
C_MUTED     = "#7d8590"

# ─── CSS global (mobile-first) ───────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap');

/* Reset de overflow horizontal */
html, body {{ overflow-x: hidden !important; max-width: 100vw !important; }}

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    color: {C_TEXT};
    -webkit-tap-highlight-color: transparent;
}}

.stApp {{ background: {C_BG}; overflow-x: hidden !important; }}

section[data-testid="stSidebar"] {{
    background: {C_SURFACE} !important;
    border-right: 1px solid {C_BORDER} !important;
}}

/* ── Brand ── */
.brand {{
    font-family: 'Inter', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: {C_TEXT};
    line-height: 1;
    letter-spacing: -0.5px;
}}
.brand-accent {{ color: {C_ACCENT}; }}
.brand-tag {{
    display: inline-block;
    font-size: 0.6rem;
    font-weight: 600;
    color: {C_MUTED};
    text-transform: uppercase;
    letter-spacing: 0.15em;
    border: 1px solid {C_BORDER};
    border-radius: 3px;
    padding: 2px 6px;
    margin-left: 6px;
    vertical-align: middle;
}}

/* ── Tipografia ── */
.sec-title {{
    font-size: 1.05rem;
    font-weight: 600;
    color: {C_TEXT};
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid {C_BORDER};
    letter-spacing: -0.2px;
}}
.sec-eyebrow {{
    font-size: 0.62rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: {C_ACCENT};
    margin-bottom: 4px;
}}

/* ── KPI cards ── */
.kpi-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
    gap: 10px;
    margin-bottom: 16px;
}}
.kpi-card {{
    background: {C_SURFACE};
    border: 1px solid {C_BORDER};
    border-radius: 10px;
    padding: 14px 14px 12px;
}}
.kpi-label {{
    font-size: 0.6rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: {C_MUTED};
    margin-bottom: 6px;
}}
.kpi-value {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.25rem;
    font-weight: 600;
    color: {C_TEXT};
    line-height: 1;
    word-break: break-all;
}}
.kpi-value.green  {{ color: {C_GREEN};  }}
.kpi-value.amber  {{ color: {C_AMBER};  }}
.kpi-value.accent {{ color: {C_ACCENT}; }}
.kpi-sub {{ font-size: 0.65rem; color: {C_MUTED}; margin-top: 4px; }}

/* ── Inputs ── */
.stTextInput input,
.stNumberInput input,
.stSelectbox > div > div,
.stTextArea textarea {{
    background: {C_SURFACE} !important;
    border: 1px solid {C_BORDER} !important;
    color: {C_TEXT} !important;
    border-radius: 8px !important;
    font-size: 1rem !important;      /* 16px evita zoom automático no iOS */
    min-height: 44px !important;     /* área de toque mínima recomendada */
}}

/* ── Botões — tamanho de toque confortável ── */
.stButton > button {{
    background: {C_ACCENT} !important;
    color: #fff !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    border: none !important;
    border-radius: 8px !important;
    min-height: 44px !important;
    padding: 0 18px !important;
    transition: opacity 0.15s !important;
}}
.stButton > button:active {{ opacity: 0.75 !important; }}

.btn-ghost > button {{
    background: transparent !important;
    border: 1px solid {C_BORDER} !important;
    color: {C_MUTED} !important;
    border-radius: 8px !important;
    min-height: 44px !important;
}}
.btn-danger > button {{
    background: {C_RED_DIM} !important;
    border: 1px solid {C_RED} !important;
    color: {C_RED} !important;
    border-radius: 8px !important;
    min-height: 44px !important;
    font-weight: 600 !important;
}}
.btn-success > button {{
    background: {C_GREEN_DIM} !important;
    border: 1px solid {C_GREEN} !important;
    color: {C_GREEN} !important;
    border-radius: 8px !important;
    min-height: 44px !important;
    font-weight: 600 !important;
}}

/* ── Tabs ── */
div[data-testid="stTabs"] button {{
    color: {C_MUTED} !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    padding: 8px 10px !important;
}}
div[data-testid="stTabs"] button[aria-selected="true"] {{
    color: {C_ACCENT} !important;
    border-bottom-color: {C_ACCENT} !important;
}}

/* ── Card de entrega (substitui o dataframe no mobile) ── */
.entrega-card {{
    background: {C_SURFACE};
    border: 1px solid {C_BORDER};
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 12px;
}}
.entrega-info {{ flex: 1; min-width: 0; }}
.entrega-loja {{
    font-weight: 600;
    font-size: 0.9rem;
    color: {C_TEXT};
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.entrega-meta {{ font-size: 0.72rem; color: {C_MUTED}; margin-top: 2px; }}
.entrega-valor {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.95rem;
    font-weight: 600;
    color: {C_GREEN};
    white-space: nowrap;
}}
.badge-pago    {{ color: {C_GREEN}; font-size: 0.68rem; font-weight: 600; }}
.badge-pendente{{ color: {C_AMBER}; font-size: 0.68rem; font-weight: 600; }}

/* ── Perfil badge ── */
.perfil-badge {{
    display: inline-block;
    font-size: 0.65rem;
    font-weight: 600;
    padding: 2px 7px;
    border-radius: 20px;
    margin-left: 6px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    vertical-align: middle;
}}
.badge-admin       {{ background: rgba(47,129,247,.15); color: {C_ACCENT}; border: 1px solid {C_ACCENT}; }}
.badge-entregador  {{ background: rgba(63,185,80,.12);  color: {C_GREEN};  border: 1px solid {C_GREEN};  }}

/* ── Expanders ── */
.streamlit-expanderHeader {{ font-weight: 600 !important; font-size: 0.9rem !important; }}
</style>
""", unsafe_allow_html=True)

# ─── Plotly layout base ───────────────────────────────────────────────────────
LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=C_MUTED, family="Inter", size=10),
    margin=dict(l=5, r=5, t=28, b=5),
    xaxis=dict(gridcolor=C_BORDER, linecolor=C_BORDER, zeroline=False, fixedrange=True),
    yaxis=dict(gridcolor=C_BORDER, linecolor=C_BORDER, zeroline=False, fixedrange=True),
    dragmode=False,
)

# ─── Helpers ─────────────────────────────────────────────────────────────────

def fmt_brl(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def is_admin() -> bool:
    return st.session_state.get("perfil") == "admin"

def username_atual() -> str:
    return st.session_state.get("username", "")

def kpi_html(label: str, value: str, sub: str = "", color: str = "") -> str:
    cls = f"kpi-value {color}".strip()
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="{cls}">{value}</div>
        {sub_html}
    </div>"""

def kpi_grid(*cards: str) -> str:
    inner = "".join(cards)
    return f'<div class="kpi-grid">{inner}</div>'


# ════════════════════════════════════════════════════════════════════════════
# COOKIE CONTROLLER — inicializado uma única vez
# ════════════════════════════════════════════════════════════════════════════
if "cookie_controller" not in st.session_state:
    st.session_state["cookie_controller"] = CookieController()

controller: CookieController = st.session_state["cookie_controller"]

# Auto-login via cookie
if "usuario" not in st.session_state:
    cookie_username = controller.get("velox_username")
    if cookie_username:
        usuario_salvo = database.obter_usuario_por_username(cookie_username)
        if usuario_salvo:
            st.session_state["usuario"]  = usuario_salvo["nome"]
            st.session_state["username"] = usuario_salvo["username"]
            st.session_state["perfil"]   = usuario_salvo["perfil"]


# ════════════════════════════════════════════════════════════════════════════
# TELA DE LOGIN
# ════════════════════════════════════════════════════════════════════════════
if "usuario" not in st.session_state:
    st.markdown(
        '<div style="text-align:center;margin-top:48px">'
        '<span class="brand">Velox<span class="brand-accent">.</span></span>'
        '</div>',
        unsafe_allow_html=True,
    )
    _, col_form, _ = st.columns([1, 1.4, 1])
    with col_form:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='font-size:1.1rem;font-weight:700;color:{C_TEXT};margin-bottom:4px;'>Entrar na conta</div>"
            f"<div style='font-size:0.78rem;color:{C_MUTED};margin-bottom:20px;'>Controle de entregas · Sobral CE</div>",
            unsafe_allow_html=True,
        )
        u_input = st.text_input("Usuário", placeholder="seu_usuario", key="li_user")
        p_input = st.text_input("Senha", type="password", placeholder="••••••••", key="li_pass")
        lembrar = st.checkbox("Manter conectado neste celular", value=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Entrar", use_container_width=True, key="btn_login"):
            if not u_input or not p_input:
                st.warning("Preencha o usuário e a senha.")
            else:
                usuario = database.autenticar_usuario(u_input, p_input)
                if usuario:
                    st.session_state["usuario"]  = usuario["nome"]
                    st.session_state["username"] = usuario["username"]
                    st.session_state["perfil"]   = usuario["perfil"]
                    if lembrar:
                        controller.set("velox_username", usuario["username"], max_age=2_592_000)
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
    st.stop()


# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        '<div class="brand">Velox<span class="brand-accent">.</span>'
        '<span class="brand-tag">Beta</span></div>',
        unsafe_allow_html=True,
    )

    badge_cls  = "badge-admin" if is_admin() else "badge-entregador"
    badge_text = "Admin" if is_admin() else "Entregador"
    st.markdown(
        f"""<div style='background:{C_SURFACE2};border:1px solid {C_BORDER};
            border-radius:8px;padding:12px 14px;margin-top:10px;'>
            <b>{st.session_state['usuario']}</b>
            <span class='perfil-badge {badge_cls}'>{badge_text}</span><br>
            <span style='color:{C_MUTED};font-size:0.72rem;'>@{username_atual()}</span>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Botão de logout
    st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
    if st.button("Sair da Conta", use_container_width=True, key="btn_sair"):
        for k in ["usuario", "username", "perfil"]:
            st.session_state.pop(k, None)
        controller.remove("velox_username")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Reset perigoso — escondido em expander para evitar clique acidental
    with st.expander("⚠️ Zona de perigo"):
        st.markdown(
            f"<p style='font-size:0.78rem;color:{C_MUTED};'>Apaga permanentemente <b>todas</b> as suas entregas. Não tem como desfazer.</p>",
            unsafe_allow_html=True,
        )
        st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
        if st.button("Apagar Todas as Minhas Entregas", use_container_width=True, key="btn_reset"):
            database.deletar_todas_entregas_usuario(username_atual())
            st.success("Histórico resetado!")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# BAIRROS
# ════════════════════════════════════════════════════════════════════════════
BAIRROS_SOBRAL = sorted([
    "Alto do Cristo", "Betânia", "Campos dos Velhos", "Centro",
    "Cohab I", "Cohab II", "Cohab III", "Gerardo Cristino",
    "Dom Expedito", "Expectativa", "Junco", "Novo Recanto",
    "Padre Palhano", "Parque Silvana", "Princesa Isabel", "Renato Parente",
    "Sinhá Sabóia", "Sumaré", "Terrenos Novos", "Vila União",
])


# ════════════════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════════════════
titulos_abas = ["➕ Novo", "📋 Lista", "⏳ Pagar", "🏢 Lojas", "📈 Painel"]
if is_admin():
    titulos_abas.append("👥 Staff")

abas = st.tabs(titulos_abas)


# ── ABA 0: NOVA ENTREGA ──────────────────────────────────────────────────────
with abas[0]:
    st.markdown(
        '<div class="sec-eyebrow">Registrar</div>'
        '<div class="sec-title">Nova Entrega</div>',
        unsafe_allow_html=True,
    )

    # Bairro
    bairros_opcoes = ["Selecionar bairro..."] + BAIRROS_SOBRAL + ["Outro (digitar)"]
    bairro_sel = st.selectbox("Bairro", bairros_opcoes, key="sel_bairro")
    if bairro_sel == "Outro (digitar)":
        bairro = st.text_input("Nome do bairro", placeholder="Digite o bairro", key="txt_bairro")
    elif bairro_sel == "Selecionar bairro...":
        bairro = ""
    else:
        bairro = bairro_sel

    # Estabelecimento
    estabs = database.listar_estabelecimentos()
    nomes_estabs = [e[1] for e in estabs]
    opcoes_estab = ["Selecionar estabelecimento..."] + nomes_estabs + ["Outro (digitar)"]
    estab_sel = st.selectbox("Estabelecimento", opcoes_estab, key="sel_estab")
    if estab_sel == "Outro (digitar)":
        estabelecimento = st.text_input("Nome do estabelecimento", placeholder="Digite o nome", key="txt_estab")
    elif estab_sel == "Selecionar estabelecimento...":
        estabelecimento = ""
    else:
        estabelecimento = estab_sel

    valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f", step=0.50)
    status_pagamento = st.selectbox("Pagamento", ["Pendente", "Pago"])

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✅ Registrar Entrega", use_container_width=True, key="btn_reg"):
        if not bairro.strip() or not estabelecimento.strip():
            st.warning("Preencha todos os campos antes de registrar.")
        elif valor <= 0:
            st.warning("Informe um valor maior que R$ 0,00.")
        else:
            database.cadastrar_entregas(
                bairro.strip(), valor, status_pagamento,
                estabelecimento.strip(), str(date.today()), username_atual()
            )
            st.success("✓ Entrega registrada!")


# ── ABA 1: HISTÓRICO ─────────────────────────────────────────────────────────
with abas[1]:
    st.markdown(
        '<div class="sec-eyebrow">Histórico</div>'
        '<div class="sec-title">Suas Entregas</div>',
        unsafe_allow_html=True,
    )

    entregas_raw = database.listar_entregas(username=username_atual())

    if not entregas_raw:
        st.info("Nenhuma entrega cadastrada ainda.")
    else:
        df = pd.DataFrame(
            entregas_raw,
            columns=["ID", "Bairro", "Valor(R$)", "Status", "Estabelecimento", "Data", "Usuario"],
        )
        df["Valor(R$)"] = pd.to_numeric(df["Valor(R$)"], errors="coerce")

        total_pagas   = int(df["Status"].value_counts().get("Pago", 0))
        total_pend    = int(df["Status"].value_counts().get("Pendente", 0))
        receita_conf  = df[df["Status"] == "Pago"]["Valor(R$)"].sum()

        st.markdown(
            kpi_grid(
                kpi_html("Total de Entregas", str(len(df)), f"{total_pagas} pagas · {total_pend} pend."),
                kpi_html("Receita Confirmada", fmt_brl(receita_conf), "caixa atual", "green"),
            ),
            unsafe_allow_html=True,
        )

        busca = st.text_input("🔍 Filtrar por bairro ou loja...", key="busca_hist")

        df_view = df.copy()
        if busca:
            mask = (
                df_view["Bairro"].str.contains(busca, case=False, na=False)
                | df_view["Estabelecimento"].str.contains(busca, case=False, na=False)
            )
            df_view = df_view[mask]

        st.markdown("<br>", unsafe_allow_html=True)

        # Cards mobile-friendly em vez de dataframe
        for _, row in df_view.iterrows():
            badge_cls = "badge-pago" if row["Status"] == "Pago" else "badge-pendente"
            badge_sym = "✓ Pago" if row["Status"] == "Pago" else "⏳ Pendente"
            col_card, col_del = st.columns([6, 1])
            with col_card:
                st.markdown(
                    f"""<div class="entrega-card">
                        <div class="entrega-info">
                            <div class="entrega-loja">{row['Estabelecimento']}</div>
                            <div class="entrega-meta">{row['Bairro']} · {row['Data']} · <span class="{badge_cls}">{badge_sym}</span></div>
                        </div>
                        <div class="entrega-valor">{fmt_brl(row['Valor(R$)'])}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
            with col_del:
                st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
                if st.button("✕", key=f"del_entrega_{int(row['ID'])}", use_container_width=True):
                    database.deletar_entrega_por_id(int(row["ID"]), username_atual())
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)


# ── ABA 2: PENDENTES ─────────────────────────────────────────────────────────
with abas[2]:
    st.markdown(
        '<div class="sec-eyebrow">Financeiro</div>'
        '<div class="sec-title">Taxas Pendentes</div>',
        unsafe_allow_html=True,
    )

    # Reutiliza os dados já carregados se disponíveis na mesma sessão
    entregas_raw2 = database.listar_entregas(username=username_atual())

    if not entregas_raw2:
        st.info("Nenhuma entrega cadastrada.")
    else:
        df2 = pd.DataFrame(
            entregas_raw2,
            columns=["ID", "Bairro", "Valor(R$)", "Status", "Estabelecimento", "Data", "Usuario"],
        )
        df2["Valor(R$)"] = pd.to_numeric(df2["Valor(R$)"], errors="coerce")
        df_pend = df2[df2["Status"] == "Pendente"].copy()

        if df_pend.empty:
            st.success("🎉 Tudo pago! Nenhuma pendência.")
        else:
            st.markdown(
                kpi_html(
                    "Total Pendente",
                    fmt_brl(df_pend["Valor(R$)"].sum()),
                    f"{len(df_pend)} taxa(s) em aberto",
                    "amber",
                ),
                unsafe_allow_html=True,
            )
            st.markdown("<br>", unsafe_allow_html=True)

            for _, row in df_pend.iterrows():
                st.markdown(
                    f"""<div class="entrega-card">
                        <div class="entrega-info">
                            <div class="entrega-loja">{row['Estabelecimento']}</div>
                            <div class="entrega-meta">{row['Bairro']} · {row['Data']}</div>
                        </div>
                        <div class="entrega-valor" style="color:{C_AMBER}">{fmt_brl(row['Valor(R$)'])}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
                st.markdown('<div class="btn-success">', unsafe_allow_html=True)
                if st.button("✓ Marcar como Pago", key=f"pagar_{int(row['ID'])}", use_container_width=True):
                    database.atualizar_status(int(row["ID"]), "Pago")
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='height:8px'></div>", unsafe_allow_html=True)


# ── ABA 3: ESTABELECIMENTOS ───────────────────────────────────────────────────
with abas[3]:
    st.markdown(
        '<div class="sec-eyebrow">Lojas</div>'
        '<div class="sec-title">Gerenciar Estabelecimentos</div>',
        unsafe_allow_html=True,
    )

    sub1, sub2 = st.tabs(["➕ Cadastro Individual", "📥 Importar em Massa"])

    with sub1:
        novo_nome = st.text_input("Nome do Local", placeholder="Ex: Burguer Central", key="nome_loja_ind")
        if st.button("Cadastrar Loja", use_container_width=True, key="btn_cad_loja"):
            nome_limpo = novo_nome.strip()
            if nome_limpo:
                inserido = database.cadastrar_estabelecimento(nome_limpo)
                if inserido:
                    st.success(f"'{nome_limpo}' cadastrado!")
                    st.rerun()
                else:
                    st.warning(f"'{nome_limpo}' já existe na lista.")
            else:
                st.warning("Digite um nome válido.")

    with sub2:
        st.markdown(
            f"<span style='font-size:0.82rem;color:{C_MUTED};'>"
            "Cole os nomes das lojas — um por linha ou separados por vírgula.</span>",
            unsafe_allow_html=True,
        )
        texto_massa = st.text_area(
            "Lista de Estabelecimentos",
            placeholder="Loja Exemplo A\nLoja Exemplo B\nLoja C, Loja D",
            height=140,
            key="txt_massa",
        )
        if st.button("🚀 Cadastrar Lista Completa", use_container_width=True, key="btn_massa"):
            if texto_massa.strip():
                lojas = list({
                    parte.strip()
                    for linha in texto_massa.split("\n")
                    for parte in linha.split(",")
                    if parte.strip()
                })
                contagem = sum(database.cadastrar_estabelecimento(l) for l in lojas)
                ignorados = len(lojas) - contagem
                msg = f"✓ {contagem} adicionadas!"
                if ignorados:
                    msg += f" ({ignorados} já existiam e foram ignoradas)"
                st.success(msg)
                if contagem:
                    st.rerun()
            else:
                st.warning("O campo está vazio.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f'<div style="font-size:0.85rem;font-weight:600;color:{C_TEXT};'
        f'margin-bottom:10px;">Lojas Cadastradas</div>',
        unsafe_allow_html=True,
    )

    estabs_lista = database.listar_estabelecimentos()
    if not estabs_lista:
        st.info("Nenhum estabelecimento cadastrado.")
    else:
        for e_id, e_nome in estabs_lista:
            col_nome, col_del = st.columns([6, 1])
            col_nome.markdown(
                f"<div style='padding:10px 0;border-bottom:1px solid {C_BORDER};"
                f"font-size:0.88rem;'>🏢 {e_nome}</div>",
                unsafe_allow_html=True,
            )
            with col_del:
                st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
                if st.button("✕", key=f"del_estab_{e_id}", use_container_width=True):
                    database.deletar_estabelecimento(id_=e_id)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)


# ── ABA 4: PAINEL ────────────────────────────────────────────────────────────
with abas[4]:
    st.markdown(
        '<div class="sec-eyebrow">Desempenho</div>'
        '<div class="sec-title">Painel de Indicadores</div>',
        unsafe_allow_html=True,
    )

    # Única query para toda a aba
    entregas_raw4 = database.listar_entregas(username=username_atual())

    if not entregas_raw4:
        st.info("Sem dados suficientes para gerar os painéis.")
    else:
        df4 = pd.DataFrame(
            entregas_raw4,
            columns=["ID", "Bairro", "Valor(R$)", "Status", "Estabelecimento", "Data", "Usuario"],
        )
        df4["Valor(R$)"] = pd.to_numeric(df4["Valor(R$)"], errors="coerce")
        df4["Data_p"] = pd.to_datetime(df4["Data"], errors="coerce").dt.date
        df4 = df4.dropna(subset=["Data_p"])

        hoje         = date.today()
        inicio_sem   = hoje - timedelta(days=hoje.weekday())
        inicio_mes   = hoje.replace(day=1)

        df_hoje  = df4[df4["Data_p"] == hoje]
        df_sem   = df4[df4["Data_p"] >= inicio_sem]
        df_mes   = df4[df4["Data_p"] >= inicio_mes]

        st.markdown(
            kpi_grid(
                kpi_html("Hoje",    fmt_brl(df_hoje["Valor(R$)"].sum()), f"{len(df_hoje)} entregas", "green"),
                kpi_html("Semana",  fmt_brl(df_sem["Valor(R$)"].sum()),  f"{len(df_sem)} entregas",  "accent"),
                kpi_html("Mês",     fmt_brl(df_mes["Valor(R$)"].sum()),  f"{len(df_mes)} entregas",  "amber"),
            ),
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # Gráfico de pizza — por loja
        with st.expander("📊 Faturamento por Estabelecimento", expanded=True):
            periodo = st.selectbox(
                "Período:",
                ["Tudo", "Hoje", "Esta Semana", "Este Mês"],
                key="filtro_periodo_painel",
            )
            mapa_periodo = {"Hoje": df_hoje, "Esta Semana": df_sem, "Este Mês": df_mes, "Tudo": df4}
            df_fil = mapa_periodo[periodo]

            if not df_fil.empty:
                df_agr = df_fil.groupby("Estabelecimento")["Valor(R$)"].sum().reset_index()
                fig_pie = px.pie(
                    df_agr,
                    names="Estabelecimento",
                    values="Valor(R$)",
                    template="plotly_dark",
                    hole=0.4,
                    title=f"Por Loja — {periodo}",
                )
                fig_pie.update_layout(LAYOUT)
                fig_pie.update_traces(textinfo="percent+value", textposition="inside")
                st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
            else:
                st.warning(f"Sem registros para: {periodo}.")

        # Gráfico de barras — por bairro
        with st.expander("📈 Faturamento por Bairro (histórico)", expanded=False):
            df_bairro = (
                df4.groupby("Bairro")["Valor(R$)"]
                .sum()
                .reset_index()
                .sort_values("Valor(R$)", ascending=False)
            )
            fig_bar = px.bar(
                df_bairro,
                x="Bairro",
                y="Valor(R$)",
                template="plotly_dark",
                text_auto=".2f",
            )
            layout_b = {**LAYOUT, "xaxis": {**LAYOUT["xaxis"], "tickangle": -45}}
            fig_bar.update_layout(layout_b)
            fig_bar.update_traces(marker_color=C_ACCENT, textposition="outside")
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})


# ── ABA 5: STAFF (somente admin) ─────────────────────────────────────────────
if is_admin():
    with abas[5]:
        st.markdown(
            '<div class="sec-eyebrow">Configurações</div>'
            '<div class="sec-title">Membros do Sistema</div>',
            unsafe_allow_html=True,
        )

        novo_nome_u = st.text_input("Nome Completo", key="txt_nome_user")
        novo_user   = st.text_input("Login (username)", key="txt_login")
        nova_senha  = st.text_input("Senha", type="password", key="txt_senha")
        perfil_sel  = st.selectbox("Perfil", ["entregador", "admin"], key="sel_perfil")

        if st.button("Salvar Membro", use_container_width=True, key="btn_cad_user"):
            if novo_nome_u.strip() and novo_user.strip() and nova_senha.strip():
                try:
                    database.cadastrar_usuario(
                        username=novo_user, nome=novo_nome_u,
                        senha=nova_senha, perfil=perfil_sel,
                    )
                    st.success(f"Membro @{novo_user.strip()} cadastrado!")
                    st.rerun()
                except Exception:
                    st.error("Erro: esse username já existe.")
            else:
                st.warning("Preencha todos os campos.")

        st.markdown("<br>", unsafe_allow_html=True)

        for u in database.listar_usuarios():
            b_cls = "badge-admin" if u["perfil"] == "admin" else "badge-entregador"
            col_r, col_d = st.columns([6, 1])
            col_r.markdown(
                f"<div style='padding:8px 0;border-bottom:1px solid {C_BORDER};font-size:0.85rem;'>"
                f"<b>{u['nome']}</b> <span class='perfil-badge {b_cls}'>{u['perfil']}</span><br>"
                f"<span style='color:{C_MUTED};'>@{u['username']}</span></div>",
                unsafe_allow_html=True,
            )
            with col_d:
                if u["username"] != username_atual():
                    st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
                    if st.button("✕", key=f"del_user_{u['id']}", use_container_width=True):
                        database.deletar_usuario(u["id"])
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
