#!/usr/bin/env python
# coding: utf-8

# In[12]:

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# 数据加载和处理
lithium_composition = pd.read_csv('combined_battery_compositions.csv')
lithium_composition = lithium_composition.drop(columns='Unnamed: 7')
lithium_composition.set_index('Battery Type', inplace=True)
lithium_composition = lithium_composition / 100

market_shares = pd.read_csv('battery_yearly_market_shares-2.csv')
market_shares_2023 = market_shares.loc[5].transpose()
market_shares_2023 = pd.DataFrame(market_shares_2023)
market_shares_2023 = market_shares_2023.drop(index=['Date', 'Other'])
market_shares_2023_cleaned = market_shares_2023.reset_index()
market_shares_2023_cleaned.columns = ['Battery Types', 'Market Share (%)']
market_shares_2023_cleaned.set_index('Battery Types', inplace=True)

price = pd.read_csv('Copy of PNICKUSDM.csv')
price_cleaned = price.transpose()
price_cleaned.index = price_cleaned.index.to_series().str.replace('M', '-').apply(lambda x: f"{x}-01")
price_cleaned.index = pd.to_datetime(price_cleaned.index, format='%Y-%m-%d')

# 定义表格数据
tables = {
    "Battery Market Share": market_shares_2023_cleaned,
    "Minerals Compositions": lithium_composition,
    "Minerals Prices": price_cleaned
}

# 计算指数时间序列
battery_types = ['NCA', 'NMC_standard', 'NMC_low_nickel', 'NMC_high_nickel', 'LFP']
minerals = ['Lithium (Li) %', 'Nickel (Ni) %', 'Manganese (Mn) %', 'Cobalt (Co) %', 'Aluminum (Al) %', 'Iron (Fe) %']

def calculate_index_over_time(date):
    mineral_prices = price_cleaned.loc[date]
    index = 0
    for battery_type in battery_types:
        market_share = market_shares_2023_cleaned.loc[battery_type, 'Market Share (%)'] / 100
        usage = lithium_composition.loc[battery_type]
        contribution = (usage * mineral_prices).sum() * market_share
        index += contribution
    return index

index_over_time = price_cleaned.index.to_series().apply(calculate_index_over_time)

# 创建图表
fig = make_subplots(
    rows=4, cols=2,
    specs=[[{"type": "pie"}, {"type": "bar"}],
           [{"type": "bar", "colspan": 2}, None],
           [{"type": "scatter", "colspan": 2}, None],
           [{"type": "scatter", "colspan": 2}, None]],
    subplot_titles=("Global Market Share", "Mineral Usage by Battery Type", "Mineral Prices", "Battery Scaled Index Over Time", "Mineral Prices Over Time")
)

# Pie chart for market share
fig.add_trace(go.Pie(labels=market_shares_2023_cleaned.index, values=market_shares_2023_cleaned['Market Share (%)']), row=1, col=1)

# Stacked bar chart for mineral usage
for mineral in minerals:
    fig.add_trace(go.Bar(name=mineral, x=lithium_composition.index, y=lithium_composition[mineral]), row=1, col=2)

# Bar chart for mineral prices (last date)
fig.add_trace(go.Bar(x=price_cleaned.columns, y=price_cleaned.iloc[-1]), row=2, col=1)
fig.update_yaxes(range=[0, 150000], row=2, col=1)

# Line chart for index over time
fig.add_trace(go.Scatter(x=index_over_time.index, y=index_over_time, mode='lines+markers', name='Scaled Index Over Time'), row=3, col=1)

# Line chart for mineral prices over time
for mineral in minerals:
    fig.add_trace(go.Scatter(x=price_cleaned.index, y=price_cleaned[mineral], mode='lines+markers', name=f'{mineral} Price'), row=4, col=1)
    fig.update_yaxes(range=[0, max(price_cleaned.max()) * 1.1], row=4, col=1)

fig.update_layout(
    title="Lithium-ion Battery Market and Mineral Data Dashboard",
    barmode='stack',
    width=1000,
    height=800
)

# 创建选项卡
tab1, tab2 = st.tabs(["📋 Tables", "📊 Dashboard"])

# 表格选项卡
with tab1:
    st.subheader("Select a Table to View")

    # 使用 selectbox 动态选择表格
    selected_table = st.selectbox("Choose a table:", list(tables.keys()))
    st.write(f"Displaying: {selected_table}")
    st.dataframe(tables[selected_table])

# 图表选项卡
with tab2:
    st.subheader("Dashboard Overview")
    st.plotly_chart(fig, use_container_width=True)
# In[ ]:




