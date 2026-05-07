import streamlit as st
import sqlite3
import pandas as pd
import joblib
import numpy as np

st.set_page_config(
    page_title="Sistem Deteksi Stunting Balita",
    page_icon="🩺",
    layout="wide"
)

# ===============================
# CUSTOM CSS - Mirip Flask UI
# ===============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

/* Reset & Global */
* { font-family: 'Poppins', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #4fc3c3 0%, #38a0a0 30%, #a0c4e8 70%, #b8d4f0 100%);
    min-height: 100vh;
}

/* Hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; }

/* ======= METRIC CARDS (Top Stats) ======= */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.25) !important;
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.4);
    border-radius: 16px;
    padding: 1.5rem 2rem !important;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

[data-testid="metric-container"] label {
    color: white !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.5px;
}

[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: white !important;
    font-size: 2.8rem !important;
    font-weight: 700 !important;
    line-height: 1.2;
}

[data-testid="stMetricDelta"] { display: none; }

/* ======= CARDS ======= */
.card {
    background: rgba(255,255,255,0.22);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,0.35);
    border-radius: 20px;
    padding: 1.8rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.08);
    margin-bottom: 1rem;
}

.card-title {
    color: white;
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ======= NUMBER INPUT ======= */
.stNumberInput > div > div > input {
    background: rgba(255,255,255,0.5) !important;
    border: none !important;
    border-radius: 10px !important;
    color: #1a4a4a !important;
    font-weight: 600 !important;
    padding: 0.6rem 1rem !important;
}
.stNumberInput > div > div:focus-within {
    background: rgba(255,255,255,0.7) !important;
    box-shadow: 0 0 0 2px rgba(56,160,160,0.5) !important;
}

/* ======= SELECTBOX - abu gelap + teks putih ======= */
.stSelectbox > div > div,
.stSelectbox > div > div > div,
[data-baseweb="select"] > div {
    background: rgba(70,70,70,0.8) !important;
    border: none !important;
    border-radius: 10px !important;
    color: white !important;
}

/* Teks terpilih */
.stSelectbox [data-baseweb="select"] span,
.stSelectbox [data-baseweb="select"] div[class*="ValueContainer"] *,
.stSelectbox [data-baseweb="select"] div[class*="singleValue"],
.stSelectbox [data-baseweb="select"] div[class*="placeholder"] {
    color: white !important;
    font-weight: 500 !important;
}

/* Panah dropdown */
.stSelectbox svg { fill: white !important; }

/* List pilihan */
[data-baseweb="popover"] [role="option"],
[data-baseweb="menu"] [role="option"] {
    color: #1a4a4a !important;
    background: white !important;
}
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="menu"] [role="option"]:hover {
    background: #e0f5f5 !important;
}

/* Label */
.stSelectbox label, .stNumberInput label {
    color: white !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
}

/* ======= SUBMIT BUTTON ======= */
.stFormSubmitButton > button {
    background: rgba(255,255,255,0.25) !important;
    color: white !important;
    border: 1.5px solid rgba(255,255,255,0.6) !important;
    border-radius: 10px !important;
    width: 100% !important;
    padding: 0.7rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    transition: all 0.3s ease !important;
    backdrop-filter: blur(4px) !important;
}

.stFormSubmitButton > button:hover {
    background: rgba(255,255,255,0.4) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(0,0,0,0.15) !important;
}

