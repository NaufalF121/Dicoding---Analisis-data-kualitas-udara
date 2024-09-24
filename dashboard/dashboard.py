import streamlit as st
import folium
import pandas as pd
from streamlit_folium import st_folium
import matplotlib.pyplot as plt

data = pd.read_csv("./dashboard/main_data.csv")

wind_directions = {
    'N': 0,
    'NNE': 22.5,
    'NE': 45,
    'ENE': 67.5,
    'E': 90,
    'ESE': 112.5,
    'SE': 135,
    'SSE': 157.5,
    'S': 180,
    'SSW': 202.5,
    'SW': 225,
    'WSW': 247.5,
    'W': 270,
    'WNW': 292.5,
    'NW': 315,
    'NNW': 337.5,
    'N': 360
}

# Sidebar
st.sidebar.title("Menu")
page = st.sidebar.selectbox("Pilih halaman", ["Peta sebaran stasiun", "Visualisasi Konsentrasi PM2.5", "Detail Informasi Stasiun"])

if page == "Peta sebaran stasiun":
    station_coords = {
        'Aotizhongxin': [41.749431, 123.534706],
        'Changping': [23.169276, 113.472297],
        'Dingling': [40.28901087962015, 116.22820454435723],
        'Dongsi': [39.919777385684995, 116.4175980582735],
        'Guanyuan': [39.93566504856561, 116.36091220694566],
        'Gucheng': [39.90750287654859, 116.20523143821556],
        'Huairou': [40.28010674366511, 116.70020509174464],
        'Nongzhanguan': [39.93366451803525, 116.46750481009873],
        'Shunyi': [40.13038897356548, 116.65058656480477],
        'Tiantan': [39.11564446598443, 117.15803926397433],
        'Wanliu': [39.99762499454515, 116.25763437810566],
        'Wanshouxigong': [39.90605105134053, 116.26267364841948]
    }

    m = folium.Map(location=[39.9042, 116.4074], zoom_start=10)

    for station, coords in station_coords.items():
        folium.Marker(location=coords, popup=station, icon=folium.Icon(color='blue', icon='info-sign')).add_to(m)

    st.title("Peta Lokasi Stasiun")
    st_folium(m, width=700, height=500)

elif page == "Visualisasi Konsentrasi PM2.5":
    st.title("Visualisasi Konsentrasi PM2.5 pada tiap Stasiun")

    # Select station
    station = st.selectbox("Pilih Stasiun", data['station'].unique())

    # Filter data by station
    station_data = data[data['station'] == station]

    # Ensure 'time' column is in datetime format
    station_data['time'] = pd.to_datetime(station_data['time'])

    # Resample data by month and calculate the mean for numeric columns only
    numeric_columns = station_data.select_dtypes(include='number').columns
    monthly_data = station_data.resample('ME', on='time')[numeric_columns].mean().reset_index()

    # Select time range by month
    min_time = monthly_data['time'].min()
    max_time = monthly_data['time'].max()
    min_month = min_time.to_period('M').start_time
    max_month = max_time.to_period('M').start_time
    time_range = st.slider("Pilih Rentang Waktu", min_value=min_month.to_pydatetime(), 
                           max_value=max_month.to_pydatetime(), 
                           value=(min_month.to_pydatetime(), max_month.to_pydatetime()), 
                           format="MMM YYYY")

    # Filter data by time range
    filtered_data = monthly_data[(monthly_data['time'] >= time_range[0]) & 
                                 (monthly_data['time'] <= time_range[1])]

    # Plot data
    fig, ax = plt.subplots()
    ax.plot(filtered_data['time'].dt.strftime('%b %Y'), filtered_data['PM2.5'], marker='o')
    ax.set_xlabel('Time')
    ax.set_ylabel('Value')
    ax.set_title(f'Konsentrasi PM2.5 pada {station}')
    plt.xticks(rotation=45)

    st.pyplot(fig)

elif page == "Detail Informasi Stasiun":
    st.title("Detail Informasi Stasiun")

    # Select station
    station = st.selectbox("Pilih Stasiun", data['station'].unique())

    # Ensure 'time' column is in datetime format
    data['time'] = pd.to_datetime(data['time'])

    # Select date
    date = st.date_input("Pilih Tanggal", value=pd.to_datetime("2013-03-01"))

    # Select hour
    hour = st.slider("Pilih Jam", min_value=0, max_value=23, value=12)

    # Filter data by station, date, and hour
    data['date_str'] = data['time'].dt.strftime('%Y-%m-%d')
    data['hour'] = data['time'].dt.hour
    detail_data = data[(data['station'] == station) & 
                       (data['date_str'] == date.strftime('%Y-%m-%d')) & 
                       (data['hour'] == hour)]
    WND = detail_data['wd'].values[0]

    if not detail_data.empty:
        st.write(f"Detail informasi untuk stasiun {station} pada tanggal {date.strftime('%Y-%m-%d')} jam {hour}:00: dengan arah angin {WND}")

        # Get the previous hour's data for comparison
        prev_time = pd.to_datetime(f"{date.strftime('%Y-%m-%d')} {hour}:00") - pd.Timedelta(hours=1)
        prev_data = data[(data['station'] == station) & 
                         (data['time'] == prev_time)]

        col1, col2 = st.columns(2)
        for i, col in enumerate(detail_data.columns):
            if col not in ['station', 'time', 'date_str', 'year', 'hour', 'month', 'day']:
                
                value = detail_data[col].values[0]
                if pd.api.types.is_numeric_dtype(detail_data[col]):
                    if not prev_data.empty:
                        prev_value = prev_data[col].values[0]
                        if value:
                            delta = ((value - prev_value)/prev_value * 100) 
                            if (value - prev_value) > 0:
                                
                                delta = f"{delta:.2f}%"
                                delta_color = "normal"
                            else:
                                
                                delta = f"{delta:.2f}%"
                                delta_color = "normal"
                        else:
                            delta = "0.00"
                            delta_color = "off"
                    else:
                        delta = "N/A"
                        delta_color = "off"
                    if i % 2 == 0:
                        col1.metric(label=col, value=f"{value:.2f}", delta=delta, delta_color=delta_color)
                    else:
                        col2.metric(label=col, value=f"{value:.2f}", delta=delta, delta_color=delta_color)
        col1.metric(label="Arah Angin", value=f"{wind_directions[WND]}°", delta="N/A", delta_color="off")

    else:
        st.write(f"Tidak ada data untuk stasiun {station} pada tanggal {date.strftime('%Y-%m-%d')} jam {hour}:00.")