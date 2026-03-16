import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
st.set_page_config(
    page_title="Salary Insights Pro",
    page_icon="📊",
    layout="wide",
)

# --- CSS Avançado: Estilo Azul com Sombras ---
st.markdown("""
    <style>
    /* Fundo da página e fontes */
    .main { background-color: #f8f9fa; }
    
    /* Título Principal */
    .main-title {
        font-size: 22px !important;
        font-weight: 700;
        color: #1E3A8A; /* Azul Escuro */
        margin-bottom: 5px;
    }
    
    /* Subtítulo das Seções */
    .section-subtitle {
        font-size: 16px !important;
        font-weight: 500;
        color: #475569;
        margin-bottom: 20px;
    }

    /* Estilização dos Filtros na Barra Lateral (Azul e Sombra) */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    .stMultiSelect, .stSelectbox {
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        padding: 5px;
        border: 1px solid #dbeafe;
    }

    /* Estilização das Métricas (Cards Azuis) */
    [data-testid="stMetric"] {
        background-color: #dbeafe;
        border-left: 5px solid #3B82F6; /* Linha lateral azul */
        padding: 15px !important;
        border-radius: 10px !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 13px !important;
        color: #64748b !important;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 20px !important;
        color: #1E40AF !important; /* Valor em azul escuro */
    }
    </style>
    """, unsafe_allow_html=True)

# --- Carregamento Otimizado ---
@st.cache_data
def load_data():
    return pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")

df = load_data()

# --- Barra Lateral (Filtros Estilizados) ---
with st.sidebar:
    st.markdown("<h2 style='color: #051647; font-size: 20px;'>🔍 Refinar Busca</h2>", unsafe_allow_html=True)
    
    anos = st.multiselect("Anos", sorted(df['ano'].unique()), default=df['ano'].unique())
    senioridade = st.multiselect("Senioridade", sorted(df['senioridade'].unique()), default=df['senioridade'].unique())
    contrato = st.multiselect("Tipo de Contrato", sorted(df['contrato'].unique()), default=df['contrato'].unique())

# --- Filtragem ---
df_filtrado = df[
    (df['ano'].isin(anos)) &
    (df['senioridade'].isin(senioridade)) &
    (df['contrato'].isin(contrato))
]

# --- Conteúdo Principal ---
st.markdown('<p class="main-title">Dashboard de Análise de Salários na Área de Dados</p>', unsafe_allow_html=True)
st.markdown('<p class="section-subtitle">Métricas gerais (Salário anual em USD)</p>', unsafe_allow_html=True)

# --- KPIs em Cards ---
if not df_filtrado.empty:
    m1, m2, m3, m4 = st.columns(4)
    
    m1.metric("Salário Médio", f"${df_filtrado['usd'].mean():,.0f}")
    m2.metric("Salário Máximo", f"${df_filtrado['usd'].max():,.0f}")
    m3.metric("Total de Registros", f"{len(df_filtrado):,}")
    m4.metric("Top Cargo", df_filtrado["cargo"].mode()[0])
else:
    st.info("Selecione filtros para exibir os resultados.")

st.markdown("<br>", unsafe_allow_html=True)

# --- Gráficos (Tons de Azul) ---
c1, c2 = st.columns(2)

with c1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values().reset_index()
        # Usando color_discrete_sequence para manter a paleta azul
        fig1 = px.bar(top_cargos, x='usd', y='cargo', orientation='h', 
                      title="Média Salarial por Cargo", 
                      color_discrete_sequence=['#3B82F6'])
        fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', title_font_size=14)
        st.plotly_chart(fig1, use_container_width=True)

with c2:
    if not df_filtrado.empty:
        fig2 = px.histogram(df_filtrado, x='usd', nbins=30, 
                            title="Frequência Salarial",
                            color_discrete_sequence=['#1E40AF'])
        fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', title_font_size=14)
        st.plotly_chart(fig2, use_container_width=True)

# --- Tabela ---
st.markdown('<p class="section-subtitle">Exploração de Dados Detalhada</p>', unsafe_allow_html=True)
st.dataframe(df_filtrado, use_container_width=True)