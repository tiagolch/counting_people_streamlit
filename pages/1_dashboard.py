import pandas as pd
import psycopg2
import streamlit as st

# --- Configuração da Página com Sidebar Fechada por Padrão ---
st.set_page_config(
    page_title="Dashboard - Hillsong Aveiro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",  # <-- Define a barra lateral iniciada fechada
)

# --- Estilização CSS alinhada ao tema principal ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght=300;400;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #111111;
        color: #FFFFFF;
        font-family: 'Inter', sans-serif;
    }
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 32px !important;
        font-weight: 700 !important;
        color: #FFD700 !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #AAAAAA !important;
        letter-spacing: 1px;
    }
    .stMultiSelect, .stDateInput, .stSelectbox {
        background-color: #1E1E1E !important;
        border-radius: 8px;
    }
    div[data-testid="stTable"] {
        background-color: #1A1A1A;
        border-radius: 8px;
    }
    hr {
        border-color: #222222 !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    "<p style='color: #888888; font-size: 14px; letter-spacing: 2px; margin-bottom: 0;'>HILLSONG CHURCH PORTUGAL - AVEIRO</p>",
    unsafe_allow_html=True,
)
st.title("📊 Painel de Métricas & Relatórios")
st.markdown("---")


# --- Leitura dos dados do Supabase ---
@st.cache_data(ttl=60)
def carregar_dados():
    try:
        db_url = st.secrets["postgres"]["url"]
        conn = psycopg2.connect(db_url)
        query = """
            SELECT 
                id,
                data_hora,
                responsavel,
                posicao,
                horario,
                adultos,
                criancas,
                total_geral,
                visitantes,
                conversoes
            FROM contagens_reuniao
            ORDER BY data_hora DESC;
        """
        df = pd.read_sql(query, conn)
        conn.close()

        if not df.empty:
            df["data_hora"] = pd.to_datetime(df["data_hora"])
            df["data"] = df["data_hora"].dt.date
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados do banco: {e}")
        return pd.DataFrame()


df_bruto = carregar_dados()

if df_bruto.empty:
    st.info(
        "Nenhum registro encontrado na base de dados para gerar o dashboard."
    )
    if st.button("🔄 Atualizar"):
        st.cache_data.clear()
        st.rerun()
    st.stop()

# --- Barra Lateral de Filtros ---
st.sidebar.header("🔍 Filtros de Consulta")

# Filtro de Data (Obrigatório)
datas_disponiveis = sorted(df_bruto["data"].unique(), reverse=True)
data_inicio, data_fim = st.sidebar.date_input(
    "Período:",
    value=(min(datas_disponiveis), max(datas_disponiveis)),
    min_value=min(datas_disponiveis),
    max_value=max(datas_disponiveis),
)

# Filtro de Horário (Opcional - vazio busca todos)
horarios = st.sidebar.multiselect(
    "Horários das Reuniões:",
    options=sorted(df_bruto["horario"].dropna().unique()),
    default=[],
    placeholder="Todos os horários",
)

# Filtro de Responsável (Opcional - vazio busca todos)
responsaveis = st.sidebar.multiselect(
    "Responsável:",
    options=sorted(df_bruto["responsavel"].dropna().unique()),
    default=[],
    placeholder="Todos os responsáveis",
)

if st.sidebar.button("🔄 Recarregar Dados"):
    st.cache_data.clear()
    st.rerun()

# --- Aplicação Inteligente dos Filtros ---
mask_data = (df_bruto["data"] >= data_inicio) & (
    df_bruto["data"] <= data_fim
)
mask_horario = df_bruto["horario"].isin(horarios) if horarios else True
mask_responsavel = (
    df_bruto["responsavel"].isin(responsaveis) if responsaveis else True
)

df = df_bruto[mask_data & mask_horario & mask_responsavel]

if df.empty:
    st.warning("Nenhum dado encontrado com os filtros selecionados.")
    st.stop()

# --- Bloco 1: KPIs Principais ---
st.markdown("### 📈 Resumo do Período Selecionado")

m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    st.metric("PÚBLICO TOTAL", f"{df['total_geral'].sum():,} PAX")
with m2:
    st.metric("ADULTOS", f"{df['adultos'].sum():,}")
with m3:
    st.metric("CRIANÇAS", f"{df['criancas'].sum():,}")
with m4:
    st.metric("VISITANTES", f"{df['visitantes'].sum():,}")
with m5:
    st.metric("CONVERSÕES", f"{df['conversoes'].sum():,}")

st.markdown("---")

# --- Bloco 2: Gráficos de Análise ---
st.markdown("### 📊 Análise Gráfica")

c1, c2 = st.columns(2)

with c1:
    st.subheader("Público Total por Horário de Reunião")
    df_horario = (
        df.groupby("horario")["total_geral"].sum().reset_index().set_index("horario")
    )
    st.bar_chart(df_horario, color="#FFD700")

with c2:
    st.subheader("Proporção: Adultos vs Crianças")
    prop_data = pd.DataFrame(
        {
            "Categoria": ["Adultos", "Crianças"],
            "Quantidade": [df["adultos"].sum(), df["criancas"].sum()],
        }
    ).set_index("Categoria")
    st.bar_chart(prop_data, color="#FFFFFF")

# --- Bloco 3: Evolução Temporal ---
st.subheader("Evolução do Público Atendido por Data")
df_tempo = df.groupby("data")["total_geral"].sum().reset_index().set_index("data")
st.line_chart(df_tempo, color="#FFD700")

st.markdown("---")

# --- Bloco 4: Tabela Detalhada ---
st.markdown("### 📋 Registros Consolidados")
st.dataframe(
    df[
        [
            "data_hora",
            "horario",
            "responsavel",
            "posicao",
            "adultos",
            "criancas",
            "total_geral",
            "visitantes",
            "conversoes",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)
