import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(
    page_title="AdvoInsight Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AdvoInsight Dashboard")
st.caption("Dashboard analisis pengaduan mahasiswa")

@st.cache_data
def create_data():
    rng = np.random.default_rng(42)
    n = 250

    categories = [
        "Akademik", "Fasilitas", "Dosen",
        "UKT", "Kemahasiswaan", "Lainnya"
    ]
    statuses = [
        "Menunggu Ditinjau",
        "Sedang Diproses",
        "Selesai"
    ]

    return pd.DataFrame({
        "ID Aduan": [f"AD-{i:04d}" for i in range(1, n + 1)],
        "Tanggal": pd.to_datetime(
            rng.choice(
                pd.date_range("2026-01-01", "2026-10-01"),
                n
            )
        ),
        "Kategori": rng.choice(categories, n),
        "Status": rng.choice(
            statuses, n, p=[0.4, 0.35, 0.25]
        ),
        "Prioritas": rng.choice(
            ["Rendah", "Sedang", "Tinggi"], n
        )
    })

df = create_data()

st.sidebar.header("Filter Data")
kategori = st.sidebar.multiselect(
    "Kategori",
    sorted(df["Kategori"].unique()),
    default=sorted(df["Kategori"].unique())
)
status = st.sidebar.multiselect(
    "Status",
    sorted(df["Status"].unique()),
    default=sorted(df["Status"].unique())
)

tanggal = st.sidebar.date_input(
    "Rentang tanggal",
    value=(df["Tanggal"].min().date(),
           df["Tanggal"].max().date())
)

filtered = df[
    df["Kategori"].isin(kategori)
    & df["Status"].isin(status)
].copy()

if isinstance(tanggal, (tuple, list)) and len(tanggal) == 2:
    filtered = filtered[
        filtered["Tanggal"].dt.date.between(
            tanggal[0], tanggal[1]
        )
    ]

col1, col2, col3 = st.columns(3)
col1.metric("Total Aduan", len(filtered))
col2.metric(
    "Belum Selesai",
    filtered["Status"].ne("Selesai").sum()
)
col3.metric(
    "Prioritas Tinggi",
    filtered["Prioritas"].eq("Tinggi").sum()
)

st.divider()

if filtered.empty:
    st.info("Tidak ada data untuk filter yang dipilih.")
else:
    kiri, kanan = st.columns(2)

    with kiri:
        st.subheader("Aduan per Kategori")
        chart = filtered["Kategori"].value_counts().rename_axis(
            "Kategori"
        ).reset_index(name="Jumlah")
        st.plotly_chart(
            px.bar(chart, x="Kategori", y="Jumlah",
                   color="Kategori"),
            use_container_width=True
        )

    with kanan:
        st.subheader("Status Pengaduan")
        chart_status = filtered["Status"].value_counts().rename_axis(
            "Status"
        ).reset_index(name="Jumlah")
        st.plotly_chart(
            px.pie(chart_status, names="Status",
                   values="Jumlah", hole=0.4),
            use_container_width=True
        )

    st.subheader("Tren Pengaduan Bulanan")
    bulanan = (
        filtered.assign(
            Bulan=filtered["Tanggal"].dt.to_period("M").astype(str)
        )
        .groupby("Bulan")
        .size()
        .reset_index(name="Jumlah")
    )
    st.plotly_chart(
        px.line(bulanan, x="Bulan", y="Jumlah",
                markers=True),
        use_container_width=True
    )

st.subheader("Data Pengaduan")
st.dataframe(filtered, use_container_width=True)

st.download_button(
    "⬇️ Unduh Data CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="data_pengaduan.csv",
    mime="text/csv"
)

st.caption("Data demonstrasi sintetis — bukan data asli.")
