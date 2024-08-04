import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go 
#import pyodbc as odbc


# Defining the Component of Connection String
DRIVER_NAME = "{ODBC Driver 17 for SQL Server}"
SERVER_NAME = "aminpour-lap"
DATABASE_NAME = "order_management"
USERNAME = "DGSERVICE\b.aminpour"


connection_string = f"""
    DRIVER={DRIVER_NAME};
    SERVER={SERVER_NAME};
    DATABASE={DATABASE_NAME};
    Trusted_Connection=yes;
"""



#conn = odbc.connect(connection_string, pooling=False)
#cursor = conn.cursor()


# Returning All the Values from Fields and Records in Desired Table 
#query1 = """
#    SELECT * 
#    FROM order_management.dbo.orders_0101_0505
#"""

#result = cursor.execute(query1).fetchall()



# Coverting our Sql Based Table into Pandas Dataframe
#df_orders = pd.read_sql(query1, conn)
df_orders = pd.read_csv('data.csv')
df_orders.head()


# Selecting only required fileds and renaming multywords to solely words title

df = df_orders[['ProductNameColor', 'Date_Formated', 'ColorName',
                'Category', 'WarrantyName', 'Quantity', 'UnitBasePrice',
                'UnitNetPrice', 'UnitDiscount', 'TotalPrice', 'TotalNetPrice', 'TotalDiscount']]

df = df.rename(columns= {'Date_Formated': 'Date', 'ProductNameColor': 'Product', 'ColorName': 'Color', 'WarrantyName': 'Warranty'})


# Convert 'Date' column to datetime
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Check for invalid dates and handle them
df = df.dropna(subset=['Date'])

# Convert numeric columns to the correct type
df['TotalPrice'] = pd.to_numeric(df['TotalPrice'], errors='coerce')
df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')


# Ensure 'Date' column is in datetime format
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Ensure 'TotalPrice' and 'Quantity' columns are numeric
df['TotalPrice'] = pd.to_numeric(df['TotalPrice'], errors='coerce')
df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')

# Check for NaN values in numeric columns and handle them
df = df.dropna(subset=['TotalPrice', 'Quantity'])




# Convert columns to numeric, forcing errors to NaN (useful for cleaning data)
df['UnitBasePrice'] = pd.to_numeric(df['UnitBasePrice'], errors='coerce')
df['TotalPrice'] = pd.to_numeric(df['TotalPrice'], errors='coerce')
df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')




# Optionally fill or drop missing values
# df = df.dropna()  # Drop rows with any missing values
# or
df = df.fillna(0)  # Replace missing values with 0 (if appropriate)


# Calculating available metrics (total)
total_quantity = df['Quantity'].sum()
total_discount = df['TotalDiscount'].sum()
total_net = df['TotalNetPrice'].sum()
total_price = df['TotalPrice'].sum()




# total price and total net price grouped by each category and date

total_price_cd = df.groupby(['Category', 'Date'])['TotalPrice'].sum().reset_index()
total_price_cd['Date'] = pd.to_datetime(total_price_cd['Date'], errors='coerce')  # Convert to datetime if needed
total_price_cd = total_price_cd.sort_values(by='Date').reset_index(drop=True)



total_net_cd = df.groupby(['Category', 'Date'])['TotalNetPrice'].sum().reset_index()
total_net_cd = total_net_cd.sort_values('Date').reset_index(drop = True)


# Example of sorting by 'Date'




# Grouping each catgory by total price and total net price

category_total = df.groupby(['Category']).agg({'TotalPrice': 'sum', 'TotalNetPrice': 'sum'}).reset_index()
category_total = category_total.sort_values('TotalPrice', ascending=False).reset_index(drop=True)








# Function to format Persian dates
def format_persian_date(date_str):
    if pd.notna(date_str):
        parts = date_str.split('-')
        if len(parts) == 3:
            year, month, day = parts
            return f'{month}-{day}'
    return 'Unknown'

# Apply date formatting to your DataFrame
df['FormattedDate'] = df['Date'].apply(format_persian_date)

# Filter DataFrame by category and date
def filter_data(df, selected_category, start_date, end_date):
    filtered_df = df[df['Category'] == selected_category]
    filtered_df = filtered_df[(filtered_df['Date'] >= start_date) & (filtered_df['Date'] <= end_date)]
    return filtered_df

# Trend Chart Sales Over Time Past 5 months
def sales_over_time(df):
    daily_sales = df.groupby(['FormattedDate', 'Date']).sum()['TotalPrice'].reset_index()
    daily_sales = daily_sales.sort_values(by='Date')
    fig = px.line(daily_sales, x='FormattedDate', y='TotalPrice', title='Sales Over Time')
    fig.update_traces(line=dict(color='blue'))
    return fig

