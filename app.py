import streamlit as st
from datetime import timedelta
from zoneinfo import ZoneInfo
import db_manager as database
import pandas as pd
import plotly.express as px
from streamlit_cookies_controller import CookieController

# ─── Setup ───────────────────────────────────────────────────────────────────
database.criar_tabela()

st.set_page_config(page_title="Velox — Entregas", layout="wide")

# Fuso horário (UTC-3, sem horário de verão)
TZ_BR = ZoneInfo("America/Fortaleza")

def hoje_br():
    """Data atual no fuso configurado — corrige o bug do servidor UTC."""
    from datetime import datetime
    return datetime.now(TZ_BR).date()

# ─── Cores ───────────────────────────────────────────────────────────────────
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

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap');

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

.stTextInput input,
.stNumberInput input,
.stSelectbox > div > div,
.stTextArea textarea {{
    background: {C_SURFACE} !important;
    border: 1px solid {C_BORDER} !important;
    color: {C_TEXT} !important;
    border-radius: 8px !important;
    font-size: 1rem !important;
    min-height: 44px !important;
}}

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
    white-space: nowrap;
}}
.status-pago    {{ color: {C_GREEN}; font-size: 0.68rem; font-weight: 600; }}
.status-pendente{{ color: {C_AMBER}; font-size: 0.68rem; font-weight: 600; }}

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
.badge-admin      {{ background: rgba(47,129,247,.15); color: {C_ACCENT}; border: 1px solid {C_ACCENT}; }}
.badge-entregador {{ background: rgba(63,185,80,.12);  color: {C_GREEN};  border: 1px solid {C_GREEN};  }}

