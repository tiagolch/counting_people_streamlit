import streamlit as st
import urllib.parse
from datetime import datetime

st.set_page_config(
    page_title="Contador Igreja",
    page_icon="👑",
    layout="centered"
)

st.markdown("""
    <style>
    div.stButton > button:first-child {
        width: 100%;
        height: 50px;
        font-size: 16px;
        font-weight: bold;
    }
    .metric-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⛪ Contador por reunião - Hillsong em Aveiro")
st.write("Introduza os dados recolhidos para consolidar o relatório.")

if "dados" not in st.session_state:
    st.session_state.dados = {
        "dir_adultos": 0, "dir_criancas": 0, "dir_visitantes": 0, "dir_conversoes": 0
    }

st.markdown("### 📝 Identificação e Horário")

data_hoje = datetime.now()

nome_pessoa = st.text_input("Nome do responsável pela contagem:", placeholder="Ex: João Silva")

posicao = st.radio(
    "Selecione a posição do responsável:",
    options=["D1", "E1", "Produção"],
    horizontal=True
)

horario_selecionado = st.radio(
    "Selecione o horário da reunião:",
    options=["09:30", "11:30", "17:30"],
    horizontal=True 
)

st.markdown("---")
st.markdown("### 🔢 Dados da Contagem")

val_dir_a = st.number_input("Adultos", min_value=0,
                            step=1, value=st.session_state.dados["dir_adultos"])
val_dir_c = st.number_input("Crianças", min_value=0,
                            step=1, value=st.session_state.dados["dir_criancas"])
val_vis = st.number_input("Visitantes", min_value=0,
                          step=1, value=st.session_state.dados["dir_visitantes"])
val_conv = st.number_input("Conversões / Decisões", min_value=0,
                           step=1, value=st.session_state.dados["dir_conversoes"])

st.markdown("---")

st.session_state.dados.update({
    "dir_adultos": val_dir_a, 
    "dir_criancas": val_dir_c,
    "dir_visitantes": val_vis, 
    "dir_conversoes": val_conv,
})

total_adultos = st.session_state.dados["dir_adultos"]
total_criancas = st.session_state.dados["dir_criancas"]
total_geral = total_adultos + total_criancas

st.markdown("### 📊 Totais Calculados")
st.metric("PÚBLICO TOTAL", total_geral)

st.markdown("---")
st.markdown("### 💬 Enviar para o WhatsApp")

nome_responsavel = nome_pessoa if nome_pessoa.strip() != "" else "Não informado"

texto_whatsapp = (
    f"📊 *RELATÓRIO DE PÚBLICO DA REUNIÃO*\n"
    f"📅 *Data:* {data_hoje.strftime('%d/%m/%Y')}\n"
    f"🕒 *Horário:* {horario_selecionado}\n"
    f"👤 *Responsável:* {nome_responsavel}\n"
    f"📍 *Posição:* {posicao}\n"
    f"🚶‍♂️ *Total Geral:* {total_geral} pessoas\n"
    f"👨‍💼 *Adultos:* {total_adultos}\n"
    f"👶 *Crianças:* {total_criancas}\n\n"
    f"⭐ *Visitantes:* {st.session_state.dados['dir_visitantes']}\n"
    f"❤️ *Conversões:* {st.session_state.dados['dir_conversoes']}\n\n"
    f"_Enviado via Contador de Reuniões Igreja_"
)

st.text_area("Toque e segure para copiar o texto abaixo:",
             value=texto_whatsapp, height=220)

texto_url = urllib.parse.quote(texto_whatsapp)
link_whatsapp = f"https://wa.me/?text={texto_url}"

st.markdown(f'<a href="{link_whatsapp}" target="_blank"><button style="width:100%; height:50px; background-color:#25D366; color:white; border:none; border-radius:5px; font-weight:bold; font-size:16px; cursor:pointer;">📲 Partilhar Direto no WhatsApp</button></a>', unsafe_allow_html=True)