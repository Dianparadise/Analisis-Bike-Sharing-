import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

#LOAD DATA
@st.cache_data
def load_data():
    df_day = pd.read_csv("submission/dashboard/day_clean.csv")
    df_hour = pd.read_csv("submission/dashboard/hour_clean.csv")
    return df_day,df_hour
df_day,df_hour = load_data()

df_filter = df_day.copy()
df_hour_filter = df_hour.copy()

#JUDUL
st.title("Dashboard Stok Penyewaan Sepeda")

#SIDEBAR
st.sidebar.title("Filter Dashboard")

st.sidebar.header("Filter Tahun")
pilihan_tahun = st.sidebar.selectbox(
    "Pilihan Tahun:",
    ["semua tahun", 2011, 2012],
    
)

st.write(f"Tahun yang dipilih adalah: **{pilihan_tahun}**")

st.sidebar.header("Pilihan Hari")
hari= ['Semua','Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
Pilihan_hari = st.sidebar.multiselect(
    "Pilih Hari untuk Dibandingkan:",
    options=hari,
    default=['Semua'] 
)

#FILTER
if "Semua" not in Pilihan_hari :
    df_hour_filter = df_hour_filter[
        df_hour_filter["weekday"].isin(Pilihan_hari)
    ]


if pilihan_tahun == 2011:
    df_filter = df_filter[df_filter["yr"] == 2011]
    df_hour_filter = df_hour_filter[df_hour_filter["yr"] == 2011]
elif pilihan_tahun == 2012:
     df_filter = df_filter[df_filter["yr"] == 2012]
     df_hour_filter = df_hour_filter[df_hour_filter["yr"] == 2012]
else:
    df_filter = df_filter
    df_hour_filter = df_hour_filter

# st.dataframe(df_filter)

df_stok = (
    df_filter.groupby("season")["cnt"]
    .agg(
        q1=lambda x: x.quantile(0.25),
        mean="mean",
        q3=lambda x: x.quantile(0.75),
        
    )
    .reset_index()
)

col1, col2, col3 = st.columns(3)
with col1:
    total_unit = df_filter["cnt"].sum()
    st.metric("Total Penyewaan", f"{total_unit:,} Unit")

with col2:
    rata_harian = df_filter["cnt"].mean()
    st.metric("Rata-rata Harian", f"{rata_harian:.0f} Unit")

with col3:
    # Cari nama musim yang punya nilai Q3 tertinggi
    musim_puncak = df_stok.sort_values(by="q3", ascending=False).iloc[0][
        "season"
    ]
    st.metric("Musim Permintaan Tertinggi", musim_puncak)

st.divider()  

st.title("GRAFIK BATAS PENYEWAAN SEPEDA")

df_gabungan = df_stok.melt(
    id_vars=['season'],
    value_vars=['q1', 'q3'],
    var_name="Jenis_Batas",
    value_name="Jumlah_Unit"
)

fig, ax = plt.subplots(figsize=(8,4))
sns.barplot(
    data = df_gabungan,
    x="season",
    y="Jumlah_Unit",
    hue="Jenis_Batas",
    ax=ax
)
ax.set_title(f"Grafik Batasan Berdasarkan Tahun: {pilihan_tahun}")
ax.set_xlabel("Musim")
ax.set_ylabel("Jumlah Penyewaan")
ax.grid(True, linestyle="--", alpha=0.3, axis="y")
st.pyplot(fig)
st.subheader("Tabel Detail Ambang Batas Stok")
st.dataframe(df_stok, use_container_width=True)

st.divider()  




# st.dataframe(df_hour_filter)

df_pivot = (
        df_hour_filter.groupby(["weekday", "hr"])["cnt"].mean().unstack()
    )
df_pivot = df_pivot.reindex([h for h in hari if h in df_pivot.index])
fig2, ax2 = plt.subplots(figsize=(12, 5))
sns.heatmap(
        df_pivot,
        cmap="YlOrRd",  
        annot=False,  # biar angka gk muncul
        cbar_kws={"label": "Rata-rata Sepeda Tersewa / Jam"},
        ax=ax2,
    )

    
ax2.set_title(
        "Intensitas Lonjakan Penyewaan per Jam (Hari vs Jam)",
        fontsize=12,
        pad=15,
        fontweight="bold",
    )
ax2.set_xlabel("Jam (00.00 - 23.00)", fontsize=10)
ax2.set_ylabel("Hari", fontsize=10)

st.title("Grafik Heatmap Penyewaan per Jam berdasarkan hari")
st.write(f"Hari yang dipilih adalah: **{Pilihan_hari}**")
st.pyplot(fig2)