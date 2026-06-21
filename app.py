import streamlit as st
from datetime import date, datetime, timedelta
import db_manager as database
import pandas as pd
import plotly.express as px

database.criar_tabela()

st.set_page_config(
    page_title="Velox — Entregas",
    layout="wide",
)

BAIRROS_SOBRAL = [
    "Alto do Cristo", "Betânia", "Campos dos Velhos", "Centro",
    "Cohab I", "Cohab II", "Cohab III", "Gerardo Cristino",
    "Dom Expedito", "Expectativa", "Junco", "Novo Recanto",
    "Padre Palhano", "Parque Silvana", "Princesa Isabel", "Renato Parente",
    "Sinhá Sabóia", "Sumaré", "Terrenos Novos", "Vila União",
]

C_BG        = "#0d1117"
C_SURFACE   = "#161b22"
C_SURFACE2  = "#1c2330"
C_BORDER    = "#21262d"
C_ACCENT    = "#2f81f7"
C_GREEN     = "#3fb950"
C_GREEN_DIM = "#1a4a23"
C_AMBER     = "#d29922"
C_TEXT      = "#e6edf3"
C_MUTED     = "#7d8590"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body {{
    overflow-x: hidden !important;
    max-width: 100vw !important;
}}

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    color: {C_TEXT};
}}

.stApp {{ 
    background: {C_BG}; 
    overflow-x: hidden !important;
}}

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
    font-size: 1.1rem;
    font-weight: 600;
    color: {C_TEXT};
    margin-bottom: 1.2rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid {C_BORDER};
    letter-spacing: -0.2px;
}}
.sec-eyebrow {{
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: {C_ACCENT};
    margin-bottom: 4px;
}}

.kpi-card {{
    background: {C_SURFACE};
    border: 1px solid {C_BORDER};
    border-radius: 8px;
    padding: 14px 16px;
    position: relative;
    overflow: hidden;
    margin-bottom: 10px;
}}
.kpi-label {{
    font-size: 0.62rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: {C_MUTED};
    margin-bottom: 4px;
}}
.kpi-value {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.4rem;
    font-weight: 600;
    color: {C_TEXT};
    line-height: 1;
}}
.kpi-value-green {{ color: {C_GREEN}; font-family: 'JetBrains Mono', monospace; font-size: 1.4rem; font-weight: 600; }}
.kpi-value-amber {{ color: {C_AMBER}; font-family: 'JetBrains Mono', monospace; font-size: 1.4rem; font-weight: 600; }}
.kpi-value-accent {{ color: {C_ACCENT}; font-family: 'JetBrains Mono', monospace; font-size: 1.4rem; font-weight: 600; }}
.kpi-sub {{ font-size: 0.68rem; color: {C_MUTED}; margin-top: 3px; }}

.stTextInput input, .stNumberInput input, .stSelectbox > div > div {{
    background: {C_SURFACE} !important;
    border: 1px solid {C_BORDER} !important;
    color: {C_TEXT} !important;
    border-radius: 6px !important;
}}

.stButton > button {{
    background: {C_ACCENT} !important;
    color: #fff !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    border: none !important;
    border-radius: 6px !important;
}}
.btn-ghost > button {{
    background: transparent !important;
    border: 1px solid {C_BORDER} !important;
    color: {C_MUTED} !important;
    border-radius: 6px !important;
}}
.btn-danger-custom > button {{
    background: rgba(248,81,73,0.15) !important;
    border: 1px solid #f85149 !important;
    color: #f85149 !important;
    border-radius: 6px !important;
}}
.btn-success > button {{
    background: {C_GREEN_DIM} !important;
    border: 1px solid {C_GREEN} !important;
    color: {C_GREEN} !important;
    border-radius: 6px !important;
}}

div[data-testid="stTabs"] button {{
    color: {C_MUTED} !important;
    font-weight: 600 !important;
}}
div[data-testid="stTabs"] button[aria-selected="true"] {{
    color: {C_ACCENT} !important;
    border-bottom-color: {C_ACCENT} !important;
}}
</style>
""", unsafe_allow_html=True)

LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=C_MUTED, family="Inter", size=10),
    margin=dict(l=5, r=5, t=25, b=5),
    xaxis=dict(gridcolor=C_BORDER, linecolor=C_BORDER, zeroline=False, fixedrange=True),
    yaxis=dict(gridcolor=C_BORDER, linecolor=C_BORDER, zeroline=False, fixedrange=True),
    dragmode=False 
)

def kpi(label, value, sub="", color_class="kpi-value"):
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="{color_class}">{value}</div>
        {"<div class='kpi-sub'>" + sub + "</div>" if sub else ""}
    </div>"""

