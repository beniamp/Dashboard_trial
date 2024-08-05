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


# Check for invalid dates and handle them
df = df.dropna(subset=['Date'])




# Convert columns to numeric, forcing errors to NaN (useful for cleaning data)
df['UnitBasePrice'] = pd.to_numeric(df['UnitBasePrice'], errors='coerce')
df['TotalPrice'] = pd.to_numeric(df['TotalPrice'], errors='coerce')
df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')



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


df = df.dropna(subset=['Date'])



# Customizing persian month to corresponding month name by dictionary
persian_months = {'01': 'Far', '02': 'Ord', '03': 'Kho',
        '04': 'Tir', '05': 'Mor', '06': 'Sha',
        '07': 'Meh', '08': 'Aba', '09': 'Aza',
        '10': 'Dey', '11': 'Bah', '12': 'Esf' }




def format_persian_date(date_str):
        if date_str is None:
            return None
        parts = date_str.split('-')
        if len(parts) == 3:
            year, month, day = parts
            persian_month = persian_months.get(month, month)
            return f'{persian_month} {day}'
        return date_str

df['FormattedDate'] = df['Date'].apply(format_persian_date)


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
def top_products_by_sales_chart(df):
    # Data transformation
    product_sales = df.groupby(['Product', 'Category', 'Color']).agg({
        'TotalPrice': 'sum', 
        'Quantity': 'sum'
    }).reset_index()
    product_sales = product_sales.sort_values(by='Quantity', ascending=False).reset_index(drop=True)
    
    # Create a Plotly table
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(product_sales.columns),
            fill_color='paleturquoise',
            align='left'
        ),
        cells=dict(
            values=[product_sales[col] for col in product_sales.columns],
            fill_color='lavender',
            align='left'
        )
    )])
    
    fig.update_layout(title='Top Products by Sales')
    
    return fig



# Unit Price Distribution for Different Ranges
def unit_price_distribution(df):
    # Define price bins with a more scalable approach
    min_price = df['UnitBasePrice'].min()
    max_price = df['UnitBasePrice'].max()
    # Define bin edges; these values can be adjusted as needed
    bin_edges = [min_price + i*(max_price-min_price)/80 for i in range(81)]
    bin_labels = [f'{int(bin_edges[i]):,}-{int(bin_edges[i+1]):,}' for i in range(len(bin_edges)-1)]
    # Assign bin labels to each price
    df['PriceRange'] = pd.cut(df['UnitBasePrice'], bins=bin_edges, labels=bin_labels, include_lowest=True)
    # Aggregate quantity sold within each price range
    price_range_distribution = df.groupby('PriceRange').sum()[['Quantity']].reset_index()
    # Create bar chart
    fig = px.bar(price_range_distribution, x='PriceRange', y='Quantity', title='Distribution of Unit Prices and Quantity Sold (8M to 150M)',
                 color_discrete_sequence=['gold'])
    
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
    
    # Filter by category
    categories = df['Category'].unique()
    selected_category = st.sidebar.selectbox('Select Category', categories)
    
    # Filter the dataframe based on the selected category
    filtered_df = df[df['Category'] == selected_category]


    # Custom date range filter using selectbox
    dates = filtered_df['Date'].unique()
    dates = sorted(dates)  # Sort the dates in ascending order
    selected_start_date = st.sidebar.selectbox('Start Date', dates, index=0)
    selected_end_date = st.sidebar.selectbox('End Date', dates, index=len(dates)-1)


    # Filter the DataFrame based on the selected dates
    filtered_df = filtered_df[(filtered_df['Date'] >= selected_start_date) & (filtered_df['Date'] <= selected_end_date)]
    

    # Show the Overall Price of Sale over time chart
    st.subheader('Sales Over Time Past 5 Months')
    fig_sales = sales_over_time(filtered_df)
    st.plotly_chart(fig_sales)

    # Show the Overall Sales Volume of Sale over time chart
    st.subheader('Quantity Over Time Past 5 Months')
    fig_quantity = sales_q_over_time(filtered_df)
    st.plotly_chart(fig_quantity)

    # Show Sales by Category
    st.subheader('Sales / Net Price by Category')
    fig_cat = sales_by_category(filtered_df)
    st.plotly_chart(fig_cat)

    # Show Top Products by Sales
    st.subheader('Top Products by Sales')
    fig_products = top_products_by_sales_chart(filtered_df)
    st.plotly_chart(fig_products)

    # Show Unit Price Distribution1
    st.subheader('Unit Price Distribution (Overall)')
    fig_dist1 = unit_price_distribution(filtered_df)
    st.plotly_chart(fig_dist1)



if __name__ == "__main__":
    main()
