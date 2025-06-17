import os, base64
import streamlit as st
import pandas as pd

# ── CONFIG BÁSICA ────────────────────────────────────
st.set_page_config(page_title="Painel de Editais", page_icon="📄", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background:#fff; color:#000; }

    .header { display:flex; justify-content:space-between; align-items:flex-start; }
    .header img { height:100px; }

    /* Forçar cor preta em todos os textos */
    .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #000 !important;
    }

    /* Manter cores originais nos multiselect */
    .stMultiSelect label, .stMultiSelect > div > div {
        color: inherit !important;
    }

    /* Cor preta para outros elementos */
    .stText, .stSubText, div[data-testid="stMarkdownContainer"] {
        color: #000 !important;
    }

    /* Estilo do botão Limpar */
    .stButton > button {
        background-color: white !important;
        color: black !important;
        border: 1px solid #ddd !important;
        border-radius: 4px !important;
    }
    .stButton > button:hover {
        background-color: #ff4444 !important;
        color: white !important;
        border: 1px solid #ff4444 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ── LOGO ─────────────────────────────────────────────
logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()
else:
    logo_base64 = ""

st.markdown(f"""
<div class="header">
  <div>
    <h2>🎯 Painel de Editais do Brasil</h2>
    <p>Use os filtros abaixo e veja instantaneamente os editais que batem.</p>
  </div>
  {'<img src="data:image/png;base64,'+logo_base64+'" alt="Logo">' if logo_base64 else ''}
</div>
""", unsafe_allow_html=True)

# ── DADOS FICTÍCIOS ─────────────────────────────────
editais = [
    {"Título": "Edital de Pesquisa CAPES 2025",          "Público-alvo": "Pesquisadores", "Categoria": "Pesquisa",   "Área": "Educação"},
    {"Título": "Inovação para Startups 2024",            "Público-alvo": "Empresas",      "Categoria": "Inovação",   "Área": "Tecnologia"},
    {"Título": "Edital FINEP Saúde Pública",             "Público-alvo": "Pesquisadores", "Categoria": "Saúde",      "Área": "Saúde"},
    {"Título": "Programa Nacional Jovem Cientista",      "Público-alvo": "Estudantes",    "Categoria": "Pesquisa",   "Área": "Multidisciplinar"},
    {"Título": "Desenv. Sustentável Rural",              "Público-alvo": "Cooperativas",  "Categoria": "Inovação",   "Área": "Meio Ambiente"},
    {"Título": "Conecta Brasil – Educação Digital",      "Público-alvo": "Escolas",       "Categoria": "Tecnologia", "Área": "Educação"},
]
df = pd.DataFrame(editais)

# ── FUNÇÃO DE LIMPAR FILTROS ─────────────────────────
def clear_filters():
    for key in ("cats_sel", "pubs_sel", "areas_sel"):
        st.session_state[key] = []

# ── FILTROS + BOTÃO LIMPAR ──────────────────────────
st.markdown("### 🔍 Filtros")

# Botão vem primeiro; on_click executa antes dos widgets
st.button("🔄 Limpar todos os filtros", on_click=clear_filters)

col1, col2, col3 = st.columns(3)

# --- Categoria -------------------------------------------------
with col1:
    categorias_disponiveis = sorted(df["Categoria"].unique())
    cats_escolhidas = st.multiselect(
        "🏷️ Categoria",
        categorias_disponiveis,
        key="cats_sel"
    )

df_cat = df[df["Categoria"].isin(cats_escolhidas)] if cats_escolhidas else df.copy()

# --- Público-alvo ---------------------------------------------
with col2:
    publicos_disponiveis = sorted(df_cat["Público-alvo"].unique())
    pubs_escolhidos = st.multiselect(
        "👥 Público-alvo",
        publicos_disponiveis,
        key="pubs_sel"
    )

df_pub = df_cat[df_cat["Público-alvo"].isin(pubs_escolhidos)] if pubs_escolhidos else df_cat.copy()

# --- Área ------------------------------------------------------
with col3:
    areas_disponiveis = sorted(df_pub["Área"].unique())
    areas_escolhidas = st.multiselect(
        "📚 Área",
        areas_disponiveis,
        key="areas_sel"
    )

df_final = (
    df_pub[df_pub["Área"].isin(areas_escolhidas)]
    if areas_escolhidas
    else df_pub.copy()
)

# ── RESULTADO ───────────────────────────────────────
st.markdown("---")
st.markdown("### 📄 Editais Encontrados")

total_editais = len(df)
editais_filtrados = len(df_final)

st.markdown(f"""
<div style="background-color: #f0f8ff; padding: 10px; border-radius: 5px; border-left: 4px solid #0066cc;">
    <strong style="color: #0066cc; font-size: 16px;">📊 {editais_filtrados} de {total_editais} editais correspondem aos filtros</strong>
</div>
""", unsafe_allow_html=True)

if df_final.empty:
    st.error("🔍 Nenhum edital encontrado com os filtros atuais. Tente ajustar os critérios de busca.")
else:
    for _, row in df_final.iterrows():
        st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #28a745;">
            <h4 style="color: #2c3e50; margin: 0 0 10px 0;">📄 {row['Título']}</h4>
            <div style="display: flex; gap: 15px; flex-wrap: wrap;">
                <span style="background-color: #e3f2fd; padding: 4px 8px; border-radius: 4px; font-size: 12px;">
                    🏷️ {row['Categoria']}
                </span>
                <span style="background-color: #f3e5f5; padding: 4px 8px; border-radius: 4px; font-size: 12px;">
                    👥 {row['Público-alvo']}
                </span>
                <span style="background-color: #e8f5e8; padding: 4px 8px; border-radius: 4px; font-size: 12px;">
                    📚 {row['Área']}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