# Trend Chart quantity of Sales Over Time Past 5 months
def sales_q_over_time(df):
    daily_sales = df.groupby(['FormattedDate', 'Date']).sum()['Quantity'].reset_index()
    daily_sales = daily_sales.sort_values(by='Date')
    fig = px.line(daily_sales, x='FormattedDate', y='Quantity', title='Quantity Sold Over Time')
    fig.update_traces(line=dict(color='red'))
    return fig

# Sales by Category
def sales_by_category(df):
    category_sales = df.groupby('Category').sum()[['TotalPrice', 'TotalNetPrice']].reset_index()
    category_sales_melted = category_sales.melt(id_vars='Category', value_vars=['TotalPrice', 'TotalNetPrice'], var_name='Metric', value_name='Value')
    fig = px.bar(category_sales_melted, x='Category', y='Value', color='Metric', 
                title='Sales by Category', barmode='group',
                color_discrete_map={'TotalPrice': 'royalblue', 'TotalNetPrice': 'darkorange'})
    fig.update_layout(xaxis_title='Category', yaxis_title='Value', legend_title='Metrics')
    return fig

# Top Products by Total Sales
def top_products_by_sales(df):
    product_sales = df.groupby(['Product', 'Category', 'Color']).agg({'TotalPrice': 'sum', 'Quantity': 'sum'}).reset_index()
    product_sales = product_sales.sort_values(by='TotalPrice', ascending=False).head(10).reset_index()
    fig = px.bar(product_sales, x='Product', y='TotalPrice', color='Quantity', title='Top Products by Total Sales')
    return fig

# Unit Price Distribution
def unit_price_distribution(df):
    min_price = df['UnitBasePrice'].min()
    max_price = df['UnitBasePrice'].max()
    bin_edges = [min_price + i*(max_price-min_price)/10 for i in range(11)]
    bin_labels = [f'{int(bin_edges[i]):,}-{int(bin_edges[i+1]):,}' for i in range(len(bin_edges)-1)]
    df['PriceRange'] = pd.cut(df['UnitBasePrice'], bins=bin_edges, labels=bin_labels, include_lowest=True)
    price_range_distribution = df.groupby('PriceRange').sum()[['Quantity']].reset_index()
    fig = px.bar(price_range_distribution, x='PriceRange', y='Quantity', title='Distribution of Unit Prices and Quantity Sold')
    return fig

# Unit Price Distribution for Different Ranges
def unit_price_distribution1(df):
    min_price = df['UnitBasePrice'].min()
    max_price = 8000000
    bin_edges = [min_price + i*(max_price-min_price)/40 for i in range(41)]
    bin_labels = [f'{int(bin_edges[i]):,}-{int(bin_edges[i+1]):,}' for i in range(len(bin_edges)-1)]
    df['PriceRange'] = pd.cut(df['UnitBasePrice'], bins=bin_edges, labels=bin_labels, include_lowest=True)
    price_range_distribution = df.groupby('PriceRange').sum()[['Quantity']].reset_index()
    fig = px.bar(price_range_distribution, x='PriceRange', y='Quantity', title='Unit Prices Distribution (Up to 8M)',
                 color_discrete_sequence=['gold'])
    return fig

def unit_price_distribution2(df):
    min_price = 8000000
    max_price = df['UnitBasePrice'].max()
    bin_edges = [min_price + i*(max_price-min_price)/40 for i in range(41)]
    bin_labels = [f'{int(bin_edges[i]):,}-{int(bin_edges[i+1]):,}' for i in range(len(bin_edges)-1)]
    df['PriceRange'] = pd.cut(df['UnitBasePrice'], bins=bin_edges, labels=bin_labels, include_lowest=True)
    price_range_distribution = df.groupby('PriceRange').sum()[['Quantity']].reset_index()
    fig = px.bar(price_range_distribution, x='PriceRange', y='Quantity', title='Unit Prices Distribution (8M to 150M)',
                 color_discrete_sequence=['gold'])
    return fig

def sales_vs_discounts(df):
    fig = px.scatter(df, x='TotalPrice', y='UnitDiscount', title='Sales vs. Discounts', trendline='ols')
    return fig




st.set_page_config(
    page_title="Sales Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded"
)

with open('style (1).css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


# Streamlit integration
def main():
    st.title('Order Records Dashboard')
    
    # Display a sample of the DataFrame to check types and content
    st.write(df.head())
    st.write(df.dtypes)

    # Display the sorted DataFrame
    st.write(total_price_cd.head())

if __name__ == "__main__":
    main()
