#!/usr/bin/env python
# coding: utf-8

# In[12]:


import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots


# In[30]:


lithium_composition = pd.read_csv('combined_battery_compositions.csv')
lithium_composition = lithium_composition.drop(columns = 'Unnamed: 7')
lithium_composition.set_index('Battery Type', inplace = True)
lithium_composition = lithium_composition/100
lithium_composition


# In[36]:


market_shares = pd.read_csv('battery_yearly_market_shares-2.csv')
market_shares_2023 = market_shares.loc[5].transpose()
market_shares_2023 = pd.DataFrame(market_shares_2023)
market_shares_2023 = market_shares_2023.drop(index=['Date', 'Other'])
market_shares_2023_cleaned = market_shares_2023.reset_index()
market_shares_2023_cleaned
market_shares_2023_cleaned.columns = ['Battery Types', 'Market Share (%)']
market_shares_2023_cleaned.set_index('Battery Types', inplace = True)
market_shares_2023_cleaned


# In[37]:


price = pd.read_csv('Copy of PNICKUSDM.csv')
price_cleaned = price.transpose()
price_cleaned
price_cleaned.index = price_cleaned.index.to_series().str.replace('M', '-').apply(lambda x: f"{x}-01")

# Convert to datetime
price_cleaned.index = pd.to_datetime(price_cleaned.index, format='%Y-%m-%d')
price_cleaned


# In[38]:


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


# In[44]:


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

for mineral in minerals:
    fig.add_trace(go.Scatter(x=price_cleaned.index, y=price_cleaned[mineral], mode='lines+markers', name=f'{mineral} Price'), row=4, col=1)
    fig.update_yaxes(range=[0, max(price_cleaned.max()) * 1.1], row=4, col=1)

fig.update_layout(
    title="Lithium-ion Battery Market and Mineral Data Dashboard",
    barmode='stack'
)

fig.show()


# In[ ]:




