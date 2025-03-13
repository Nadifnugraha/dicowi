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
product_sales = order_items_df.groupby("product_id").agg({"price": "sum", "order_id": "count"}).reset_index()
product_sales.rename(columns={"price": "total_revenue", "order_id": "total_sold"}, inplace=True)
product_sales = product_sales.merge(products_df, on="product_id", how="left")


# Streamlit app
st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")

# Sidebar Navigation
st.sidebar.image("logo.png", width=150)
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to", ["Overview", "Sales Analysis", "Payment Methods", "Customer Distribution"])

# Filter by date range
st.sidebar.subheader("Filter by Date Range")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime(order_items_df['shipping_limit_date']).min())
end_date = st.sidebar.date_input("End Date", pd.to_datetime(order_items_df['shipping_limit_date']).max())
filtered_orders = order_items_df[(order_items_df['shipping_limit_date'] >= str(start_date)) & (order_items_df['shipping_limit_date'] <= str(end_date))]

st.title("📊 E-Commerce Dashboard")
st.markdown("---")

if menu == "Overview":
    st.header("📊 Overview of E-Commerce Data")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Orders", filtered_orders.shape[0])
    col2.metric("Unique Products", products_df['product_id'].nunique())
    col3.metric("Total Revenue", f"${filtered_orders['price'].sum():,.2f}")
    
    st.subheader("Data Summary")
    st.write(filtered_orders.describe())
    
    if st.checkbox("Show Raw Data"):
        st.write(filtered_orders)

elif menu == "Sales Analysis":
    st.header("📈 Sales Analysis")
    most_popular = product_sales.nlargest(10, "total_sold")
    least_popular = product_sales.nsmallest(10, "total_sold")
    
    fig, ax = plt.subplots(1, 2, figsize=(18, 6), gridspec_kw={'wspace': 0.4})
    sns.barplot(y=most_popular["product_category_name"], x=most_popular["total_sold"], ax=ax[0], palette="Blues")
    ax[0].set_title("Top 10 Best-Selling Products")
    ax[0].set_xlabel("Total Sold")
    ax[0].set_ylabel("Product Category")
    
    sns.barplot(y=least_popular["product_category_name"], x=least_popular["total_sold"], ax=ax[1], palette="Reds")
    ax[1].set_title("Top 10 Least-Selling Products")
    ax[1].set_xlabel("Total Sold")
    ax[1].set_ylabel("Product Category")
    
    st.pyplot(fig)
    
    # Top Profitable Products
    top_profitable = product_sales.nlargest(10, "total_revenue")
    st.subheader("🏆 Top 10 Most Profitable Products")
    st.write(top_profitable[["product_category_name", "total_revenue"]])
    
    if st.button("Download Sales Data"):
        csv = product_sales.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", data=csv, file_name="sales_data.csv", mime='text/csv')

elif menu == "Payment Methods":
    st.header("💳 Payment Methods Distribution")
    
    # Menggunakan data yang sudah difilter berdasarkan rentang tanggal
    filtered_payments = order_payments_df[order_payments_df['order_id'].isin(filtered_orders['order_id'])]

    if not filtered_payments.empty:
        payment_counts = filtered_payments["payment_type"].value_counts()

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

        # Menampilkan jumlah transaksi per metode pembayaran di bawah pie chart
        st.subheader("📋 Payment Methods Breakdown")
        st.write(payment_counts.reset_index().rename(columns={"index": "Payment Method", "payment_type": "Transaction Count"}))
    else:
        st.warning("No payment data available for the selected date range.")


elif menu == "Customer Distribution":
    st.header("🌍 Customer Distribution by Zip Code")
    customer_distribution = customers_df["customer_zip_code_prefix"].value_counts().nlargest(10)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x=customer_distribution.index, y=customer_distribution.values, palette="coolwarm")
    ax.set_title("Customer Distribution by Zip Code (Top 10)")
    ax.set_xlabel("Zip Code")
    ax.set_ylabel("Number of Customers")
    st.pyplot(fig)
    
    search_zip = st.text_input("Search Customer by Zip Code")
    if search_zip:
        filtered_customers = customers_df[customers_df["customer_zip_code_prefix"].astype(str) == search_zip]
        st.write(filtered_customers)
    
    # Top Customers
    st.subheader("🏅 Top 10 Customers with Highest Orders")
    top_customers = order_items_df["order_id"].value_counts().nlargest(10)
    st.write(top_customers)

