import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

# Dataset
datetime_cols = ["order_approved_at", "order_purchase_timestamp"]
all_df = pd.read_csv("./data/all_data.csv")

# Convert datetime columns to datetime type
for col in datetime_cols:
    if col in all_df.columns:
        all_df[col] = pd.to_datetime(all_df[col])

# Sort dataset and reset index
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(drop=True, inplace=True)

# Filter untuk ulasan pelanggan (order_reviews_df)
if 'review_score' in all_df.columns:
    order_reviews_df = all_df[['review_score']].dropna()
else:
    order_reviews_df = pd.DataFrame(columns=['review_score'])

# Data preparation for daily orders
daily_orders_df = all_df.groupby(all_df["order_approved_at"].dt.date).agg(
    order_count=("order_id", "count"),
    revenue=("payment_value", "sum")
).reset_index()
daily_orders_df.rename(columns={"order_approved_at": "date"}, inplace=True)

# Visualisasi sebaran ulasan pelanggan
def plot_review_ratings():
    if order_reviews_df.empty:
        st.warning("Data ulasan pelanggan tidak tersedia!")
        return
    plt.figure(figsize=(10, 6))
    sns.countplot(data=order_reviews_df, x='review_score', palette='viridis')
    plt.title('Sebaran Ulasan Pelanggan Berdasarkan Rating')
    plt.xlabel('Rating Ulasan')
    plt.ylabel('Jumlah Ulasan')
    st.pyplot()

# Visualisasi daily orders
def plot_daily_orders():
    if daily_orders_df.empty:
        st.warning("Data harian tidak tersedia!")
        return
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=daily_orders_df, x='date', y='order_count', marker='o', label='Orders')
    plt.title('Daily Orders')
    plt.xlabel('Tanggal')
    plt.ylabel('Jumlah Order')
    plt.legend(title='Legend')
    plt.xticks(rotation=45, ha='right')
    st.pyplot()

# Streamlit Layout
def main():
    st.title('Dashboard E-Commerce Analysis')

    st.sidebar.header('Pilih Visualisasi')
    options = ['Sebaran Ulasan Pelanggan', 'Daily Orders and Revenue']
    selected_option = st.sidebar.selectbox('Pilih topik visualisasi:', options)

    if selected_option == 'Sebaran Ulasan Pelanggan':
        st.subheader('Sebaran Ulasan Pelanggan Berdasarkan Rating')
        plot_review_ratings()
    elif selected_option == 'Daily Orders and Revenue':
        st.subheader('Jumlah Order Harian dan Revenue')
        plot_daily_orders()

    # Menambahkan informasi berdasarkan input waktu
    st.sidebar.header('Filter Waktu')
    start_date = st.sidebar.date_input(
        'Tanggal Mulai',
        value=pd.to_datetime(daily_orders_df['date'].min())
    )
    end_date = st.sidebar.date_input(
        'Tanggal Akhir',
        value=pd.to_datetime(daily_orders_df['date'].max())
    )

    # Metrics berdasarkan filter waktu
    if st.sidebar.button('Hitung Metrics'):
        filtered_data = daily_orders_df[
            (daily_orders_df['date'] >= start_date) & 
            (daily_orders_df['date'] <= end_date)
        ]
        total_orders = filtered_data['order_count'].sum()
        total_revenue = filtered_data['revenue'].sum()
        st.write(f"Total Order dari {start_date} hingga {end_date}: **{total_orders}**")
        st.write(f"Total Revenue dari {start_date} hingga {end_date}: **Rp {total_revenue:,.2f}**")
    st.caption('Copyright (C) Fadilla. 2024')

# Jalankan aplikasi
if __name__ == "__main__":
    main()
