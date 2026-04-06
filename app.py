import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("⚡ Energy Consumption Dashboard")

@st.cache_data
def load_data():
    # اقرأ الملف الصغير
    df = pd.read_csv("energy_sample.csv")
    
    # دمج أعمدة Date و Time (إن وجدت) لإنشاء datetime
    if 'datetime' not in df.columns:
        if 'Date' in df.columns and 'Time' in df.columns:
            df['datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], errors='coerce')
        else:
            st.error("لا يوجد أعمدة Date/Time لإنشاء datetime!")
            return pd.DataFrame()  # جدول فارغ لتجنب crash
    
    # تحويل العمود الرئيسي للطاقة
    df['Global_active_power'] = pd.to_numeric(df['Global_active_power'], errors='coerce')
    
    # حذف أي قيم مفقودة
    df = df.dropna(subset=['datetime', 'Global_active_power'])
    
    # جعل datetime هو الفهرس
    df.set_index('datetime', inplace=True)
    
    return df

df = load_data()

if not df.empty:
    # Sidebar Filters
    st.sidebar.header("Filters")
    date_range = st.sidebar.date_input(
        "Select Date Range",
        [df.index.min().date(), df.index.max().date()]
    )
    filtered_df = df.loc[str(date_range[0]):str(date_range[1])]

    # Line Chart
    st.subheader("📈 Energy Consumption Over Time")
    st.line_chart(filtered_df['Global_active_power'])

    # Daily Average
    st.subheader("📊 Daily Average Consumption")
    daily = filtered_df.resample('D').mean()
    st.line_chart(daily['Global_active_power'])

    # Hourly Peak
    st.subheader("🔥 Peak Hours Analysis")
    filtered_df['hour'] = filtered_df.index.hour
    hourly_avg = filtered_df.groupby('hour')['Global_active_power'].mean()
    fig, ax = plt.subplots()
    ax.plot(hourly_avg.index, hourly_avg.values, marker='o')
    ax.set_title("Consumption by Hour")
    ax.set_xlabel("Hour")
    ax.set_ylabel("Power (kW)")
    st.pyplot(fig)

    # Key Stats
    st.subheader("📌 Key Statistics")
    st.write("Average Consumption:", filtered_df['Global_active_power'].mean())
    st.write("Max Consumption:", filtered_df['Global_active_power'].max())
    st.write("Min Consumption:", filtered_df['Global_active_power'].min())
else:
    st.warning("البيانات غير موجودة أو لم يتم تحميلها بنجاح.")
