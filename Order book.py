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
buy_orders = [subyacente[0]*(1-i/1500) for i in range(10)]
buy_orders_size = [rd.randint(1, i) for i in range(110,10,-10)]
order_book_b = pd.DataFrame({'Price': buy_orders, 'Size':buy_orders_size}).sort_values(by=['Price'], ascending=False).reset_index(drop=True)


sell_orders = [subyacente[0]*(1+i/1500) for i in range(10)]
sell_orders_size = [rd.randint(1, i) for i in range(110,10,-10)]
order_book_s = pd.DataFrame({'Price': sell_orders, 'Size':sell_orders_size}).sort_values(by=['Price']).reset_index(drop=True)

order_book = order_book_s.sort_values(by=['Price'], ascending=False).append(order_book_b)

trades = pd.DataFrame(columns=['Price','Size'])

# MATCHING ALGORITHM
for s in range(1, len(subyacente)):

    for i in range(8):
        for j in range(8): 
            if order_book_b['Price'][i] >= order_book_s['Price'][j] and order_book_b['Size'][i] > 0 and order_book_s['Price'][j] > 0:
                price = order_book_b['Price'][i]
                size = min(order_book_b['Size'][i], order_book_s['Size'][j])
                trades.loc[i]=[price, size]
                print(f'\n {size} DCFDs entered at ${round(price,2)} \n')
                
                order_book_b['Size'][i] -= size 
                if order_book_b['Size'][i] == 0:
                    order_book_b = order_book_b.drop(i).reset_index(drop=True)
                    print('Order gone from Buy order book')
                
                order_book_s['Size'][j] -= size 
                if order_book_s['Size'][j] == 0:
                    order_book_s = order_book_s.drop(j).reset_index(drop=True)
                    print('Order gone from Sell order book')
    
    buy_orders = [subyacente[s]*(1-i/1500) for i in range(3)]
    buy_orders_size = [rd.randint(1, i) for i in range(100,10,-30)]
    new_buy_orders=[[i,j] for i in buy_orders for j in buy_orders_size]
    for order in range(3):
        order_book_b.loc[len(order_book_b)+i] = new_buy_orders[order]
    order_book_b.sort_values(by=['Price'], ascending=False).reset_index(drop=True)
    
    sell_orders = [subyacente[s]*(1-i/1500) for i in range(3)]
    sell_orders_size = [rd.randint(1, i) for i in range(100,10,-30)]
    new_sell_orders=[[i,j] for i in sell_orders for j in sell_orders_size]
    for order in range(3):
        order_book_s.loc[len(order_book_s)+i] = new_sell_orders[order]
    order_book_s.sort_values(by=['Price']).reset_index(drop=True)
