"""
Created on Sat Sep 18 09:49:34 2021
Jero & Juan
"""
import pandas as pd
import numpy as np
import time
import streamlit as st
import random as rd
import matplotlib.pyplot as plt
import yfinance as yf
import string
st.set_page_config(layout="wide")

adress_gen = string.ascii_letters + string.digits

st.write(""" 
         ## DCFD Decentralized Exchange
         """)

st.sidebar.write('Panel de Trading')
ticker = st.sidebar.selectbox('Select Strategy', ('AAPL','GME'))
side1, side2= st.sidebar.columns(2)
with st.sidebar.form(key='form1'):
    
    leverage = st.slider('Select Leverage', min_value=(1), max_value=(100))
    cantidad = st.number_input('Enter Quantity', step =1)
    buy = st.form_submit_button('Buy')
    sell = st.form_submit_button('Sell')
    closebuy = st.form_submit_button('Close Buy')
    closesell = st.form_submit_button('Close Sell')
    print(leverage, cantidad, buy, sell, closebuy, closesell)
    
    

col1, col2 = st.columns([1, 2.5])
col2.write('Underlying Asset Price')
col1.write('Order Book')

plot_slot = col2.empty()
margin_plot = col2.empty()
trade_df = col2.empty()

balance_slot = st.sidebar.empty()

sell_df = col1.empty()
metric_slot = col1.empty()
buy_df = col1.empty()
info_slot = col1.empty()
trades_slot = col1.empty()



# Definimos los agentes involucrados dado que conectaron sus billeteras virtuales
class user:    
    def __init__(self, name, wallet_id, usdt): 
        # Donde balance es el balance de stablecoins en la billetera de un usuario
        # Y la dirección es 1 para "LONG" y -1 para "SHORT"
        self.name = name
        self.wallet_id = wallet_id
        self.usdt = usdt
        self.active = False
  
# Creamos un smart contract vacio para ser usado para el settlement
class smart_contract:
    def __init__(self, address, balance):
        self.address = address
        self.balance = balance
        
    def send_back_long(self):
        sum_to_transfer =  df.loc[df.last_valid_index(),'margin_long'] #init_margin_long +
        user_long.usdt += sum_to_transfer
        self.balance -= sum_to_transfer
        print(f'{sum_to_transfer} TRASFERRED TO USER LONG \n')
        
    def send_back_short(self):
        sum_to_transfer =  df.loc[df.last_valid_index(),'margin_short'] #init_margin_short +
        user_short.usdt += sum_to_transfer
        self.balance -= sum_to_transfer
        print(f'{sum_to_transfer} TRASFERRED TO USER SHORT \n')


smart_contract = smart_contract('abcd', 0)
       

# Estos fields van a venir de la interfaz        
user_long = user("Jero", "01234", 10000)
user_short = user("Juan","56789", 10000)     


subyacente = pd.read_csv('sub.csv')



''' Order Book '''
def create_orders(market_price,buy=True):
    if buy:
        buy_orders = [market_price*(1-i/1500) for i in range(3)]
        buy_orders_size = [rd.randint(1, i) for i in range(100,10,-30)]
        address = [''.join(rd.choice(adress_gen) for i in range(10)) for j in range(3)]
        return [list(i) for i in zip(buy_orders, buy_orders_size, address)]
    else:
        sell_orders = [market_price*(1+i/1500) for i in range(3)]
        sell_orders_size = [rd.randint(1, i) for i in range(100,10,-30)]
        address = [''.join(rd.choice(adress_gen) for i in range(10)) for j in range(3)]
        return [list(i) for i in zip(sell_orders,sell_orders_size, address)]



order_book_b = pd.DataFrame(create_orders(subyacente['price'][0]), columns=['Price', 'Size', 'Address']).sort_values(by=['Price'], ascending=False).reset_index(drop=True)
order_book_s = pd.DataFrame(create_orders(subyacente['price'][0],False), columns=['Price', 'Size', 'Address']).sort_values(by=['Price']).reset_index(drop=True)


#df = pd.DataFrame() 


trades = pd.DataFrame(columns=['Price','Size', 'MP', 'Contract id'])

def match_orders(i):
    global order_book_b, order_book_s
    
    while max(order_book_b['Price']) >= min(order_book_s['Price']):
        if order_book_b['Price'][0] >= order_book_s['Price'][0]:
            price = order_book_b['Price'][0]
            size = min(order_book_b['Size'][0], order_book_s['Size'][0])
            contract_id = order_book_b['Address'][0]
            trades.loc[contract_id]=[price, size, i, contract_id]
            info_slot.write(f'\n {size} DCFDs entered at ${round(price,2)}')
            #print(f'{size} matched at {round(price,2)}')
            
            order_book_b.loc[0,'Size'] -= size 
            order_book_s.loc[0,'Size'] -= size 
            
            if order_book_b.loc[0,'Size'] == 0:
                order_book_b = order_book_b.drop(0).reset_index(drop=True)
                
            if order_book_s.loc[0,'Size'] == 0:
                order_book_s = order_book_s.drop(0).reset_index(drop=True)
 




#columns = ['Price', 'margin_long', 'margin_short', 'pnl_long',
 #                            'pnl_short', 'state_long', 'state_short', 'risk_long', 'risk_short'], index=[0]
 
# RISK MANAGEMENT TOOL (CENTRALIZED) Para los cálculos del margen de cada agente  

