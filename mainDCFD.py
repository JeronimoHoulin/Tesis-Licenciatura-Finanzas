"""
Created on Sat Sep 18 09:49:34 2021
Jero & Juan
"""
import pandas as pd
import streamlit as st
import random as rd
import matplotlib.pyplot as plt
import string
import os
import plotly.express as px

st.set_page_config(layout="wide")

adress_gen = string.ascii_letters + string.digits

st.write(""" 
         ## DCFD Decentralized Exchange
         """)

st.sidebar.write('Panel de Trading')
balance_slot = st.sidebar.empty()

ticker = st.sidebar.selectbox('Subyacente: ', ('AAPL','GME'))
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
order_history = col2.empty()

st.sidebar.write('WalletID: 123***45')

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
        sum_to_transfer =  df.loc[df.last_valid_index(),'pnl_long'] #init_margin_long +
        user.usdt += sum_to_transfer
        self.balance -= sum_to_transfer
        print(f'{sum_to_transfer} TRANSFERRED TO USER \n')
        
    def send_back_short(self):
        sum_to_transfer =  df.loc[df.last_valid_index(),'pnl_short'] #init_margin_short +
        user.usdt += sum_to_transfer
        self.balance -= sum_to_transfer
        print(f'{sum_to_transfer} TRANSFERRED TO USER \n')


smart_contract = smart_contract('abcd', 0) ##HAY QUE HACER QUE SE SUMEN LOS  MARGENES CUANDO UNO ENTRA EN UN CONTRATO
       


user =  user("Jero", "01234", 10000)


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
 

