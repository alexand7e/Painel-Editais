import os, base64
import streamlit as st
import pandas as pd
import unicodedata

# ── CONFIG BÁSICA ───────────────────────────────────
st.set_page_config(page_title="Painel de Editais", page_icon="📄", layout="wide")

# ── CSS CUSTOMIZADO ─────────────────────────────────
st.markdown(
    """
    <style>
    /* Estilo geral */
    .stApp { background:#fff; color:#000; }
    .header { display:flex; justify-content: space-between; align-items: flex-start; }
    .header img { height: 100px; width: auto; }
    .stButton > button { background-color: white !important; color: black !important; border:1px solid #ddd !important; border-radius:4px !important; }
    .stMultiSelect label { color: #000 !important; }

    /* Estilo dos cards usando <details> */
    details.edital-card {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        margin: 20px 0 !important;
    }
    details.edital-card summary {
        list-style: none;
        outline: none;
        cursor: pointer;
        padding: 20px;
        margin: 0;
        display: block;
    }
    details.edital-card summary::-webkit-details-marker {
        display: none;
    }
    details.edital-card summary h3 {
        margin: 0 0 10px 0;
    }
    details.edital-card summary ul {
        margin: 0;
        padding: 0;
    }
    details.edital-card summary li {
        margin-bottom: 4px;
    }
    details.edital-card .details-list {
        padding: 0 20px 20px 20px;
        margin: 0;
    }
    details.edital-card .details-list li {
        margin-bottom: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ── FUNÇÃO PARA NORMALIZAR TEXTO ─────────────────────────────────
def normalizar_texto(texto):
    if pd.isna(texto) or texto == '—':
        return texto
    texto_sem_acento = unicodedata.normalize('NFD', str(texto))
    texto_sem_acento = ''.join(char for char in texto_sem_acento if unicodedata.category(char) != 'Mn')
    return texto_sem_acento.lower().strip()

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
    <h2> Painel de Editais do Piauí</h2>
  </div>
  {'<img src="data:image/png;base64,'+logo_base64+'" alt="Logo">' if logo_base64 else ''}
</div>
""", unsafe_allow_html=True)

# ── CARREGAMENTO E TRATAMENTO DOS DADOS ─────────────────────────────────
df = pd.read_excel("Editais.xlsx")
df = df.rename(columns={'Editais': 'Título'})
required_columns = ["Título", "Categoria", "Público", "Área"]
if any(col not in df.columns for col in required_columns):
    st.error("❌ Algumas colunas necessárias não foram encontradas!")
    st.stop()
for col in df.columns:
    df[col] = df[col].astype(str).replace(['nan','None','NaN','null',''], '—').fillna('—').str.strip()

# ── FUNÇÃO PARA LIMPAR FILTROS ─────────────────────────
def clear_filters():
    for k in ("categoria_sel", "publico_sel", "area_sel"):
        if k in st.session_state:
            st.session_state[k] = []

# ── FILTROS ────────────────────────────────────────
st.markdown("---")
st.button("🔄 Limpar todos os filtros", on_click=clear_filters)
col1, col2, col3 = st.columns(3)
with col1:
    cat = st.multiselect("🏛️ Categoria", ["Público","Privado"], key="categoria_sel")
    if cat:
        # normaliza as tags escolhidas
        norm_sel = [normalizar_texto(c) for c in cat]

        # aplica normalização na coluna e testa se todas as tags estão presentes
        norm_cat_series = df["Categoria"].apply(normalizar_texto)
        mask = pd.Series(True, index=df.index)
        for nc in norm_sel:
            mask &= norm_cat_series.str.contains(nc, na=False)

        df = df[mask]

with col2:
    publicos = sorted({p.strip() for val in df["Público"].dropna() for p in str(val).replace(';',',').split(',') if p.strip()})
    pub = st.multiselect("👥 Público", publicos, key="publico_sel")
    if pub:
        df = df[df["Público"].apply(lambda x: all(item.lower() in x.lower() for item in pub))]
with col3:
    areas = {normalizar_texto(a.strip()): a.title() for val in df["Área"].dropna() if val!='—' for a in str(val).split(',') if a.strip()}
    area_sel = st.multiselect("📚 Área", sorted(areas.values()), key="area_sel")
    if area_sel:
        df = df[df["Área"].apply(lambda v: all(normalizar_texto(a) in [normalizar_texto(x) for x in str(v).split(',')] for a in area_sel))]

# ── RESULTADOS ───────────────────────────────────
st.markdown("---")
st.markdown("### 📄 Editais Encontrados")
st.markdown(f"📊 {len(df)} editais correspondem aos filtros")

detail_labels = {
    'Fonte': '📰 Fonte',
    'Objetivo': '🎯 Objetivo',
    'Requisitos': '✅ Requisitos',
    'Público-Alvo': '🎯 Público-Alvo',
    'Prazo': '⏰ Prazo',
    'Recursos': '💰 Recursos',
    'Link do edital': '🔗 Link do Edital'
}

if df.empty:
    st.info("🔍 Nenhum edital encontrado com os filtros atuais.")
else:
    for _, row in df.iterrows():
        detalhes_html = ""
        for col in df.columns:
            if col in {"Título", "Categoria", "Público", "Área", "Órgãos"}:
                continue
            val = row[col]
            if val and val != '—':
                lbl = detail_labels.get(col, col)
                if col == 'Link do edital':
                    detalhes_html += f'<li><strong>{lbl}:</strong> <a href="{val}" target="_blank">Acessar edital</a></li>'
                else:
                    detalhes_html += f'<li><strong>{lbl}:</strong> {val}</li>'

        card_html = f"""
        <details class="edital-card">
          <summary>
            <h3>🏛️ {row['Título']}</h3>
            <ul>
              <li><strong>Categoria:</strong> {row['Categoria']}</li>
              <li><strong>Público:</strong> {row['Público']}</li>
              <li><strong>Área:</strong> {row['Área']}</li>
            </ul>
          </summary>
          <ul class="details-list">
            {detalhes_html}
          </ul>
        </details>
        """
        st.markdown(card_html, unsafe_allow_html=True)
