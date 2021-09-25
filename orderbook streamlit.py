import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random as rd
import streamlit as st
import time 
pd.options.mode.chained_assignment = None
plt.style.use('dark_background')
st.set_page_config(page_title=None, page_icon=None, layout='wide', initial_sidebar_state='auto', menu_items=None)

st.write("""
   # Decentralized CFDs Exchange
""")

def brownian_motion(S0, u, rf, num_days, sigma):  #efinimos sus variables
    dt = 1/360
    price_series = [S0]
    for i in range(num_days):
        price_series.append(price_series[-1]*(1+u*dt + sigma * np.random.normal(0, 1) * np.sqrt(dt)))
    return price_series 

subyacente = brownian_motion(10, 0.1, 0.025, 30, 0.2)
empty_sub = pd.DataFrame([9.9],columns=['Price'], index=[0])


col1, col2 = st.columns([1, 2.5])
col2.write('Underlying Asset Price')
col1.write('Order Book')

plot_slot = col2.empty()
metric_slot = col2.empty()
info_slot = col2.empty()
trades_slot = col2.empty()
sell_df = col1.empty()
buy_df = col1.empty()



s = 0
def create_orders(buy=True, market_price=s):
    if buy:
        buy_orders = [subyacente[market_price]*(1-i/1500) for i in range(3)]
        buy_orders_size = [rd.randint(1, i) for i in range(100,10,-30)]
        return [list(i) for i in zip(buy_orders, buy_orders_size)]
    else:
        sell_orders = [subyacente[market_price]*(1+i/1500) for i in range(3)]
        sell_orders_size = [rd.randint(1, i) for i in range(100,10,-30)]
        return [list(i) for i in zip(sell_orders,sell_orders_size)]

# ORDER BOOK
trades = pd.DataFrame(columns=['Price','Size', 'Underlying Market Price'])

order_book_b = pd.DataFrame(create_orders(), columns=['Price', 'Size']).sort_values(by=['Price'], ascending=False).reset_index(drop=True)
order_book_s = pd.DataFrame(create_orders(False), columns=['Price', 'Size']).sort_values(by=['Price']).reset_index(drop=True)



# MATCHING ALGORITHM
trade = 0
print("\n SELL", order_book_s.sort_values(by=['Price'], ascending=False))
print("\n BUY", order_book_b)
for s in range(len(subyacente)):
    empty_sub.loc[s+1] = subyacente[s]
    fig, ax = plt.subplots()
    ax.plot(empty_sub)
    fig.set_figheight(7)
    fig.set_figwidth(15)
    plot_slot.pyplot(fig)
    while max(order_book_b['Price']) >= min(order_book_s['Price']):
        if order_book_b['Price'][0] >= order_book_s['Price'][0]:
            trade += 1 
            price = order_book_b['Price'][0]
            size = min(order_book_b['Size'][0], order_book_s['Size'][0])
            trades.loc[trade]=[price, size, subyacente[s]]
            info_slot.write(f'\n {size} DCFDs entered at ${round(price,2)}')
            
            order_book_b['Size'][0] -= size 
            order_book_s['Size'][0] -= size 
            
            if order_book_b['Size'][0] == 0:
                order_book_b = order_book_b.drop(0).reset_index(drop=True)
                
            if order_book_s['Size'][0] == 0:
                order_book_s = order_book_s.drop(0).reset_index(drop=True)

    #New orders
    new_buy_orders=create_orders(market_price=s)
    for order in range(3):
        order_book_b.loc[len(order_book_b)+s] = new_buy_orders[order]
    order_book_b = order_book_b.sort_values(by=['Price'], ascending=False).reset_index(drop=True)
    
    new_sell_orders=create_orders(False,market_price=s)
    for order in range(3):
        order_book_s.loc[len(order_book_s)+s] = new_sell_orders[order]
    order_book_s = order_book_s.sort_values(by=['Price']).reset_index(drop=True)
    
    metric_slot.metric(label='Underlying Price', value=round(subyacente[s],2), delta=round(subyacente[s]-subyacente[s-1],3))
    trades_slot.dataframe(trades)
    sell_df.dataframe(order_book_s.sort_values(by=['Price'], ascending=False)[:10])
    buy_df.dataframe(order_book_b[:10])
    time.sleep(1)
    


    
