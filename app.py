import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("⚡ Energy Consumption Dashboard")

@st.cache_data
def load_data():
    df = pd.read_csv("energy_sample.csv")
    
    # إنشاء datetime إذا لم يكن موجود
    if 'datetime' not in df.columns:
        if 'Date' in df.columns and 'Time' in df.columns:
            df['datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], errors='coerce')
        else:
            st.error("لا يوجد أعمدة Date/Time لإنشاء datetime!")
            return pd.DataFrame()
    
    # تحويل الطاقة إلى رقمي
    df['Global_active_power'] = pd.to_numeric(df['Global_active_power'], errors='coerce')
    
    # حذف أي قيم مفقودة
    df = df.dropna(subset=['datetime', 'Global_active_power'])
    
    # تأكد أن الفهرس DatetimeIndex
    df = df.set_index('datetime')
    df.index = pd.to_datetime(df.index)  # تحويل الفهرس لأي حالة غير صحيحة
    
    return df

df = load_data()

if not df.empty:
    st.sidebar.header("Filters")
    
    # Sidebar date_input
    date_range = st.sidebar.date_input(
        "Select Date Range",
        [df.index.min().date(), df.index.max().date()]
    )
    
    # تحويل start و end إلى datetime
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    
    # --- فلترة آمنة باستخدام try-except ---
    try:
        filtered_df = df.loc[start_date:end_date]
        if filtered_df.empty:
            st.warning("لا توجد بيانات ضمن النطاق المختار!")
        else:
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

    except KeyError:
        st.error("حدث خطأ أثناء فلترة البيانات، يرجى التأكد من أن التواريخ ضمن نطاق البيانات.")

else:
    st.warning("البيانات غير موجودة أو لم يتم تحميلها بنجاح.")
