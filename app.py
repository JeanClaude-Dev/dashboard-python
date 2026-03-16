import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Configuração da Página ---
st.set_page_config(
    page_title="Data Salary Insights | Portfolio",
    page_icon="💰",
    layout="wide",
)

# --- Estilo Customizado (CSS) ---
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 1.8rem; color: #00ffcc; }
    .main { background-color: #0e1117; }
    div.stButton > button:first-child { background-color: #00ffcc; color: black; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- Carregamento Otimizado de Dados ---
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv"
    df = pd.read_csv(url)
    return df

df = load_data()

# --- Barra Lateral Minimalista ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3222/3222764.png", width=100)
    st.title("Filtros de Análise")
    
    anos = st.multiselect("📅 Ano de Referência", sorted(df['ano'].unique()), default=df['ano'].unique())
    senioridade = st.multiselect("📈 Senioridade", sorted(df['senioridade'].unique()), default=df['senioridade'].unique())
    contrato = st.multiselect("📄 Tipo de Contrato", sorted(df['contrato'].unique()), default=df['contrato'].unique())
    
    st.divider()
    st.caption("Desenvolvido para Portfólio de Data Science")

# --- Lógica de Filtragem ---
df_filtrado = df[
    (df['ano'].isin(anos)) &
    (df['senioridade'].isin(senioridade)) &
    (df['contrato'].isin(contrato))
]

# --- Cabeçalho Impactante ---
st.title("📊 Global Data Science Salary Explorer")
st.markdown(f"Exibindo análise de **{len(df_filtrado)}** registros salariais em todo o mundo.")

# --- Seção de KPIs (Métricas) ---
col1, col2, col3, col4 = st.columns(4)

if not df_filtrado.empty:
    avg_salary = df_filtrado['usd'].mean()
    max_salary = df_filtrado['usd'].max()
    mode_job = df_filtrado['cargo'].mode()[0]
    
    with col1:
        st.metric("Salário Médio (Anual)", f"USD {avg_salary/1000:.1f}k")
    with col2:
        st.metric("Teto Salarial", f"USD {max_salary/1000:.1f}k")
    with col3:
        st.metric("Amostras", f"{len(df_filtrado):,}")
    with col4:
        st.metric("Cargo mais Comum", mode_job)
else:
    st.error("Nenhum dado encontrado para os filtros selecionados.")

st.divider()

# --- Análises Visuais ---
tab1, tab2 = st.tabs(["📈 Distribuição & Mercado", "🗺️ Visão Geográfica"])

with tab1:
    c1, c2 = st.columns([1.2, 0.8])
    
    with c1:
        # Gráfico de Barras Horizontal com degradê
        top_jobs = df_filtrado.groupby('cargo')['usd'].mean().nlargest(12).sort_values().reset_index()
        fig_jobs = px.bar(
            top_jobs, x='usd', y='cargo', 
            orientation='h', 
            title="Média Salarial por Cargo (Top 12)",
            color='usd',
            color_continuous_scale='Viridis',
            template="plotly_dark"
        )
        fig_jobs.update_layout(showlegend=False, height=500)
        st.plotly_chart(fig_jobs, use_container_width=True)

    with c2:
        # Histograma com Boxplot Marginal
        fig_dist = px.histogram(
            df_filtrado, x="usd", 
            marginal="box", 
            title="Distribuição Salarial e Outliers",
            color_discrete_sequence=['#00ffcc'],
            template="plotly_dark"
        )
        st.plotly_chart(fig_dist, use_container_width=True)

with tab2:
    # Mapa Coroplético
    st.subheader("Concentração Salarial de Cientistas de Dados")
    df_ds = df_filtrado[df_filtrado['cargo'].str.contains('Data Scientist', case=False)]
    
    if not df_ds.empty:
        geo_data = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        fig_map = px.choropleth(
            geo_data, locations='residencia_iso3', color='usd',
            hover_name='residencia_iso3', 
            color_continuous_scale='RdYlGn',
            template="plotly_dark"
        )
        fig_map.update_layout(height=600, margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("Filtre por cargos que contenham 'Data Scientist' para visualizar o mapa.")

# --- Tabela de Dados & Exportação ---
with st.expander("📂 Explorar Dados Brutos e Exportar"):
    c_down1, c_down2 = st.columns([3, 1])
    with c_down1:
        st.dataframe(df_filtrado, use_container_width=True)
    with c_down2:
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar CSV Filtrado",
            data=csv,
            file_name='data_salaries_export.csv',
            mime='text/csv',
        )
        st.write("Dica: Use estes dados para treinar modelos de regressão!")

# --- Footer ---
st.markdown("---")
st.markdown(
    "<div style='text-align: center'>Dashboard desenvolvido como parte do Portfólio Profissional de Dados</div>", 
    unsafe_allow_html=True
)