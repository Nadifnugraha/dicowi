import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
file_path = "all_dfs.pkl"
data = pd.read_pickle(file_path)

order_items_df = data["order_items_df"]
order_payments_df = data["order_payments_df"]
products_df = data["products_df"]
orders_df = data["orders_df"]
customers_df = data["customers_df"]

order_items_df = order_items_df.merge(products_df[['product_id', 'product_category_name']], on='product_id', how='left')
order_items_df = order_items_df.merge(orders_df[['order_id', 'customer_id']], on='order_id', how='left')
order_items_df = order_items_df.merge(customers_df[['customer_id', 'customer_zip_code_prefix']], on='customer_id', how='left')
order_items_df["shipping_limit_date"] = pd.to_datetime(order_items_df["shipping_limit_date"])

order_payments_df = order_payments_df.merge(order_items_df[['order_id', 'shipping_limit_date', 'product_category_name']], on='order_id', how='left')

# Define seasons
def get_season(date):
    month = date.month
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    else:
        return "Fall"

order_items_df["season"] = order_items_df["shipping_limit_date"].apply(get_season)
order_payments_df["season"] = order_payments_df["shipping_limit_date"].apply(get_season)

st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")

st.sidebar.image("logo.png", width=150)
st.sidebar.title("Filters")

# Filter by Season
selected_season = st.sidebar.selectbox("Select Season", ["All", "Winter", "Spring", "Summer", "Fall"])

# Filter by Product Category
selected_category = st.sidebar.selectbox("Select Product Category", ["All"] + sorted(order_items_df["product_category_name"].dropna().unique().tolist()))

if selected_season != "All":
    filtered_orders = order_items_df[order_items_df['season'] == selected_season]
else:
    filtered_orders = order_items_df

filtered_payments = order_payments_df.copy()
if selected_season != "All":
    filtered_payments = filtered_payments[filtered_payments['season'] == selected_season]

if selected_category != "All":
    filtered_payments = filtered_payments[filtered_payments["product_category_name"] == selected_category]

st.title("E-Commerce Dashboard")
st.markdown("---")

st.header("Top 10 Best Selling Products")
if not filtered_orders.empty:
    product_sales = filtered_orders.groupby("product_id").agg({"order_id": "count"}).reset_index()
    product_sales = product_sales.merge(products_df, on="product_id", how="left")
    top_10_best = product_sales.sort_values(by="order_id", ascending=False).head(10)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(y=top_10_best["product_category_name"], x=top_10_best["order_id"], palette="Greens", errorbar=None)
    ax.set_title("Top 10 Best Selling Products")
    ax.set_xlabel("Units Sold")
    ax.set_ylabel("Product Category")
    st.pyplot(fig)
else:
    st.warning("No data available for the selected season.")

st.header("Top 10 Least Selling Products")
if not filtered_orders.empty:
    product_sales_least = filtered_orders.groupby("product_id").agg({"order_item_id": "count"}).reset_index()
    product_sales_least = product_sales_least.merge(products_df, on="product_id", how="left")
    top_10_least = product_sales_least.sort_values(by="order_item_id", ascending=True).head(10)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(y=top_10_least["product_category_name"], x=top_10_least["order_item_id"], palette="Reds", errorbar=None)
    ax.set_title("Top 10 Least Selling Products")
    ax.set_xlabel("Units Sold")
    ax.set_ylabel("Product Category")
    st.pyplot(fig)
else:
    st.warning("No data available for the selected season.")

st.header("Payment Methods Distribution")
if not filtered_payments.empty:
    payment_counts = filtered_payments["payment_type"].value_counts()
    payment_counts = payment_counts[(payment_counts > 0) & (payment_counts.index != "not_defined")]
    
    fig, ax = plt.subplots(figsize=(8, 8))
    colors = ["#1E3A8A", "#3B82F6", "#60A5FA", "#93C5FD", "#BFDBFE"]
    wedges, _, autotexts = ax.pie(payment_counts.values, autopct=lambda p: f'{p:.1f}%' if p > 1 else '', colors=colors, startangle=140, wedgeprops={'edgecolor': 'white', 'linewidth': 2})
    
    for text in autotexts:
        text.set_fontsize(12)
    
    centre_circle = plt.Circle((0,0),0.70,fc='white')
    fig.gca().add_artist(centre_circle)
    
    ax.set_title("Payment Methods Distribution")
    st.pyplot(fig)
    
    legend_labels = "".join([f"<div style='display: flex; align-items: center;'><span style='width: 12px; height: 12px; background-color:{colors[i]}; display: inline-block; margin-right: 5px;'></span>{ptype}: {pcount} ({pcount / payment_counts.sum() * 100:.1f}%)</div>" for i, (ptype, pcount) in enumerate(zip(payment_counts.index, payment_counts.values))])
    
    st.markdown(f"<div style='text-align: center;'>{legend_labels}</div>", unsafe_allow_html=True)
else:
    st.warning("No payment data available for the selected filters.")

st.header("Customer Distribution by Zip Code (Top 10)")
filtered_customers = order_items_df.copy()

if selected_season != "All":
    filtered_customers = filtered_customers[filtered_customers['season'] == selected_season]

if selected_category != "All":
    filtered_customers = filtered_customers[filtered_customers["product_category_name"] == selected_category]

if not filtered_customers.empty:
    customer_distribution = filtered_customers.groupby("customer_zip_code_prefix").size().reset_index(name="customer_count")
    top_10_zipcodes = customer_distribution.sort_values(by="customer_count", ascending=False).head(10)

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=top_10_zipcodes["customer_zip_code_prefix"].astype(str), y=top_10_zipcodes["customer_count"], palette="coolwarm")
    ax.set_title("Customer Distribution by Zip Code (Top 10)")
    ax.set_xlabel("Zip Code")
    ax.set_ylabel("Number of Customers")
    plt.xticks(rotation=45)
    st.pyplot(fig)
else:
    st.warning("No customer data available for the selected filters.")