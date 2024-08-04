import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


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
# df_orders = pd.read_sql(query1, conn)
df_orders = pd.read_csv('data.csv')
df_orders.head()


# Selecting only required fileds and renaming multywords to solely words title

df = df_orders[['ProductNameColor', 'Date_Formated', 'ColorName',
                'Category', 'WarrantyName', 'Quantity', 'UnitBasePrice',
                'UnitNetPrice', 'UnitDiscount', 'TotalPrice', 'TotalNetPrice', 'TotalDiscount']]

df = df.rename(columns= {'Date_Formated': 'Date', 'ProductNameColor': 'Product', 'ColorName': 'Color', 'WarrantyName': 'Warranty'})



# Calculating available metrics (total)
total_quantity = df['Quantity'].sum()
total_discount = df['TotalDiscount'].sum()
total_net = df['TotalNetPrice'].sum()
total_price = df['TotalPrice'].sum()




# total price and total net price grouped by each category and date

total_price_cd = df.groupby(['Category', 'Date'])['TotalPrice'].sum().reset_index()
total_price_cd = total_price_cd.sort_values('Date').reset_index(drop = True)

total_net_cd = df.groupby(['Category', 'Date'])['TotalNetPrice'].sum().reset_index()
total_net_cd = total_net_cd.sort_values('Date').reset_index(drop = True)



# Grouping each catgory by total price and total net price

category_total = df.groupby(['Category']).agg({'TotalPrice': 'sum', 'TotalNetPrice': 'sum'}).reset_index()
category_total = category_total.sort_values('TotalPrice', ascending=False).reset_index(drop=True)



st.set_page_config(layout='wide', initial_sidebar_state='expanded')

with open('style (1).css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)





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

# Streamlit dashboard
def main():
    st.title('Order Records Dashboard')
    
    # Filter by category
    categories = df['Category'].unique()
    selected_category = st.sidebar.selectbox('Select Category', categories)
    
    # Filter by date
    min_date = df['Date'].min()
    max_date = df['Date'].max()
    start_date = st.sidebar.date_input('Start Date', min_date)
    end_date = st.sidebar.date_input('End Date', max_date)
    
    # Filter data
    filtered_df = filter_data(df, selected_category, start_date, end_date)
    
    # Display charts
    st.header('Sales Over Time')
    st.plotly_chart(sales_over_time(filtered_df))
    
    st.header('Quantity Sold Over Time')
    st.plotly_chart(sales_q_over_time(filtered_df))
    
    st.header('Sales by Category')
    st.plotly_chart(sales_by_category(filtered_df))
    
    st.header('Top Products by Total Sales')
    top_products = top_products_by_sales(filtered_df)
    st.write(top_products)
    
    st.header('Unit Price Distribution')
    st.plotly_chart(unit_price_distribution(filtered_df))
    
    st.header('Unit Price Distribution (Up to 8M)')
    st.plotly_chart(unit_price_distribution1(filtered_df))
    
    st.header('Unit Price Distribution (8M to 150M)')
    st.plotly_chart(unit_price_distribution2(filtered_df))
    
    st.header('Sales vs. Discounts')
    st.plotly_chart(sales_vs_discounts(filtered_df))

if __name__ == "__main__":
    main()
