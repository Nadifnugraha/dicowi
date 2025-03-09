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
customers_df = data["customers_df"]
products_df = data["products_df"]

# Merge product data
product_sales = order_items_df.groupby("product_id").size().reset_index(name="count")
product_sales = product_sales.merge(products_df, on="product_id", how="left")

# Most and least popular products
most_popular = product_sales.nlargest(10, "count")
least_popular = product_sales.nsmallest(10, "count")

# Payment methods
payment_counts = order_payments_df["payment_type"].value_counts()

# Customer distribution by Zip Code
customer_distribution = customers_df["customer_zip_code_prefix"].value_counts().nlargest(10)

# Streamlit app
st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")

# Sidebar Navigation
st.sidebar.image("logo.png", width=150)
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to", ["Overview", "Sales Analysis", "Payment Methods", "Customer Distribution"])

st.title("📊 E-Commerce Dashboard")
st.markdown("---")

if menu == "Overview":
    st.header("📊 Overview of E-Commerce Data")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Orders", order_items_df.shape[0])
    col2.metric("Unique Products", products_df['product_id'].nunique())
    col3.metric("Total Revenue", f"${order_items_df['price'].sum():,.2f}")
    
    st.subheader("Data Summary")
    st.write(order_items_df.describe())

elif menu == "Sales Analysis":
    st.header("📈 Sales Analysis")
    fig, ax = plt.subplots(1, 2, figsize=(18, 6), gridspec_kw={'wspace': 0.4})
    
    # Best-Selling Products
    sns.barplot(y=most_popular["product_category_name"], x=most_popular["count"], ax=ax[0], palette="Blues")
    ax[0].set_title("Top 10 Best-Selling Products")
    ax[0].set_xlabel("Total Sold")
    ax[0].set_ylabel("Product Category")
    
    # Least-Selling Products
    sns.barplot(y=least_popular["product_category_name"], x=least_popular["count"], ax=ax[1], palette="Reds")
    ax[1].set_title("Top 10 Least-Selling Products")
    ax[1].set_xlabel("Total Sold")
    ax[1].set_ylabel("Product Category")
    
    st.pyplot(fig)

elif menu == "Payment Methods":
    st.header("💳 Payment Methods Distribution")
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = sns.color_palette("Blues", len(payment_counts))
    wedges, _, autotexts = ax.pie(
        payment_counts.values, labels=None, 
        autopct=lambda p: f'{p:.1f}%' if p > 0.1 else '', 
        colors=colors, startangle=140, wedgeprops={'edgecolor': 'white'}
    )
    plt.setp(autotexts, size=10, weight="bold", color="white")
    ax.set_title("Most Frequently Used Payment Methods")
    ax.legend(payment_counts.index, title="Payment Methods", loc="lower center", bbox_to_anchor=(0.5, -0.1), ncol=2)
    st.pyplot(fig)

elif menu == "Customer Distribution":
    st.header("🌍 Customer Distribution by Zip Code")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x=customer_distribution.index, y=customer_distribution.values, palette="coolwarm")
    ax.set_title("Customer Distribution by Zip Code (Top 10)")
    ax.set_xlabel("Zip Code")
    ax.set_ylabel("Number of Customers")
    st.pyplot(fig)

st.sidebar.info("Developed by Your Name")
