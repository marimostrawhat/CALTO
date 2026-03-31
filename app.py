import streamlit as st
import pandas as pd
import numpy as np

st.title("⚡UPT Balikpapan Transmission Fault Locator⚡")

# =========================
# LOAD DATA (DARI GITHUB)
# =========================
df = pd.read_excel("tower_data.xlsx")

# Standardisasi nama kolom
df.columns = [col.strip().upper() for col in df.columns]

# =========================
# PILIH LINE
# =========================
lines = df["LINE"].unique()
selected_line = st.selectbox("Pilih Line", lines)

# Filter & sort
df_line = df[df["LINE"] == selected_line].sort_values("SEQUENCE").reset_index(drop=True)

# =========================
# INPUT JARAK GANGGUAN
# =========================
fault_distance = st.number_input("Jarak Gangguan (km)", min_value=0.0)

# =========================
# HAVERSINE FUNCTION
# =========================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c

# =========================
# PROSES HITUNG
# =========================
if st.button("Hitung"):

    # Hitung jarak antar tower
    distances = [0]
    for i in range(1, len(df_line)):
        d = haversine(
            df_line.loc[i-1, 'LATITUDE'], df_line.loc[i-1, 'LONGITUDE'],
            df_line.loc[i, 'LATITUDE'], df_line.loc[i, 'LONGITUDE']
        )
        distances.append(d)

    df_line['SEGMENT_KM'] = distances
    df_line['CUM_KM'] = df_line['SEGMENT_KM'].cumsum()

    # Cari posisi terdekat
    idx = (df_line['CUM_KM'] - fault_distance).abs().idxmin()

    st.subheader("⚡ Hasil")

    tower_now = df_line.loc[idx, 'TOWER']
    st.write(f"📍 Tower terdekat: **{tower_now}**")

    # =========================
    # SPAN INFO + KOORDINAT
    # =========================
    if idx < len(df_line)-1:
        tower_next = df_line.loc[idx+1, 'TOWER']
        st.write(f"🔗 Span: {tower_now} - {tower_next}")

        d1 = df_line.loc[idx, 'CUM_KM']
        d2 = df_line.loc[idx+1, 'CUM_KM']

        ratio = (fault_distance - d1) / (d2 - d1) if d2 != d1 else 0

        lat = df_line.loc[idx, 'LATITUDE'] + ratio * (
            df_line.loc[idx+1, 'LATITUDE'] - df_line.loc[idx, 'LATITUDE']
        )

        lon = df_line.loc[idx, 'LONGITUDE'] + ratio * (
            df_line.loc[idx+1, 'LONGITUDE'] - df_line.loc[idx, 'LONGITUDE']
        )

        st.write(f"🌍 Estimasi Koordinat: {lat:.6f}, {lon:.6f}")

    st.write(f"📏 Jarak kumulatif tower: {df_line.loc[idx, 'CUM_KM']:.2f} km")

    # =========================
    # TAMPILKAN DATA
    # =========================
    with st.expander("Lihat Data"):
        st.dataframe(df_line)
