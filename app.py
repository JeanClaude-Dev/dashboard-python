import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
st.set_page_config(
    page_title="Data Salary Analytics",
    page_icon="📊",
    layout="wide",
)

# --- CSS Customizado (UI/UX Moderna) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    
    /* Títulos e Subtítulos do Corpo Principal */
    .main-title { font-size: 22px !important; font-weight: 700; color: #1E3A8A; margin-bottom: 5px; }
    .section-subtitle { font-size: 15px !important; font-weight: 500; color: #64748b; margin-bottom: 20px; }

    /* TITULOS DOS FILTROS EM AZUL MARINHO */
    [data-testid="stWidgetLabel"] p {
        color: #000080 !important; /* Azul Marinho (Navy) */
        font-weight: 600 !important;
        font-size: 15px !important;
    }

    /* Cards de Métricas */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border-left: 5px solid #3B82F6;
        padding: 15px !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    [data-testid="stMetricLabel"] { font-size: 13px !important; color: #64748b !important; }
    [data-testid="stMetricValue"] { font-size: 22px !important; color: #1E40AF !important; }

    /* Estilização dos Filtros (Selects) */
    .stMultiSelect {
        background-color: #ffffff;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Ajuste de padding das colunas */
    [data-testid="column"] { padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- Carregamento de Dados ---
@st.cache_data
def load_data():
    # Carrega o dataframe diretamente do link fornecido
    df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")
    return df

df = load_data()

# --- Barra Lateral ---
with st.sidebar:
    st.markdown("<h2 style='color: #1E3A8A; font-size: 18px;'>⚙️ Configurações</h2>", unsafe_allow_html=True)
    st.divider()
    
    # Filtros com títulos agora estilizados em Azul Marinho via CSS
    anos = st.multiselect("Ano", sorted(df['ano'].unique()), default=df['ano'].unique())
    senioridade = st.multiselect("Senioridade", sorted(df['senioridade'].unique()), default=df['senioridade'].unique())
    tamanho_emp = st.multiselect("Tamanho da Empresa", sorted(df['tamanho_empresa'].unique()), default=df['tamanho_empresa'].unique())

# --- Filtragem ---
df_filtrado = df[
    (df['ano'].isin(anos)) &
    (df['senioridade'].isin(senioridade)) &
    (df['tamanho_empresa'].isin(tamanho_emp))
]

# --- Cabeçalho ---
st.markdown('<p class="main-title">Dashboard de Análise de Salários na Área de Dados</p>', unsafe_allow_html=True)
st.markdown('<p class="section-subtitle">Visão executiva baseada em registros salariais globais (USD)</p>', unsafe_allow_html=True)

# --- Linha 1: KPIs ---
if not df_filtrado.empty:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Salário Médio", f"${df_filtrado['usd'].mean():,.0f}")
    m2.metric("Salário Máximo", f"${df_filtrado['usd'].max():,.0f}")
    m3.metric("Total de Registros", f"{len(df_filtrado):,}")
    m4.metric("Cargo Principal", df_filtrado["cargo"].mode()[0])

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Linha 2: Gráficos ---
    col_bar, col_donut = st.columns([2, 1])

    with col_bar:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values().reset_index()
        fig_bar = px.bar(top_cargos, x='usd', y='cargo', orientation='h', 
                         title="Média Salarial por Cargo (Top 10)", 
                         color_discrete_sequence=['#3B82F6'])
        fig_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', title_font_size=14, height=400)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_donut:
        # Gráfico de Rosca: Tamanho da Empresa
        df_tamanho = df_filtrado['tamanho_empresa'].value_counts().reset_index()
        df_tamanho.columns = ['tamanho', 'contagem']
        df_tamanho['tamanho'] = df_tamanho['tamanho'].map({'S': 'Pequena', 'M': 'Média', 'L': 'Grande'})
        
        fig_donut = px.pie(df_tamanho, values='contagem', names='tamanho', hole=0.6,
                           title="Distribuição por Empresa",
                           color_discrete_sequence=['#1E3A8A', '#3B82F6', '#93C5FD'])
        fig_donut.update_layout(title_font_size=14, height=400, showlegend=True, 
                              legend=dict(yanchor="top", y=-0.1, xanchor="center", x=0.5, orientation="h"))
        st.plotly_chart(fig_donut, use_container_width=True)

    # --- Linha 3: Histograma ---
    st.markdown("---")
    fig_hist = px.histogram(df_filtrado, x='usd', nbins=40, title="Frequência de Faixas Salariais",
                            color_discrete_sequence=['#1E40AF'])
    fig_hist.update_layout(plot_bgcolor='rgba(0,0,0,0)', title_font_size=14, height=300)
    st.plotly_chart(fig_hist, use_container_width=True)

else:
    st.info("Utilize os filtros laterais para iniciar a análise.")

# --- Rodapé ---
with st.expander("🔍 Explorar Dados Detalhados"):
    st.dataframe(df_filtrado, use_container_width=True)