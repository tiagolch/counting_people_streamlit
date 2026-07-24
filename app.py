import os
import urllib.parse
from datetime import datetime
from PIL import Image
import psycopg2
import streamlit as st

st.set_page_config(
    page_title="Hillsong Portugal em Aveiro - Contador",
    page_icon="▽",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- Função de gravação com Fallback Seguro ---


def salvar_no_banco(dados):
    try:
        # Tenta obter a URL dos secrets
        if "postgres" not in st.secrets or "url" not in st.secrets["postgres"]:
            st.warning("⚠️ Configuração de banco de dados ausente (Secrets).")
            return False

        db_url = st.secrets["postgres"]["url"]

        # Define timeout curto na conexão para não travar a tela caso a rede falhe
        conn = psycopg2.connect(db_url, connect_timeout=3)
        cursor = conn.cursor()

        sql_insert = """
            INSERT INTO contagens_reuniao 
            (data_hora, responsavel, posicao, horario, adultos, criancas, total_geral, visitantes, conversoes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        cursor.execute(
            sql_insert,
            (
                dados["data_hora"],
                dados["responsavel"],
                dados["posicao"],
                dados["horario"],
                dados["adultos"],
                dados["criancas"],
                dados["total_geral"],
                dados["visitantes"],
                dados["conversoes"],
            ),
        )

        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        # Se falhar a gravação no banco, avisa o usuário sem interromper o fluxo
        st.warning(
            "⚠️ Não foi possível conectar à base de dados. O relatório poderá ser enviado normalmente pelo WhatsApp!"
        )
        print(f"Erro ao salvar no banco: {e}")  # Log para debug interno
        return False


# --- Estilização CSS ---
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
    .stTextInput input, .stNumberInput input {
        background-color: #222222 !important;
        color: #FFFFFF !important;
        border: 1px solid #333333 !important;
        border-radius: 8px !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 42px !important;
        font-weight: 700 !important;
        color: #FFD700 !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #AAAAAA !important;
        letter-spacing: 1px;
    }
    div.stButton > button {
        width: 100%;
        height: 52px;
        background-color: #FFFFFF !important;
        color: #000000 !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        border: none !important;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #FFD700 !important;
        color: #000000 !important;
        transform: translateY(-2px);
    }
    hr {
        border-color: #222222 !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

if os.path.exists("logo.png"):
    imagem_logo = Image.open("logo.png")

    col_logo_1, col_logo_2, col_logo_3 = st.columns([2, 1, 2])
    with col_logo_2:
        st.image(imagem_logo, use_column_width=True)
else:
    st.markdown(
        "<h2 style='text-align: center; color: #FFD700; margin-bottom: 20px;'>✝ = ❤️</h2>",
        unsafe_allow_html=True,
    )

st.markdown(
    "<p style='text-align: center; color: #888888; font-size: 14px; letter-spacing: 2px; margin-bottom: 0;'>HILLSONG CHURCH PORTUGAL</p>",
    unsafe_allow_html=True,
)
st.markdown(
    "<h1 style='text-align: center; margin-top: 0; margin-bottom: 30px;'>AVEIRO</h1>",
    unsafe_allow_html=True,
)

if "dados" not in st.session_state:
    st.session_state.dados = {
        "dir_adultos": 0,
        "dir_criancas": 0,
        "dir_visitantes": 0,
        "dir_conversoes": 0,
    }

data_hoje = datetime.now()

st.markdown("### 📝 Identificação")
nome_pessoa = st.text_input(
    "Responsável pela contagem:", placeholder="Ex: Tiago Chaves"
)

col_esq, col_dir = st.columns(2)

with col_esq:
    posicao = st.radio(
        "Posição no Auditório:",
        options=["D1", "E1", "Produção"],
        horizontal=True,
    )

with col_dir:
    horario_selecionado = st.radio(
        "Horário da Reunião:",
        options=["09:30", "11:30", "17:30"],
        horizontal=True,
    )

st.markdown("---")
st.markdown("### 🔢 Métricas de Público")

col1, col2 = st.columns(2)
with col1:
    val_dir_a = st.number_input(
        "Adultos",
        min_value=0,
        step=1,
        value=st.session_state.dados["dir_adultos"],
    )
    val_vis = st.number_input(
        "Visitantes (Novo/Welcome)",
        min_value=0,
        step=1,
        value=st.session_state.dados["dir_visitantes"],
    )

with col2:
    val_dir_c = st.number_input(
        "Crianças (Hillsong Kids)",
        min_value=0,
        step=1,
        value=st.session_state.dados["dir_criancas"],
    )
    val_conv = st.number_input(
        "Decisões / Conversões",
        min_value=0,
        step=1,
        value=st.session_state.dados["dir_conversoes"],
    )

st.session_state.dados.update({
    "dir_adultos": val_dir_a,
    "dir_criancas": val_dir_c,
    "dir_visitantes": val_vis,
    "dir_conversoes": val_conv,
})

total_adultos = st.session_state.dados["dir_adultos"]
total_criancas = st.session_state.dados["dir_criancas"]
total_geral = total_adultos + total_criancas

st.markdown("---")

col_metric, _ = st.columns([2, 1])
with col_metric:
    st.metric(label="PÚBLICO TOTAL ATENDIDO", value=f"{total_geral} PAX")

st.markdown("---")
st.markdown("### 💬 Comunicação")

nome_responsavel = nome_pessoa if nome_pessoa.strip() != "" else "Não informado"

texto_whatsapp = (
    f"📊 *RELATÓRIO DE PÚBLICO - HILLSONG PORTUGAL EM AVEIRO*\n"
    f"📅 *Data:* {data_hoje.strftime('%d/%m/%Y')}\n"
    f"🕒 *Horário:* {horario_selecionado}\n"
    f"👤 *Responsável:* {nome_responsavel}\n\n"
    f"📍 *Posição:* {posicao}\n"
    f"🚶‍♂️ *Total Geral:* {total_geral} pessoas\n"
    f"👨‍💼 *Adultos:* {total_adultos}\n"
    f"👶 *Crianças:* {total_criancas}\n\n"
    f"⭐ *Visitantes:* {st.session_state.dados['dir_visitantes']}\n"
    f"❤️ *Conversões:* {st.session_state.dados['dir_conversoes']}\n\n"
    f"_Enviado via Hillsong Portugal em Aveiro Meeting Counter_"
)

texto_url = urllib.parse.quote(texto_whatsapp)
link_whatsapp = f"https://wa.me/?text={texto_url}"

# --- Botão com Processamento Seguro ---
if st.button("📲 Guardar Dados e Partilhar no WhatsApp"):
    dados_registro = {
        "data_hora": data_hoje,
        "responsavel": nome_responsavel,
        "posicao": posicao,
        "horario": horario_selecionado,
        "adultos": total_adultos,
        "criancas": total_criancas,
        "total_geral": total_geral,
        "visitantes": st.session_state.dados["dir_visitantes"],
        "conversoes": st.session_state.dados["dir_conversoes"],
    }

    sucesso_banco = salvar_no_banco(dados_registro)

    if sucesso_banco:
        st.success("✅ Relatório registado na base de dados!")

    # Exibe o botão do WhatsApp independentemente de ter salvado no banco ou falhado
    st.markdown(
        f"""
        <a href="{link_whatsapp}" target="_blank" style="text-decoration: none;">
            <button style="
                width:100%; 
                height:52px; 
                background-color:#25D366; 
                color:white; 
                border:none; 
                border-radius:8px; 
                font-weight:600; 
                font-size:16px; 
                cursor:pointer;
                margin-top:10px;">
                👉 Abrir WhatsApp agora
            </button>
        </a>
        """,
        unsafe_allow_html=True,
    )
