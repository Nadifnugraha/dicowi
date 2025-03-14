import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
file_path = "all_dfs.pkl"
data = pd.read_pickle(file_path)

# Extract relevant DataFrames
order_items_df = data["order_items_df"]
order_payments_df = data["order_payments_df"]
products_df = data["products_df"]

# Convert dates to datetime format
order_items_df["shipping_limit_date"] = pd.to_datetime(order_items_df["shipping_limit_date"])
order_payments_df = order_payments_df.merge(order_items_df[['order_id', 'shipping_limit_date']], on='order_id', how='left')

# Filter out empty months
excluded_dates = {"2020-04", "2020-02", "2016-09", "2016-12"}
date_counts = order_items_df['shipping_limit_date'].dt.to_period("M").value_counts()
available_dates = [date for date in date_counts[date_counts > 0].index.astype(str).tolist() if date not in excluded_dates]

# Streamlit app
st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")

# Sidebar
st.sidebar.image("logo.png", width=150)
st.sidebar.title("Filters")

# Select Month & Year
if available_dates:
    selected_date = st.sidebar.selectbox("Select Month & Year", sorted(available_dates, reverse=True))
    
    # Filter data based on selected month & year
    filtered_orders = order_items_df[order_items_df['shipping_limit_date'].dt.to_period("M").astype(str) == selected_date]
    filtered_payments = order_payments_df[order_payments_df['shipping_limit_date'].dt.to_period("M").astype(str) == selected_date]
else:
    filtered_orders = pd.DataFrame()
    filtered_payments = pd.DataFrame()
    st.sidebar.warning("No available data.")

st.title("📊 E-Commerce Dashboard")
st.markdown("---")

# Interactive Revenue Over Time
st.header("📊 Revenue Over Time")
if not filtered_orders.empty:
    revenue_over_time = filtered_orders.groupby(filtered_orders['shipping_limit_date'].dt.to_period("D")).agg({"price": "sum"}).reset_index()
    revenue_over_time['shipping_limit_date'] = revenue_over_time['shipping_limit_date'].astype(str)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(x=revenue_over_time['shipping_limit_date'], y=revenue_over_time['price'], marker='o', color='b')
    ax.set_title("Daily Revenue Trend for Selected Month")
    ax.set_xlabel("Date")
    ax.set_ylabel("Total Revenue")
    plt.xticks(rotation=45)
    st.pyplot(fig)
else:
    st.warning("No revenue data available for the selected month.")

# Interactive Sales by Category
st.header("📦 Sales by Category")
if not filtered_orders.empty:
    category_sales = filtered_orders.merge(products_df, on="product_id", how="left")
    category_summary = category_sales.groupby("product_category_name").agg({"price": "sum"}).reset_index()
    category_summary = category_summary.sort_values(by="price", ascending=False).head(15)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(y=category_summary["product_category_name"], x=category_summary["price"], palette="Blues")
    ax.set_title("Top 15 Sales by Product Category")
    ax.set_xlabel("Total Revenue")
    ax.set_ylabel("Product Category")
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig)
else:
    st.warning("No sales data available for the selected month.")

# Interactive Payment Distribution
st.header("💳 Payment Methods Distribution")
if not filtered_payments.empty:
    payment_counts = filtered_payments["payment_type"].value_counts()
    fig, ax = plt.subplots(figsize=(8, 8))
    colors = ["#1E3A8A", "#3B82F6", "#60A5FA", "#93C5FD", "#BFDBFE"]
    wedges, _, autotexts = ax.pie(payment_counts.values, autopct='%1.1f%%', colors=colors, startangle=140, wedgeprops= {'edgecolor': 'white', 'linewidth': 2})
    
    for text in autotexts:
        text.set_fontsize(12)
    
    # Convert to donut chart
    centre_circle = plt.Circle((0,0),0.70,fc='white')
    fig.gca().add_artist(centre_circle)
    
    ax.set_title("Payment Methods Distribution")
    st.pyplot(fig)
    
    # Display legend below chart
    legend_labels = "".join([f"<div style='display: flex; align-items: center;'><span style='width: 12px; height: 12px; background-color:{colors[i]}; display: inline-block; margin-right: 5px;'></span>{ptype}: {pcount} ({pcount / payment_counts.sum() * 100:.1f}%)</div>" for i, (ptype, pcount) in enumerate(zip(payment_counts.index, payment_counts.values))])
    
    st.markdown(f"<div style='text-align: center;'>{legend_labels}</div>", unsafe_allow_html=True)
else:
    st.warning("No payment data available for the selected month.")