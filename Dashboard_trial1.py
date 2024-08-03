import warnings
import numpy as pd
import pandas as pd
import pyodbc as odbc
import streamlit as st
import matplotlib.pyplot as plt


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


st.title('Order Management Dashboard')
st.markdown("عملکرد فروش از 1 فروردین تا 5 مرداد 1403")

st.subheader("Metrics")
col1 = st.columns(1)
st.metric('Total Quantity', total_quantity)


st.sidebar.header('Dashboard `version 2`')


st.sidebar.header('Dashboard `version 2`')