.streamlit-expanderHeader {{ font-weight: 600 !important; font-size: 0.9rem !important; }}
</style>
""", unsafe_allow_html=True)

# ─── Plotly base ──────────────────────────────────────────────────────────────
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
    return f"""<div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="{cls}">{value}</div>
        {sub_html}
    </div>"""

def kpi_grid(*cards: str) -> str:
    return f'<div class="kpi-grid">{"".join(cards)}</div>'

def parse_data_robusta(serie: pd.Series) -> pd.Series:
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        parsed = pd.to_datetime(serie, format=fmt, errors="coerce")
        if parsed.notna().sum() > parsed.isna().sum():
            return parsed.dt.date
    return pd.to_datetime(serie, infer_datetime_format=True, errors="coerce").dt.date


# ════════════════════════════════════════════════════════════════════════════
# COOKIE CONTROLLER
# ════════════════════════════════════════════════════════════════════════════
if "cookie_controller" not in st.session_state:
    st.session_state["cookie_controller"] = CookieController()

controller: CookieController = st.session_state["cookie_controller"]

if "usuario" not in st.session_state:
    cookie_username = controller.get("velox_username")
    if cookie_username:
        usuario_salvo = database.obter_usuario_por_username(cookie_username)
        if usuario_salvo:
            st.session_state["usuario"]  = usuario_salvo["nome"]
            st.session_state["username"] = usuario_salvo["username"]
            st.session_state["perfil"]   = usuario_salvo["perfil"]


# ════════════════════════════════════════════════════════════════════════════
# LOGIN
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
            f"<div style='font-size:1.1rem;font-weight:700;color:{C_TEXT};margin-bottom:4px;'>"
            f"Acessar conta</div>"
            f"<div style='font-size:0.78rem;color:{C_MUTED};margin-bottom:20px;'>"
            f"Controle de entregas · Sobral CE</div>",
            unsafe_allow_html=True,
        )
        u_input = st.text_input("Usuário", placeholder="seu_usuario", key="li_user")
        p_input = st.text_input("Senha", type="password", placeholder="••••••••", key="li_pass")
        lembrar = st.checkbox("Manter conectado neste dispositivo", value=True)
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

    st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
    if st.button("Sair da conta", use_container_width=True, key="btn_sair"):
        for k in ["usuario", "username", "perfil"]:
            st.session_state.pop(k, None)
        controller.remove("velox_username")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("Zona de perigo"):
        st.markdown(
            f"<p style='font-size:0.78rem;color:{C_MUTED};'>"
            f"Apaga permanentemente todas as suas entregas. Irreversível.</p>",
            unsafe_allow_html=True,
        )
        st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
        if st.button("Apagar todas as minhas entregas", use_container_width=True, key="btn_reset"):
            database.deletar_todas_entregas_usuario(username_atual())
            st.success("Histórico apagado.")
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
titulos_abas = ["Novo", "Entregas", "Pendentes", "Lojas", "Painel"]
if is_admin():
    titulos_abas.append("Equipe")

abas = st.tabs(titulos_abas)


# ── ABA 0: NOVA ENTREGA ──────────────────────────────────────────────────────
with abas[0]:
    st.markdown(
        '<div class="sec-eyebrow">Registrar</div>'
        '<div class="sec-title">Nova Entrega</div>',
        unsafe_allow_html=True,
    )

    bairros_opcoes = ["Selecionar bairro..."] + BAIRROS_SOBRAL + ["Outro"]
    bairro_sel = st.selectbox("Bairro", bairros_opcoes, key="sel_bairro")
    if bairro_sel == "Outro":
        bairro = st.text_input("Nome do bairro", placeholder="Digite o bairro", key="txt_bairro")
    elif bairro_sel == "Selecionar bairro...":
        bairro = ""
    else:
        bairro = bairro_sel

    estabs = database.listar_estabelecimentos()
    nomes_estabs = [e[1] for e in estabs]
    opcoes_estab = ["Selecionar estabelecimento..."] + nomes_estabs + ["Outro"]
    estab_sel = st.selectbox("Estabelecimento", opcoes_estab, key="sel_estab")
    if estab_sel == "Outro":
        estabelecimento = st.text_input("Nome do estabelecimento", placeholder="Digite o nome", key="txt_estab")
    elif estab_sel == "Selecionar estabelecimento...":
        estabelecimento = ""
    else:
        estabelecimento = estab_sel

    valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f", step=0.50)
    status_pagamento = st.selectbox("Status do pagamento", ["Pendente", "Pago"])
    
    # Campo de data adicionado para permitir corrigir entregas feitas em dias anteriores!
    data_entrega = st.date_input("Data da entrega", value=hoje_br())

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Registrar entrega", use_container_width=True, key="btn_reg"):
        if not bairro.strip() or not estabelecimento.strip():
            st.warning("Preencha todos os campos antes de registrar.")
        elif valor <= 0:
            st.warning("Informe um valor maior que R$ 0,00.")
        else:
            # Salva com a data escolhida no input
            database.cadastrar_entregas(
                bairro.strip(), valor, status_pagamento,
                estabelecimento.strip(), str(data_entrega), username_atual()
            )
            st.success("Entrega registrada.")


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

        total_pagas  = int(df["Status"].value_counts().get("Pago", 0))
        total_pend   = int(df["Status"].value_counts().get("Pendente", 0))
        receita_conf = df[df["Status"] == "Pago"]["Valor(R$)"].sum()

        st.markdown(
            kpi_grid(
                kpi_html("Total de Entregas", str(len(df)), f"{total_pagas} pagas · {total_pend} pendentes"),
                kpi_html("Receita Confirmada", fmt_brl(receita_conf), "somente pagas", "green"),
            ),
            unsafe_allow_html=True,
        )

        busca = st.text_input("Buscar por bairro ou estabelecimento", key="busca_hist")

        df_view = df.copy()
        if busca:
            mask = (
                df_view["Bairro"].str.contains(busca, case=False, na=False)
                | df_view["Estabelecimento"].str.contains(busca, case=False, na=False)
            )
            df_view = df_view[mask]

        st.markdown("<br>", unsafe_allow_html=True)

        for _, row in df_view.iterrows():
            s_cls = "status-pago" if row["Status"] == "Pago" else "status-pendente"
            s_txt = "Pago" if row["Status"] == "Pago" else "Pendente"
            v_cor = C_GREEN if row["Status"] == "Pago" else C_AMBER
            col_card, col_del = st.columns([6, 1])
            with col_card:
                st.markdown(
                    f"""<div class="entrega-card">
                        <div class="entrega-info">
                            <div class="entrega-loja">{row['Estabelecimento']}</div>
                            <div class="entrega-meta">{row['Bairro']} &middot; {row['Data']} &middot;
                                <span class="{s_cls}">{s_txt}</span></div>
                        </div>
                        <div class="entrega-valor" style="color:{v_cor};">{fmt_brl(row['Valor(R$)'])}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
            with col_del:
                st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
                if st.button("Excluir", key=f"del_entrega_{int(row['ID'])}", use_container_width=True):
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
            st.success("Sem pendências. Tudo recebido.")
        else:
            st.markdown(
                kpi_html(
                    "Total em Aberto",
                    fmt_brl(df_pend["Valor(R$)"].sum()),
                    f"{len(df_pend)} taxa(s) pendente(s)",
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
                            <div class="entrega-meta">{row['Bairro']} &middot; {row['Data']}</div>
                        </div>
                        <div class="entrega-valor" style="color:{C_AMBER};">{fmt_brl(row['Valor(R$)'])}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
                st.markdown('<div class="btn-success">', unsafe_allow_html=True)
                if st.button("Confirmar recebimento", key=f"pagar_{int(row['ID'])}", use_container_width=True):
                    database.atualizar_status(int(row["ID"]), "Pago")
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


# ── ABA 3: ESTABELECIMENTOS ───────────────────────────────────────────────────
with abas[3]:
    st.markdown(
        '<div class="sec-eyebrow">Lojas</div>'
        '<div class="sec-title">Estabelecimentos</div>',
        unsafe_allow_html=True,
    )

    sub1, sub2 = st.tabs(["Cadastro individual", "Importar em massa"])

    with sub1:
        novo_nome = st.text_input("Nome do estabelecimento", placeholder="Ex: Burguer Central", key="nome_loja_ind")
        if st.button("Cadastrar", use_container_width=True, key="btn_cad_loja"):
            nome_limpo = novo_nome.strip()
            if nome_limpo:
                inserido = database.cadastrar_estabelecimento(nome_limpo)
                if inserido:
                    st.success(f"'{nome_limpo}' cadastrado.")
                    st.rerun()
                else:
                    st.warning(f"'{nome_limpo}' já existe na lista.")
            else:
                st.warning("Digite um nome válido.")

    with sub2:
        st.markdown(
            f"<span style='font-size:0.82rem;color:{C_MUTED};'>"
            "Cole os nomes — um por linha ou separados por vírgula.</span>",
            unsafe_allow_html=True,
        )
        texto_massa = st.text_area(
            "Lista de estabelecimentos",
            placeholder="Loja A\nLoja B\nLoja C, Loja D",
            height=140,
            key="txt_massa",
        )
        if st.button("Cadastrar lista", use_container_width=True, key="btn_massa"):
            if texto_massa.strip():
                lojas = list({
                    parte.strip()
                    for linha in texto_massa.split("\n")
                    for parte in linha.split(",")
                    if parte.strip()
                })
                contagem  = sum(database.cadastrar_estabelecimento(l) for l in lojas)
                ignorados = len(lojas) - contagem
                msg = f"{contagem} estabelecimento(s) adicionado(s)."
                if ignorados:
                    msg += f" {ignorados} já existiam e foram ignorados."
                st.success(msg)
                if contagem:
                    st.rerun()
            else:
                st.warning("O campo está vazio.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f'<div style="font-size:0.85rem;font-weight:600;color:{C_TEXT};margin-bottom:10px;">'
        f'Cadastrados</div>',
        unsafe_allow_html=True,
    )

    estabs_lista = database.listar_estabelecimentos()
    if not estabs_lista:
        st.info("Nenhum estabelecimento cadastrado.")
    else:
        for e_id, e_nome in estabs_lista:
            col_nome, col_del = st.columns([6, 1])
            col_nome.markdown(
