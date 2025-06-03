import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import geopandas as gpd

# Setting page config dan judul
st.set_page_config(page_title="Analisis Cluster Zona Overfishing", layout="wide")
st.title("Analisis Cluster Wilayah Rawan Overfishing")
st.markdown("""
Aplikasi ini menampilkan hasil clustering aktivitas kapal nelayan beserta peta interaktif dan grafik pendukung.  
Gunakan filter yang ada di sidebar untuk menyaring data berdasarkan jenis operasi, periode waktu, dan intensity.
""")

# ===== Fungsi untuk memuat data =====
@st.cache_data(show_spinner=True)
def load_data():
    # Pastikan file 'hasil_clustering_clean.csv' ada pada direktori yang sama
    df = pd.read_csv("hasil_clustering_clean.csv")
    # Konversi timestamp menjadi datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

df = load_data()

# ===== Sidebar: Filter Data =====
st.sidebar.header("Filter Data")

# Filter berdasarkan Jenis Operasi
opsi_operasi = df['jenis_operasi'].unique().tolist()
selected_ops = st.sidebar.multiselect("Pilih Jenis Operasi", opsi_operasi, default=opsi_operasi)

# Filter berdasarkan rentang tanggal
min_date = df['timestamp'].min().date()
max_date = df['timestamp'].max().date()
selected_date = st.sidebar.date_input("Pilih Rentang Tanggal", 
                                        value=(min_date, max_date),
                                        min_value=min_date,
                                        max_value=max_date)

# Filter berdasarkan rentang intensity
min_intensity = int(df['intensity'].min())
max_intensity = int(df['intensity'].max())
selected_intensity = st.sidebar.slider("Rentang Intensity", min_intensity, max_intensity, (min_intensity, max_intensity))

# Terapkan filter ke DataFrame
filtered_df = df[
    (df['jenis_operasi'].isin(selected_ops)) &
    (df['timestamp'].dt.date >= selected_date[0]) &
    (df['timestamp'].dt.date <= selected_date[1]) &
    (df['intensity'] >= selected_intensity[0]) &
    (df['intensity'] <= selected_intensity[1])
]

st.sidebar.markdown(f"**Total data terfilter:** {filtered_df.shape[0]} baris")

# ===== Tampilan Data =====
st.subheader("Preview Data Hasil Clustering")
st.dataframe(filtered_df.head(10))

# ===== Ringkasan Statistik =====
st.subheader("Statistik Rata‑Rata Intensity per Cluster")
cluster_summary = filtered_df.groupby('cluster')['intensity'].mean().reset_index().sort_values(by='intensity', ascending=False)
st.dataframe(cluster_summary)

# Interpretasi zona berdasarkan rata-rata intensity
st.markdown("""
**Interpretasi Zona:**  
- Cluster dengan nilai rata‑rata intensity tertinggi dianggap sebagai zona aktivitas tinggi.  
- Anda dapat melihat cluster dengan intensity yang lebih rendah sebagai zona aktivitas sedang atau rendah.
""")

# ===== Visualisasi Grafik Distribusi =====
st.subheader("Distribusi Intensity Berdasarkan Cluster")
fig, ax = plt.subplots(figsize=(8, 4))
sns.boxplot(x="cluster", y="intensity", data=filtered_df, palette="Set2", ax=ax)
ax.set_title("Boxplot Intensity per Cluster")
st.pyplot(fig)

# ===== Visualisasi Peta Interaktif dengan Folium =====
st.subheader("Peta Interaktif Hasil Clustering")

# Jika data menggunakan koordinat, tentukan titik tengah peta
if filtered_df.shape[0] > 0:
    map_center = [filtered_df['latitude'].mean(), filtered_df['longitude'].mean()]
else:
    map_center = [0, 0]

m = folium.Map(location=map_center, zoom_start=8)

# Definisikan palet warna (sesuaikan jika jumlah cluster lebih dari 5)
colors = ['red', 'blue', 'green', 'purple', 'orange']

for idx, row in filtered_df.iterrows():
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=5,
        color=colors[int(row['cluster']) % len(colors)],
        fill=True,
        fill_color=colors[int(row['cluster']) % len(colors)],
        fill_opacity=0.7,
        popup=(
            f"<b>Kapal:</b> {row['kapal_id']}<br>"
            f"<b>Intensity:</b> {row['intensity']}<br>"
            f"<b>Jenis Operasi:</b> {row['jenis_operasi']}<br>"
            f"<b>Cluster:</b> {row['cluster']}"
        )
    ).add_to(m)

# Tampilkan peta menggunakan streamlit_folium
st_data = st_folium(m, width=700, height=500)

# ===== Legenda Sederhana =====
st.markdown("### Legenda Cluster")
legend_data = {
    "Zona Aktivitas Tinggi": colors[ cluster_summary.iloc[0]["cluster"] ] if not cluster_summary.empty else "N/A",
    "Zona Aktivitas Sedang": colors[ cluster_summary.iloc[1]["cluster"] ] if cluster_summary.shape[0] > 1 else "N/A",
    "Zona Aktivitas Rendah": colors[ cluster_summary.iloc[-1]["cluster"] ] if cluster_summary.shape[0] > 0 else "N/A"
}
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"<span style='color:{legend_data['Zona Aktivitas Tinggi']};font-size:25px'>&#9679;</span> **Zona Tinggi**", unsafe_allow_html=True)
with col2:
    st.markdown(f"<span style='color:{legend_data['Zona Aktivitas Sedang']};font-size:25px'>&#9679;</span> **Zona Sedang**", unsafe_allow_html=True)
with col3:
    st.markdown(f"<span style='color:{legend_data['Zona Aktivitas Rendah']};font-size:25px'>&#9679;</span> **Zona Rendah**", unsafe_allow_html=True)