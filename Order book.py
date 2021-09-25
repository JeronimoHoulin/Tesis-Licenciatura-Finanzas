import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import random as rd
pd.options.mode.chained_assignment = None

def brownian_motion(S0, u, rf, num_days, sigma):  #efinimos sus variables
    dt = 1/360
    price_series = [S0]
    for i in range(num_days):
        price_series.append(price_series[-1]*(1+u*dt + sigma * np.random.normal(0, 1) * np.sqrt(dt)))
    return price_series 

subyacente = brownian_motion(146, 0.1, 0.025, 30, 0.2)


# ORDER BOOK
trades = pd.DataFrame(columns=['Price','Size', 'Market Price'])

order_book_b = pd.DataFrame(create_orders(), columns=['Price', 'Size']).sort_values(by=['Price'], ascending=False).reset_index(drop=True)
order_book_s = pd.DataFrame(create_orders(False), columns=['Price', 'Size']).sort_values(by=['Price']).reset_index(drop=True)

# MATCHING ALGORITHM
trade = 0
print("\n SELL", order_book_s.sort_values(by=['Price'], ascending=False))
print("\n BUY", order_book_b)
for s in range(len(subyacente)):
    while max(order_book_b['Price']) >= min(order_book_s['Price']):
        if order_book_b['Price'][0] >= order_book_s['Price'][0]:
            trade += 1 
            price = order_book_b['Price'][0]
            size = min(order_book_b['Size'][0], order_book_s['Size'][0])
            trades.loc[trade]=[price, size, subyacente[s]]
            print(f'\n {size} DCFDs entered at ${round(price,2)}')
            
            order_book_b['Size'][0] -= size 
            order_book_s['Size'][0] -= size 
            
            if order_book_b['Size'][0] == 0:
                order_book_b = order_book_b.drop(0).reset_index(drop=True)
                print('Order gone from Buy order book')
                print("\n SELL", order_book_s.sort_values(by=['Price'], ascending=False))
                print("\n BUY", order_book_b)
                print("\n -------------------------")
                
            if order_book_s['Size'][0] == 0:
                order_book_s = order_book_s.drop(0).reset_index(drop=True)
                print('Order gone from Sell order book')
                print("\n SELL", order_book_s.sort_values(by=['Price'], ascending=False))
                print("\n BUY", order_book_b)
                print("\n -------------------------")     
    #New orders
    new_buy_orders=create_orders(market_price=s)
    for order in range(3):
        order_book_b.loc[len(order_book_b)+s] = new_buy_orders[order]
    order_book_b = order_book_b.sort_values(by=['Price'], ascending=False).reset_index(drop=True)
    
    new_sell_orders=create_orders(False,market_price=s)
    for order in range(3):
        order_book_s.loc[len(order_book_s)+s] = new_sell_orders[order]
    order_book_s = order_book_s.sort_values(by=['Price']).reset_index(drop=True)
    time.sleep(2)