# RISK MANAGEMENT TOOL (CENTRALIZED) Para los cálculos del margen de cada agente      
def main():
    global order_book_b, order_book_s, market_price, df, subyacente, leverage, cantidad, counter, buy, sell, closesell, closebuy
    while True:
        subyacente = pd.read_csv('sub.csv')   
        fig, ax = plt.subplots()
        ax.plot(subyacente['price'])
        fig.set_figheight(7) 
        fig.set_figwidth(15)
        plot_slot.pyplot(fig)
        
        i = round(subyacente.loc[subyacente.index[-1],'price'],3)
        
        ## If Buy orders ##

        if buy == True and user.active == False: 
            print('BUY ORDER \n')
            user.active = True
            df = pd.DataFrame()
            init_margin_long = init_margin_short = i* cantidad / leverage
            df.loc[0, ['Price', 'margin_long', 'margin_short', 'pnl_long',
               'pnl_short', 'state_long', 'state_short', 'risk_long', 'risk_short', 'balance_long', 'balance_short']] = [i, init_margin_long, init_margin_short, 0, 0, 0, 0, 0, 0, user.usdt, user.usdt]
            user.usdt = user.usdt - init_margin_long
            
            
            #print(f'user balance {user_long.usdt}')

            
        if closebuy == True:
            print('User long closed position \n')
            df = pd.read_csv('df.csv')

            smart_contract.send_back_long() ##hacer que se envie en margen a wallet del smart.
            
            df1 = pd.DataFrame(columns = ["Entry Price", "Exit Price", "Direction", "P&L"])
            df1 = df1.append({'Entry Price':df.Price[df.index[0]],'Exit Price':df.Price[df.index[-1]], 'Direction': 'Long', 'P&L': df.pnl_long[df.index[-1]] }, ignore_index=True)
            
            order_history.dataframe(df1)
            

            os.remove("df.csv")
            
            user.active = False
            buy = False
            closebuy = False
            
        ## If Sell orders ##

        if sell == True and user.active == False: 
            print('SELL ORDER \n')
            user.active = True
            df = pd.DataFrame()
            init_margin_short = init_margin_long = i* cantidad / leverage
            df.loc[0, ['Price', 'margin_long', 'margin_short', 'pnl_long',
               'pnl_short', 'state_long', 'state_short', 'risk_long', 'risk_short', 'balance_long', 'balance_short']] = [i, init_margin_long, init_margin_short, 0, 0, 0, 0, 0, 0, user.usdt, user.usdt]
            user.usdt = user.usdt - init_margin_short
            
            
            #print(f'user balance {user_long.usdt}')

            
        if closesell == True:
            print('User short closed position \n')
            df = pd.read_csv('df.csv')

            smart_contract.send_back_short() ##hacer que se envie en margen a wallet del smart.
            
            df1 = pd.DataFrame(columns = ["Entry Price", "Exit Price", "Direction", "P&L"])
            df1 = df1.append({'Entry Price':df.Price[df.index[0]],'Exit Price':df.Price[df.index[-1]], 'Direction': 'Short', 'P&L': df.pnl_short[df.index[-1]] }, ignore_index=True)
            
            order_history.dataframe(df1)
            

            os.remove("df.csv")
            
            user.active = False
            sell = False
            closesell = False
        
        
        
        if user.active == True:
            df.to_csv('df.csv')

            
        match_orders(i)
        
        
             
        ### SI la orden del usuario se matcheo... Mostrar el proceso
        #0 = active, 1 = called, 3 = liquidated
        
        if user.active == True:  
            df.loc[i,'Price'] = trades['Price'][len(trades)-1] 
            entryprice = df.loc[df.index[0],'Price']
            df.loc[i,"risk_long"] = leverage * (((df.loc[i,"Price"]) / entryprice) -1)
            df.loc[i,"risk_short"] = -leverage * (((df.loc[i,"Price"]) / entryprice) -1)
            
            df.loc[i,"pnl_long"] = ((df.loc[i,"Price"] / entryprice) -1) * cantidad * entryprice
            df.loc[i,"pnl_short"] = -((df.loc[i,"Price"] / entryprice) -1) * cantidad * entryprice
    
            df.loc[i,'margin_long'] = round(df.iloc[-1,3]+df.iloc[-2,1],2) 
            df.loc[i,'margin_short'] = round(df.iloc[-1,4]+df.iloc[-2,2],2)

            df.loc[i, 'balance_long'] = user.usdt
            df.loc[i, 'balance_short'] = user.usdt
            
            """
            df2 = pd.DataFrame(columns = ["Values", "Names"], index=["Margin Long", "Margin Short"])
            df2.Names["Long"] = "Margin Long"
            df2.Names["Short"] = "Margin Short"
            df2.Values["Long"] = df.loc[-1,'margin_long'][-1]
            df2.Values["Short"] = df.loc[-1,'margin_short'][-1]
            """
            #fig = px.pie(df2, values='Values', names='Names')
            #margin_plot.write(fig)
            margin_plot.bar_chart(df[['margin_long', 'margin_short']])
            #margin_plot.bar_chart(df2.Values)
            #Long
            if df.loc[i,"risk_long"] < -0.50 and df.loc[i,"risk_long"] > -0.8:
                df.loc[i,"state_long"] = 1
                #print(df)
                print(f"Hey, {user.name}, you just got a margin call ! Add more funds !")
        
            elif df.loc[i,"risk_long"] < -0.8:                 
                df.loc[i,"state_long"] = 3
                print("Your position has been liquidated !")
                
                user.active = False
                buy = False
                closebuy = False
                
                
            #Short
            if df.loc[i,"risk_short"] < -0.50 and df.loc[i,"risk_short"] > -0.8:
                df.loc[i,"state_short"] = 1
                print(f"Hey, {user.name}, you just got a margin call ! Add more funds !")
                
                    
            elif df.loc[i,"risk_short"] < -0.8:
                df.loc[i,"state_short"] = 3
                print("Your position has been liquidated !")
                
                user.active = False
                sell = False
                closesell = False
                
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
        print(f'User state: {user.active}')
        balance_slot.write(f'User balance: {round(user.usdt,2)}')
        
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
        
event_loop([main()])