/* ======= RESULT BOX ======= */
.result-box {
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    margin-top: 1rem;
    text-align: center;
    font-weight: 600;
    font-size: 1rem;
    animation: fadeIn 0.5s ease;
}
.result-normal { background: rgba(72,199,142,0.3); border: 1.5px solid #48c78e; color: white; }
.result-stunting { background: rgba(255,189,89,0.3); border: 1.5px solid #ffbd59; color: white; }
.result-severe { background: rgba(255,91,91,0.3); border: 1.5px solid #ff5b5b; color: white; }

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ======= RESET BUTTON ======= */
.stButton > button {
    background: transparent !important;
    color: white !important;
    border: 1.5px solid rgba(255,255,255,0.5) !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    transition: all 0.3s !important;
}
.stButton > button:hover {
    background: rgba(255,255,255,0.15) !important;
    border-color: white !important;
}

/* ======= DATAFRAME ======= */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

/* ======= PAGE TITLE ======= */
.page-title {
    color: white;
    font-size: 1.6rem;
    font-weight: 700;
    text-align: center;
    margin-bottom: 1.5rem;
    text-shadow: 0 2px 8px rgba(0,0,0,0.15);
    letter-spacing: 0.5px;
}

/* ======= LEGEND ======= */
.legend-item {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: white;
    font-size: 0.85rem;
    margin-right: 1rem;
}
.legend-dot {
    width: 14px; height: 14px;
    border-radius: 3px;
    display: inline-block;
}

/* DIVIDER */
hr { border-color: rgba(255,255,255,0.2) !important; }
</style>
""", unsafe_allow_html=True)

# ===============================
# LOAD MODEL & ENCODER
# ===============================
@st.cache_resource
def load_models():
    model = joblib.load("svm_best_model.joblib")
    label_encoder = joblib.load("label_encoder_tb.joblib")
    return model, label_encoder

try:
    model, label_encoder = load_models()
except Exception as e:
    st.error(f"Gagal memuat model: {e}")
    st.stop()

# ===============================
# DATABASE SETUP
# ===============================
def get_db():
    conn = sqlite3.connect("stunting.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS balita (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gender INTEGER,
        usia_ukur REAL,
        berat REAL,
        tinggi REAL,
        status TEXT
    )
    """)
    conn.commit()
    conn.close()

create_table()

# ===============================
# LOGIKA Z-SCORE
# ===============================
def estimate_zscore(umur, tinggi, jk):
    if umur <= 12:
        median_tinggi = 50.0 + (umur * 2.15)
    elif umur <= 24:
        median_tinggi = 75.8 + (umur - 12) * 1.05
    else:
        median_tinggi = 88.4 + (umur - 24) * 0.65
    z = (tinggi - median_tinggi) / 2.8
    return round(z, 2)

# ===============================
# DASHBOARD DATA
# ===============================
def get_dashboard_data():
    conn = get_db()
    rows = conn.execute("SELECT status, COUNT(*) as jumlah FROM balita GROUP BY status").fetchall()
    conn.close()
    status_dict = {"Normal": 0, "Stunting": 0, "Severely Stunted": 0}
    for r in rows:
        if r["status"] in status_dict:
            status_dict[r["status"]] = r["jumlah"]
    total = sum(status_dict.values())
    stunting_total = status_dict["Stunting"] + status_dict["Severely Stunted"]
    prevalensi = round((stunting_total / total) * 100, 1) if total > 0 else 0
    return status_dict, total, stunting_total, prevalensi

# ===============================
# MAIN UI
# ===============================
st.markdown('<div class="page-title">🩺 Sistem Deteksi Stunting Balita</div>', unsafe_allow_html=True)

# --- TOP METRICS ---
status_dict, total, stunting_total, prevalensi = get_dashboard_data()

m1, m2, m3 = st.columns(3)
m1.metric("Total Balita", total)
m2.metric("Total Stunting", stunting_total)
m3.metric("Prevalensi", f"{prevalensi}%")

st.markdown("<br>", unsafe_allow_html=True)

# --- MAIN CONTENT: 2 Kolom ---
col_left, col_right = st.columns([1, 1.2], gap="large")

# ---- KIRI: Form Input ----
with col_left:
    st.markdown('<div class="card"><div class="card-title">📋 Input Data Balita</div>', unsafe_allow_html=True)

    with st.form("form_prediksi"):
        gender = st.selectbox(
            "Jenis Kelamin",
            options=["-- Pilih --", "Laki-laki", "Perempuan"]
        )
        usia = st.number_input("Umur (Bulan)", min_value=0.0, max_value=60.0, step=0.1, value=None, placeholder="Masukkan umur...")
        berat = st.number_input("Berat Badan (kg)", min_value=0.0, step=0.1, value=None, placeholder="Masukkan berat...")
        tinggi = st.number_input("Tinggi Badan (cm)", min_value=0.0, step=0.1, value=None, placeholder="Masukkan tinggi...")

        submitted = st.form_submit_button("🔍  ANALISIS DATA")

    # Hasil prediksi di bawah form
    if submitted:
        if gender == "-- Pilih --" or usia is None or berat is None or tinggi is None:
            st.markdown('<div class="result-box result-stunting">⚠️ Harap isi semua data dengan lengkap!</div>', unsafe_allow_html=True)
        else:
            try:
                jk = 0 if gender == "Laki-laki" else 1
                zs = estimate_zscore(usia, tinggi, jk)

                data_input = pd.DataFrame([[jk, usia, berat, tinggi, zs]],
                                           columns=["jk", "usia_ukur", "berat", "tinggi", "zs_tb_u"])

                prediction_numeric = model.predict(data_input)[0]
                status = label_encoder.inverse_transform([prediction_numeric])[0]

                # Hard logic (Standar WHO)
                if zs < -3.0:
                    status = "Severely Stunted"
                elif zs < -2.0:
                    status = "Stunting"
                else:
                    status = "Normal"

                # Simpan DB
                conn = get_db()
                conn.execute("INSERT INTO balita (gender, usia_ukur, berat, tinggi, status) VALUES (?,?,?,?,?)",
                             (jk, usia, berat, tinggi, status))
                conn.commit()
                conn.close()

                # Tampilkan hasil
                if status == "Normal":
                    css_class = "result-normal"
                    icon = "✅"
                elif status == "Stunting":
                    css_class = "result-stunting"
                    icon = "⚠️"
                else:
                    css_class = "result-severe"
                    icon = "🚨"

                st.markdown(f'''
                    <div class="result-box {css_class}">
                        {icon} Status: <strong>{status}</strong><br>
                        <small>Z-Score TB/U: {zs}</small>
                    </div>
                ''', unsafe_allow_html=True)

                st.rerun()

            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

# ---- KANAN: Pie Chart + Reset ----
with col_right:
    st.markdown('<div class="card"><div class="card-title">🥧 Distribusi Status Gizi</div>', unsafe_allow_html=True)

    # Pie chart dengan plotly
    try:
        import plotly.graph_objects as go

        status_dict, total, stunting_total, prevalensi = get_dashboard_data()
        labels = list(status_dict.keys())
        values = list(status_dict.values())
        colors = ["#48c78e", "#ffbd59", "#ff5b5b"]

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0,
            marker=dict(colors=colors, line=dict(color='rgba(255,255,255,0.3)', width=2)),
            textinfo='percent',
            textfont=dict(size=13, color='white', family='Poppins'),
            hovertemplate='<b>%{label}</b><br>Jumlah: %{value}<br>%{percent}<extra></extra>'
        )])

        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=10, b=10, l=10, r=10),
            height=300,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.15,
                xanchor="center",
                x=0.5,
                font=dict(color='white', size=12),
                bgcolor='rgba(0,0,0,0)'
            )
        )

        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    except ImportError:
        # Fallback bar chart
        chart_df = pd.DataFrame({
            "Status": list(status_dict.keys()),
            "Jumlah": list(status_dict.values())
        }).set_index("Status")
        st.bar_chart(chart_df)

    # Tombol Reset
    st.markdown("<br>", unsafe_allow_html=True)
    col_btn = st.columns([1, 2, 1])
    with col_btn[1]:
        if st.button("🗑️  Reset Database", use_container_width=True):
            conn = get_db()
            conn.execute("DELETE FROM balita")
            conn.commit()
            conn.close()
            st.success("Data berhasil direset!")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ---- TABEL RIWAYAT ----
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="card"><div class="card-title">📊 Riwayat Data Balita</div>', unsafe_allow_html=True)

conn = get_db()
df = pd.read_sql_query("""
    SELECT id, 
           CASE gender WHEN 0 THEN 'Laki-laki' ELSE 'Perempuan' END as 'Jenis Kelamin',
           usia_ukur as 'Usia (bln)',
           berat as 'Berat (kg)',
           tinggi as 'Tinggi (cm)',
           status as 'Status'
    FROM balita ORDER BY id DESC
""", conn)
conn.close()

if df.empty:
    st.markdown('<p style="color:rgba(255,255,255,0.6); text-align:center;">Belum ada data tersimpan.</p>', unsafe_allow_html=True)
else:
    st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown('</div>', unsafe_allow_html=True)