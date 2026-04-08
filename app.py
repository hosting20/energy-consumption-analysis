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
    
    # حذف أي قيم مفقودة في datetime أو الطاقة
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
    df = df.dropna(subset=['datetime', 'Global_active_power'])
    
    # التأكد من فهرس datetimeIndex مرتب
    df = df.set_index('datetime')
    df = df.sort_index()
    
    return df

df = load_data()

if not df.empty:
    # عرض نطاق التواريخ الفعلي
    st.write("أقدم تاريخ في البيانات:", df.index.min().date())
    st.write("أحدث تاريخ في البيانات:", df.index.max().date())

    # Sidebar Filters
    st.sidebar.header("Filters")
    date_range = st.sidebar.date_input(
        "Select Date Range",
        [df.index.min().date(), df.index.max().date()]
    )

    # تحويل Sidebar إلى datetime
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

    # فلترة آمنة باستخدام Boolean mask
    mask = (df.index >= start_date) & (df.index <= end_date)
    filtered_df = df.loc[mask]

    if filtered_df.empty:
        st.warning("لا توجد بيانات ضمن النطاق المختار! سيتم عرض كامل البيانات.")
        filtered_df = df.copy()

    # Line Chart
    st.subheader("📈 Energy Consumption Over Time")
    st.line_chart(filtered_df['Global_active_power'])

# Daily Average
st.subheader("📊 Daily Average Consumption")
numeric_df = filtered_df.select_dtypes(include='number')
daily = numeric_df.resample('D').mean()
st.line_chart(daily['Global_active_power'])

# Hourly Peak
st.subheader("🔥 Peak Hours Analysis")
filtered_df['hour'] = filtered_df.index.hour
hourly_avg = filtered_df.groupby('hour')['Global_active_power'].mean()

    # Key Stats
    st.subheader("📌 Key Statistics")
    st.write("Average Consumption:", filtered_df['Global_active_power'].mean())
    st.write("Max Consumption:", filtered_df['Global_active_power'].max())
    st.write("Min Consumption:", filtered_df['Global_active_power'].min())

else:
    st.warning("البيانات غير موجودة أو لم يتم تحميلها بنجاح.")
