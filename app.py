import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Energy Dashboard", layout="wide")

st.title("⚡ Energy Consumption Dashboard")

@st.cache_data
def load_data():
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00235/household_power_consumption.txt"
    df = pd.read_csv(url, sep=';', low_memory=False)

    df = df.sample(20000, random_state=42)

    df['datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], errors='coerce')
    df['Global_active_power'] = pd.to_numeric(df['Global_active_power'], errors='coerce')

    df = df.dropna(subset=['datetime', 'Global_active_power'])
    df.set_index('datetime', inplace=True)

    return df

df = load_data()

# Sidebar
st.sidebar.header("📅 Filter")

date_range = st.sidebar.date_input(
    "Select Date Range",
    [df.index.min(), df.index.max()]
)

filtered_df = df.loc[str(date_range[0]):str(date_range[1])]

# Charts
st.subheader("📈 Energy Consumption")
st.line_chart(filtered_df['Global_active_power'])

st.subheader("📊 Daily Consumption")
daily = filtered_df.resample('D').mean()
st.line_chart(daily['Global_active_power'])

st.subheader("🔥 Peak Hours")

filtered_df['hour'] = filtered_df.index.hour
hourly = filtered_df.groupby('hour')['Global_active_power'].mean()

fig, ax = plt.subplots()
ax.plot(hourly.index, hourly.values)

st.pyplot(fig)

# Metrics
st.subheader("📌 Key Metrics")

col1, col2, col3 = st.columns(3)

col1.metric("Average", round(filtered_df['Global_active_power'].mean(), 2))
col2.metric("Max", round(filtered_df['Global_active_power'].max(), 2))
col3.metric("Min", round(filtered_df['Global_active_power'].min(), 2))