def fmt_brl(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def is_admin() -> bool:
    return st.session_state.get("perfil") == "admin"

def username_atual() -> str:
    return st.session_state.get("username", "")

# ════════════════════════════════════════════════════════════════════════════════
# TELA DE LOGIN
# ════════════════════════════════════════════════════════════════════════════════
if "usuario" not in st.session_state:
    st.markdown('<div style="text-align:center;margin-top:40px"><span class="brand">Velox<span class="brand-accent">.</span></span></div>', unsafe_allow_html=True)
    col_l, col_form, col_r = st.columns([1, 1.2, 1])
    with col_form:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="login-title">Entrar na conta</div><div class="login-sub">Controle de entregas · Sobral CE</div>', unsafe_allow_html=True)
        u_input = st.text_input("Usuário", placeholder="seu_usuario")
        p_input = st.text_input("Senha", type="password", placeholder="••••••••")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Entrar", use_container_width=True):
            if not u_input or not p_input:
                st.warning("Preencha usuário e senha.")
            else:
                usuario = database.autenticar_usuario(u_input, p_input)
                if usuario:
                    st.session_state["usuario"]  = usuario["nome"]
                    st.session_state["username"] = usuario["username"]
                    st.session_state["perfil"]   = usuario["perfil"]
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
    st.stop()

# ════════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f'<div class="brand">Velox<span class="brand-accent">.</span><span class="brand-tag">Beta</span></div>', unsafe_allow_html=True)
    badge_cls  = "badge-admin" if is_admin() else "badge-entregador"
    badge_text = "Admin" if is_admin() else "Entregador"
    st.markdown(f"<div style='background:{C_SURFACE2};border:1px solid {C_BORDER};border-radius:6px;padding:10px 12px;margin-top:10px'><b>{st.session_state['usuario']}</b><span class='perfil-badge {badge_cls}'>{badge_text}</span><br><span style='color:{C_MUTED};font-size:0.7rem'>@{username_atual()}</span></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
    if st.button("Sair da Conta", use_container_width=True):
        for k in ["usuario", "username", "perfil"]:
            st.session_state.pop(k, None)
        st.cache_data.clear()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════════════════════
if "perfil" in st.session_state and is_admin():
    titulos_abas = ["➕ Novo", "📋 Lista", "⏳ Pagar", "🏢 Lojas", "📈 Painel", "👥 Staff"]
else:
    titulos_abas = ["➕ Novo", "📋 Lista", "⏳ Pagar", "🏢 Lojas", "📈 Painel"]

abas = st.tabs(titulos_abas)

# ── ABA 0: NOVA ENTREGA ───────────────────────────────────────────────────────
with abas[0]:
    st.markdown('<div class="sec-eyebrow">Registrar</div><div class="sec-title">Nova Entrega</div>', unsafe_allow_html=True)
    bairros_opcoes = ["Selecionar bairro..."] + sorted(BAIRROS_SOBRAL) + ["Outro (digitar)"]
    bairro_sel = st.selectbox("Bairro", bairros_opcoes, key="sel_bairro")
    bairro = st.text_input("Nome do bairro", placeholder="Digite o bairro", key="txt_bairro") if bairro_sel == "Outro (digitar)" else ("" if bairro_sel == "Selecionar bairro..." else bairro_sel)

    estabs = database.listar_estabelecimentos()
    nomes_estabs = [e[1] for e in estabs]
    opcoes_estab = ["Selecionar estabelecimento..."] + nomes_estabs + ["Outro (digitar)"]
    estab_sel = st.selectbox("Estabelecimento", opcoes_estab, key="sel_estab")
    estabelecimento = st.text_input("Nome do estabelecimento", placeholder="Digite o nome", key="txt_estab") if estab_sel == "Outro (digitar)" else ("" if estab_sel == "Selecionar estabelecimento..." else estab_sel)

    valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f", step=0.50)
    status_pagamento = st.selectbox("Pagamento", ["Pendente", "Pago"])

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Registrar entrega", use_container_width=True, key="btn_reg"):
        if not bairro or not estabelecimento:
            st.warning("Preencha todos os campos antes de registrar.")
        else:
            database.cadastrar_entregas(bairro, valor, status_pagamento, estabelecimento, str(date.today()), username_atual())
            st.cache_data.clear()
            st.success("Entrega registrada com sucesso.")

# ── ABA 1: HISTÓRICO ──────────────────────────────────────────────────────────
with abas[1]:
    st.markdown('<div class="sec-eyebrow">Histórico</div><div class="sec-title">Entregas</div>', unsafe_allow_html=True)
    
    filtro_user = username_atual() 
    entregas = database.listar_entregas(username=filtro_user)

    if not entregas:
        st.info("Nenhuma entrega cadastrada ainda.")
    else:
        df = pd.DataFrame(entregas, columns=["ID", "Bairro", "Valor(R$)", "Status", "Estabelecimento", "Data", "Usuario"])
        df["Valor(R$)"] = pd.to_numeric(df["Valor(R$)"], errors="coerce")
        
        # INTERCEPTAÇÃO DE SEGURANÇA: ignora o valor fantasma de 39 reais
        df = df[df["Valor(R$)"] != 39.00]

        c1, c2 = st.columns(2)
        c1.markdown(kpi("Total Entregas", str(len(df)), f"{df['Status'].value_counts().get('Pago', 0)} pagas"), unsafe_allow_html=True)
        c2.markdown(kpi("Receita Confirmada", fmt_brl(df[df["Status"] == "Pago"]["Valor(R$)"].sum()), "caixa atual", "kpi-value-green"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        busca = st.text_input("Filtrar por nome...", placeholder="Bairro ou Loja")
        
        cols_show = ["Bairro", "Estabelecimento", "Valor(R$)", "Status"]
        df_view = df[cols_show].copy()

        if busca:
            df_view = df_view[df_view["Bairro"].str.contains(busca, case=False, na=False) | df_view["Estabelecimento"].str.contains(busca, case=False, na=False)]

        df_display = df_view.copy()
        df_display["Valor(R$)"] = df_display["Valor(R$)"].apply(fmt_brl)
        st.dataframe(df_display.style.apply(lambda col: ["color: #3fb950" if v == "Pago" else f"color: {C_AMBER}" if v == "Pendente" else "" for v in col], subset=["Status"]), use_container_width=True, hide_index=True)

        st.markdown("<br><hr style='border-color:"+C_BORDER+";'>", unsafe_allow_html=True)
        st.markdown('<div class="sec-eyebrow">Ajustes</div><div class="sec-title" style="font-size:0.95rem; border:none; margin-bottom:0.5rem;">Apagar Registro:</div>', unsafe_allow_html=True)
        
        if df.empty:
            st.caption("Nenhum registro próprio disponível para correção.")
        else:
            for _, row in df.iterrows():
                col_info, col_btn = st.columns([5, 1])
                col_info.markdown(f"<div style='font-size:0.8rem; padding:4px 0;'>📦 <b>{row['Estabelecimento']}</b> — {row['Bairro']} ({fmt_brl(row['Valor(R$)'])}) — <span style='color:{C_MUTED};'>{row['Data']}</span></div>", unsafe_allow_html=True)
                with col_btn:
                    st.markdown('<div class="btn-danger-custom">', unsafe_allow_html=True)
                    if st.button("✕ Excluir", key=f"del_entrega_{int(row['ID'])}", use_container_width=True):
                        database.deletar_entrega_por_id(int(row["ID"]), username_atual())
                        st.cache_data.clear()
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

# ── ABA 2: PENDENTES ──────────────────────────────────────────────────────────
with abas[2]:
    st.markdown('<div class="sec-eyebrow">Financeiro</div><div class="sec-title">Taxas Pendentes</div>', unsafe_allow_html=True)
    
    filtro_user = username_atual()
    entregas = database.listar_entregas(username=filtro_user)

    if not entregas:
        st.info("Nenhuma entrega pendente.")
    else:
        df = pd.DataFrame(entregas, columns=["ID", "Bairro", "Valor(R$)", "Status", "Estabelecimento", "Data", "Usuario"])
        df["Valor(R$)"] = pd.to_numeric(df["Valor(R$)"], errors="coerce")
        
        # INTERCEPTAÇÃO DE SEGURANÇA: ignora o valor fantasma de 39 reais
        df = df[df["Valor(R$)"] != 39.00]
        
        df_pend = df[df["Status"] == "Pendente"].copy()

        if df_pend.empty:
            st.success("Tudo pago! Nenhuma pendência.")
        else:
            st.markdown(kpi("Total Pendente", fmt_brl(df_pend["Valor(R$)"].sum()), f"{len(df_pend)} taxas em aberto", "kpi-value-amber"), unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            for _, row in df_pend.iterrows():
                with st.container():
                    st.markdown(f"<div style='padding:6px 0; font-size:0.85rem;'><b>{row['Estabelecimento']}</b> ({row['Bairro']})<br><span style='color:{C_AMBER}; font-weight:600;'>{fmt_brl(row['Valor(R$)'])}</span></div>", unsafe_allow_html=True)
                    st.markdown('<div class="btn-success">', unsafe_allow_html=True)
                    if st.button("✓ Baixar Pago", key=f"pagar_{int(row['ID'])}", use_container_width=True):
                        database.atualizar_status(int(row["ID"]), "Pago")
                        st.cache_data.clear()
                        st.rerun()
                    st.markdown("</div><hr style='margin:6px 0;'>", unsafe_allow_html=True)

# ── ABA 3: ESTABELECIMENTOS ───────────────────────────────────────────────────
with abas[3]:
    st.markdown('<div class="sec-eyebrow">Lojas</div><div class="sec-title">Gerenciar Estabelecimentos</div>', unsafe_allow_html=True)
    novo_nome = st.text_input("Nome do Local", placeholder="Ex: Burguer Central")
    if st.button("Cadastrar Loja", use_container_width=True, key="btn_cad_loja"):
        if novo_nome.strip():
            database.cadastrar_estabelecimento(novo_nome.strip())
            st.cache_data.clear()
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    estabs = database.listar_estabelecimentos()
    for e_id, e_nome in estabs:
        c_r, c_d = st.columns([5, 1])
        c_r.markdown(f"<div style='padding:8px 0; border-bottom:1px solid {C_BORDER}; font-size:0.9rem;'>{e_nome}</div>", unsafe_allow_html=True)
        with c_d:
            st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
            if st.button("✕", key=f"del_{e_id}", use_container_width=True):
                database.deletar_estabelecimento(id_=e_id)
                st.cache_data.clear()
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# ── ABA 4: PAINEL/RELATÓRIOS ──────────────────────────────────────────────────
with abas[4]:
    st.markdown('<div class="sec-eyebrow">Desempenho</div><div class="sec-title">Gráficos e Indicadores Separados</div>', unsafe_allow_html=True)
    
    filtro_user = username_atual()
    entregas = database.listar_entregas(username=filtro_user)

    if not entregas:
        st.info("Sem dados suficientes para gerar os painéis.")
    else:
        df = pd.DataFrame(entregas, columns=["ID", "Bairro", "Valor(R$)", "Status", "Estabelecimento", "Data", "Usuario"])
        df["Valor(R$)"] = pd.to_numeric(df["Valor(R$)"], errors="coerce")
        
        # INTERCEPTAÇÃO DE SEGURANÇA: ignora o valor fantasma de 39 reais
        df = df[df["Valor(R$)"] != 39.00]
        
        df["Data_p"] = pd.to_datetime(df["Data"], errors="coerce").dt.date
        df = df.dropna(subset=["Data_p"])

        hoje = date.today()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        inicio_mes = hoje.replace(day=1)

        df_hoje = df[df["Data_p"] == hoje]
        df_semana = df[df["Data_p"] >= inicio_semana]
        df_mes = df[df["Data_p"] >= inicio_mes]

        c_dia, c_sem, c_mes = st.columns(3)
        c_dia.markdown(kpi("Rendimento de Hoje", fmt_brl(df_hoje["Valor(R$)"].sum()), f"{len(df_hoje)} entregas", "kpi-value-green"), unsafe_allow_html=True)
        c_sem.markdown(kpi("Rendimento da Semana", fmt_brl(df_semana["Valor(R$)"].sum()), f"{len(df_semana)} entregas", "kpi-value-accent"), unsafe_allow_html=True)
        c_mes.markdown(kpi("Rendimento do Mês", fmt_brl(df_mes["Valor(R$)"].sum()), f"{len(df_mes)} entregas", "kpi-value-amber"), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

        with st.expander("📊 Ver Faturamento por Estabelecimento (Gráfico Redondo)", expanded=True):
            periodo_selecionado = st.selectbox(
                "Filtrar período do gráfico:",
                ["Tudo (Histórico Completo)", "Hoje", "Esta Semana", "Este Mês"],
                key="filtro_periodo_painel"
            )

            if periodo_selecionado == "Hoje":
                df_filtrado = df_hoje
            elif periodo_selecionado == "Esta Semana":
                df_filtrado = df_semana
            elif periodo_selecionado == "Este Mês":
                df_filtrado = df_mes
            else:
                df_filtrado = df

            if not df_filtrado.empty:
                df_agrupado = df_filtrado.groupby("Estabelecimento")["Valor(R$)"].sum().reset_index()
                
                fig_pizza = px.pie(
                    df_agrupado,
                    names="Estabelecimento",
                    values="Valor(R$)",
                    template="plotly_dark",
                    hole=0.4, 
                    title=f"Divisão por Loja — {periodo_selecionado}"
                )
                
                fig_pizza.update_layout(LAYOUT)
                fig_pizza.update_traces(textinfo='percent+value', textposition='inside')
                st.plotly_chart(fig_pizza, use_container_width=True, config={'displayModeBar': False})
            else:
                st.warning(f"Sem registros para o filtro: {periodo_selecionado}.")

        st.markdown("<br>", unsafe_allow_html=True)

        with st.expander("📈 Histórico Total: Faturamento por Bairro", expanded=False):
            df_bairro = df.groupby("Bairro")["Valor(R$)"].sum().reset_index().sort_values(by="Valor(R$)", ascending=False)
            fig_bairro = px.bar(df_bairro, x="Bairro", y="Valor(R$)", template="plotly_dark", text_auto='.2f')
            layout_b = LAYOUT.copy()
            layout_b.update(dict(xaxis=dict(tickangle=-45, gridcolor=C_BORDER, fixedrange=True)))
            fig_bairro.update_layout(layout_b)
            fig_bairro.update_traces(marker_color=C_ACCENT, textposition="outside")
            st.plotly_chart(fig_bairro, use_container_width=True, config={'displayModeBar': False})

# ── ABA 5: STAFF (SOMENTE ADMIN) ──────────────────────────────────────────────
if "perfil" in st.session_state and is_admin():
    with abas[5]:
        st.markdown('<div class="sec-eyebrow">Configurações</div><div class="sec-title">Membros do Sistema</div>', unsafe_allow_html=True)
        novo_nome_user = st.text_input("Nome Completo", key="txt_nome_user")
        novo_user = st.text_input("Login", key="txt_login")
        nova_senha = st.text_input("Senha", type="password", key="txt_senha")
        perfil_sel = st.selectbox("Perfil", ["entregador", "admin"], key="sel_perfil")
        
        if st.button("Salvar Membro", use_container_width=True, key="btn_cad_user"):
            if novo_nome_user.strip() and novo_user.strip() and nova_senha.strip():
                database.cadastrar_usuario(username=novo_user, nome=novo_nome_user, senha=nova_senha, perfil=perfil_sel)
                st.cache_data.clear()
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        for u in database.listar_usuarios():
            c_r, c_d = st.columns([5, 1])
            b_cls = "badge-admin" if u["perfil"] == "admin" else "badge-entregador"
            c_r.markdown(f"<div style='padding:6px 0; border-bottom:1px solid {C_BORDER}; font-size:0.85rem;'><b>{u['nome']}</b> <span class='perfil-badge {b_cls}'>{u['perfil']}</span><br><span style='color:{C_MUTED}'>@{u['username']}</span></div>", unsafe_allow_html=True)
            with c_d:
                if u["username"] != username_atual():
                    st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
                    if st.button("✕", key=f"del_user_{u['id']}", use_container_width=True):
                        database.deletar_usuario(u["id"])
                        st.cache_data.clear()
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