counter = 0
def main():
    global order_book_b, order_book_s, market_price, df, subyacente, leverage, cantidad, counter, balance_slot, buy
    while True:
        subyacente = pd.read_csv('sub.csv')   
        fig, ax = plt.subplots()
        ax.plot(subyacente['price'])
        fig.set_figheight(7) 
        fig.set_figwidth(15)
        plot_slot.pyplot(fig)
        
        i = round(subyacente.loc[subyacente.index[-1],'price'],3)
        print(counter)
        if buy == True and counter == 0: #or sell == True: 
            counter =+ 1
            #add_user_order(subyacente.loc[subyacente.index[-1],'price'], leverage = leverage, cantidad = cantidad)
            user_long.active = True
            df = pd.DataFrame()
            init_margin_long = init_margin_short = i* cantidad / leverage
            df.loc[0, ['Price', 'margin_long', 'margin_short', 'pnl_long',
               'pnl_short', 'state_long', 'state_short', 'risk_long', 'risk_short']] = [i, init_margin_long, init_margin_short, 0, 0, 0, 0, 0, 0]
            user_long.usdt = user_long.usdt - init_margin_long
            print(f'user balance {user_long.usdt}')
            
        print('closebuy: {closebuy}')        
        if closebuy == True and counter == 1:
            counter = 1
            print('User long closed position \n')
            user_long.usdt =+ 30000
            #smart_contract.send_back_long()
            user_long.active = False
            buy = False

        if sell == True and counter == 0: #or sell == True: 
            counter =+ 1
            #add_user_order(subyacente.loc[subyacente.index[-1],'price'], leverage = leverage, cantidad = cantidad)
            user_long.active = True
            df = pd.DataFrame()
            init_margin_long, init_margin_short = i, i
            df.loc[0, ['Price', 'margin_long', 'margin_short', 'pnl_long',
               'pnl_short', 'state_long', 'state_short', 'risk_long', 'risk_short']] = [i, init_margin_long, init_margin_short, 0, 0, 0, 0, 0, 0]
            
            if closesell == True:
                user_short.active = False
                print('User short closed position \n')
                smart_contract.send_back_short()
        
        
        match_orders(i)
        
        
             
        ### SI la orden del usuario se matcheo... Mostrar el proceso
        if user_long.active == True:  
            df.loc[i,'Price'] = trades['Price'][len(trades)-1] #Suponiendo q gabo. (en todo el script long=GABO)
            entryprice = df.loc[df.index[0],'Price']
            df.loc[i,"risk_long"] = leverage * (((df.loc[i,"Price"]) / entryprice) -1)
            df.loc[i,"risk_short"] = -leverage * (((df.loc[i,"Price"]) / entryprice) -1)
            
            df.loc[i,"pnl_long"] = ((df.loc[i,"Price"] / entryprice) -1) * cantidad * entryprice
            df.loc[i,"pnl_short"] = -((df.loc[i,"Price"] / entryprice) -1) * cantidad * entryprice
    
            df.loc[i,'margin_long'] = round(df.iloc[-1,3]+df.iloc[-2,1],2) 
            df.loc[i,'margin_short'] = round(df.iloc[-1,4]+df.iloc[-2,2],2)
            
            margin_plot.bar_chart(df[['margin_long', 'margin_short']])
            
            #Long
            if df.loc[i,"risk_long"] < -0.50 and df.loc[i,"risk_long"] > -0.8:
                df.loc[i,"state_long"] = "Called"
                #print(df)
                print(f"Hey, {user_long.name}, you just got a margin call ! Add more funds !")
        
            elif df.loc[i,"risk_long"] < -0.8:                 
                df.loc[i,"state_long"] = "Liquidated"
                print("Your position has been liquidated !")
                
                
            #Short
            if df.loc[i,"risk_short"] < -0.50 and df.loc[i,"risk_short"] > -0.8:
                df.loc[i,"state_short"] = "Called"
                print(f"Hey, {user_short.name}, you just got a margin call ! Add more funds !")
                
                    
            elif df.loc[i,"risk_short"] < -0.8:
                df.loc[i,"state_short"] = "Liquidated"
                print("Your position has been liquidated !")
                
            trade_df.dataframe(df)
                 
    
        #New orders so the order book keeps running
        new_buy_orders=create_orders(i, True)
        for order in range(3):
            order_book_b.loc[len(order_book_b)+i] = new_buy_orders[order]
        order_book_b = order_book_b.sort_values(by=['Price'], ascending=False).reset_index(drop=True)
        
        new_sell_orders=create_orders(i,False)
        for order in range(3):
            order_book_s.loc[len(order_book_s)+i] = new_sell_orders[order]
        order_book_s = order_book_s.sort_values(by=['Price']).reset_index(drop=True)
        
        metric_slot.metric(label='Underlying Price', value=round(i,2), delta=round(i-subyacente.loc[subyacente.index[-2], 'price'],3))
        trades_slot.dataframe(trades)
        sell_df.dataframe(order_book_s.sort_values(by=['Price'], ascending=False).reset_index(drop=True)[:9])
        buy_df.dataframe(order_book_b[:9])
        print(f'User state: {user_long.active}')
        balance_slot.write(f'User balance: {user_long.usdt}')
        
        yield


  
def event_loop(tareas):
    while tareas:
        actual = tareas.pop(0)
        try:
            #print('-')
            next(actual)
            tareas.append(actual)
        except StopIteration:
            #print(f'{actual} stopped iteration')
            pass
        
#brownian_motion(subyacente, 0.1, 0, 0.2)
event_loop([main()])
