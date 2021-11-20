""" Created on Sat Sep 18 09:49:34 2021 Jero & Juan """

import pandas as pd
import numpy as np
import time
import streamlit as st
import random as rd
import matplotlib.pyplot as plt
import string
import plotly.express as px

plt.style.use('dark_background')

st.set_page_config(layout="wide")

adress_gen = string.ascii_letters + string.digits

st.title("DCFD Decentralized Exchange")

st.sidebar.write('Trading Panel')
balance_slot = st.sidebar.empty()

ticker = st.sidebar.selectbox('Underlying: ', ('AAPL','GME'))
side1, side2= st.sidebar.columns(2)
with st.sidebar.form(key='form1'):
    leverage = st.slider('Select Leverage', min_value=(1), max_value=(10))
    cantidad = st.number_input('Enter Quantity', step =1, value=1)
    buy = st.form_submit_button('Long')
    sell = st.form_submit_button('Short')
    closep = st.form_submit_button('Close Position')
    #closesell = st.form_submit_button('Close Short')
   # print(f'{leverage}, {cantidad}, {buy}, {sell}, {closep} \n')
    
    
col1, col2 = st.columns([1, 2.5])
col1.write('Order Book')

plot_slot = col2.empty()
liquidated_pos = col2.empty()
order_history_title = col2.write('User order history')
order_history = col2.empty()
margin_plot = col2.empty()
trade_df = col2.empty()

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
        sum_to_transfer = df.loc[df.index[-1],'margin_long'] 
        user.usdt += sum_to_transfer
        self.balance -= sum_to_transfer
        print(f'{sum_to_transfer} TRANSFERRED TO USER \n')
        
    def send_back_short(self):
        sum_to_transfer =  df.loc[df.index[-1],'margin_short'] 
        user.usdt += sum_to_transfer
        self.balance -= sum_to_transfer
        print(f'{sum_to_transfer} TRANSFERRED TO USER \n')


smart_contract = smart_contract('abcd', 0) ##HAY QUE HACER QUE SE SUMEN LOS  MARGENES CUANDO UNO ENTRA EN UN CONTRATO
       

user =  user("Jero", "01234", 10000)


subyacente = pd.read_csv('sub.csv')


''' Order Book '''
def create_orders(market_price,buy=True):
    if buy:
        buy_orders_price = [market_price*(1-i/1500) for i in range(3)]
        buy_orders_size = [rd.randint(1, i) for i in np.linspace(10,50,3)]
        address = [''.join(rd.choice(adress_gen) for i in range(10)) for j in range(3)]
        return [list(i) for i in zip(buy_orders_price, buy_orders_size, address)]
    else:
        sell_orders_price = [market_price*(1+i/1500) for i in range(3)]
        sell_orders_size = [rd.randint(1, i) for i in np.linspace(10,50,3)]
        address = [''.join(rd.choice(adress_gen) for i in range(10)) for j in range(3)]
        return [list(i) for i in zip(sell_orders_price,sell_orders_size, address)]


order_book_b = pd.DataFrame(create_orders(subyacente['price'][0]), columns=['Price', 'Size', 'Address']).sort_values(by=['Price'], ascending=False).reset_index(drop=True)
order_book_s = pd.DataFrame(create_orders(subyacente['price'][0],False), columns=['Price', 'Size', 'Address']).sort_values(by=['Price']).reset_index(drop=True)

trades = pd.DataFrame(columns=['Price','Size', 'MP', 'Contract id'])

def match_orders(i):
    global order_book_b, order_book_s
    while max(order_book_b['Price']) >= min(order_book_s['Price']):
        if order_book_b['Price'][0] >= order_book_s['Price'][0]:
            price = order_book_b['Price'][0]
            size = min(order_book_b['Size'][0], order_book_s['Size'][0])
            contract_id = order_book_b['Address'][0]
            trades.loc[contract_id]=[price, size, i, contract_id]
            info_slot.subheader(f'\n {size} DCFDs entered at ${round(price,2)}')
            
            order_book_b.loc[0,'Size'] -= size 
            order_book_s.loc[0,'Size'] -= size 
            
            if order_book_b.loc[0,'Size'] == 0:
                order_book_b = order_book_b.drop(0).reset_index(drop=True)
                
            if order_book_s.loc[0,'Size'] == 0:
                order_book_s = order_book_s.drop(0).reset_index(drop=True)

def init_trade_df(i, init_margin): # Creamos el DF que muestra la evolucion del trade. Magins, PnL and Risk levels
    df = pd.DataFrame()
    df.loc[0, ['Price', 'margin_long', 'margin_short','pnl_long','pnl_short', 'state_long','state_short', 'risk_long', 'risk_short', 'Balance']] = [i, init_margin, init_margin, 0, 0, 0, 0, 1, 1, user.usdt]
    return df  

df1 = pd.read_csv('order_history.csv')[["Entry Price", "Exit Price", "Direction", "P&L", "Balance"]]
if len(df1)>0:
    user.usdt = df1.Balance[df1.index[-1]]


    
# RISK MANAGEMENT TOOL (CENTRALIZED) Para los cálculos del margen de cada agente  
def main():
    global order_book_b, order_book_s, market_price, df, subyacente, leverage, cantidad, buy, sell, closep, df1
    while True:
        # LEYENDO Y GRAFICANDO EL MOVIMIENTO DEL SUBYACENTE GENERADO POR PRICEGEN NOTEBOOK
        try:
            subyacente = pd.read_csv('sub.csv')
        except:
            time.sleep(0.01)
            subyacente = pd.read_csv('sub.csv')
            
        fig = px.line(subyacente, x= subyacente.index, y=['price','Ema-5', 'Ema-20'], color_discrete_sequence = ['orange','red', 'green'], title='Underlying Asset Price')
        plot_slot.plotly_chart(fig)
        i = round(subyacente.loc[subyacente.index[-1],'price'],3)
        
        ## BUY orders ##
        if buy == True and user.active == False:
            user.active = True

            df = init_trade_df(i, i * cantidad / leverage) #Set the initial margin required to start the trade and create DF
            entryprice_long = entryprice_short = df.loc[df.index[0],'Price']
            user.usdt = user.usdt - i * cantidad / leverage # Le sustraemos el margen a la cuenta del usuario para el smart contract
            
            df1 = df1.append({'Entry Price':entryprice_long,'Exit Price':0, 'Quantity':cantidad, 'Direction': 'Long',
                              'P&L': 0, 'Balance': df.Balance[df.index[-1]]}, ignore_index=True)
            df1.to_csv('order_history.csv')
            order_history.dataframe(df1) #Show the user's open position
            
            
            
        ## SELL orders ##
        if sell == True and user.active == False: 
            user.active = True

            df = init_trade_df(i, i * cantidad / leverage)
            entryprice_long = entryprice_short = df.loc[df.index[0],'Price']
            user.usdt = user.usdt - i * cantidad / leverage

            df1 = df1.append({'Entry Price':entryprice_short,'Exit Price':0, 'Quantity':cantidad, 'Direction': 'Short',
                              'P&L': 0, 'Balance': df.Balance[df.index[-1]]}, ignore_index=True)
            df1.to_csv('order_history.csv')
            order_history.dataframe(df1) #Show the user's open position
            
        ## CLOSING orders ##   
        if closep == True:
            df = pd.read_csv('df.csv')
            
            if df1.loc[df1.index[-1], 'Direction'] == 'Long': 
                smart_contract.send_back_long() ##hacer que se envie en margen a wallet del smart.
                df1 = df1.append({'Entry Price':df.Price[df.index[0]],'Exit Price':df.Price[df.index[-1]], 'Quantity':cantidad, 'Direction': 'Long',
                                  'P&L': df.margin_long[df.index[-1]]-df.margin_long[df.index[0]], 'Balance': df.Balance[df.index[-1]]}, ignore_index=True)
                df1.to_csv('order_history.csv')
                order_history.dataframe(df1)
                print('Se ejecuto esto')
                user.active = False
                buy = False
                closep = False
                
            else:
                smart_contract.send_back_short() ##hacer que se envie en margen a wallet del smart.
                df1 = df1.append({'Entry Price':df.Price[df.index[0]],'Exit Price':df.Price[df.index[-1]], 'Quantity':cantidad, 'Direction': 'Short',
                                  'P&L': df.margin_short[df.index[-1]]-df.margin_short[df.index[0]], 'Balance': df.Balance[df.index[-1]]}, ignore_index=True)
                df1.to_csv('order_history.csv')
                order_history.dataframe(df1)
                print('Se ejecuto esto otro')
                user.active = False
                sell = False
                closep = False
            
    
            

        match_orders(i)
                
        ### SI la orden del usuario esta activa... Mostrar la evolucion.
        if user.active == True:
            df.to_csv('df.csv') 

            order_history.dataframe(df1)

            df.loc[i,'Price'] = trades['Price'][len(trades)-1]
            
            df.loc[i,"risk_long"] = df.loc[i,"margin_long"] / df.loc[df.index[0],"margin_long"]
            df.loc[i,"risk_short"] = df.loc[i,"margin_short"] / df.loc[df.index[0],"margin_short"]
            
            df.loc[i, 'pnl_long'] = (df.iloc[-1,0] - df.iloc[-2,0]) * cantidad
            df.loc[i,'pnl_short'] = -(df.iloc[-1,0] - df.iloc[-2,0]) * cantidad
    
            df.loc[i,'margin_long'] = round(df.iloc[-1,3]+df.iloc[-2,1],2) 
            df.loc[i,'margin_short'] = round(df.iloc[-1,4]+df.iloc[-2,2],2)

            if len(df1)>0: # CALCULAMOS EL BALANCE DEL USUARIO COMO USDT + PNL DE LA OPEN POSITION
                if buy==True:
                    df.loc[i, 'Balance'] = user.usdt + df.loc[df.index[-1],'margin_long'] - df.loc[df.index[0],'margin_long']
                if sell==True:
                    df.loc[i, 'Balance'] = user.usdt + df.loc[df.index[-1],'margin_short'] - df.loc[df.index[0],'margin_short']
            else:    
                if buy==True:
                    df.loc[i, 'Balance'] = user.usdt + df.loc[i,'margin_long']
                if sell==True:
                    df.loc[i, 'Balance'] = user.usdt + df.loc[i,'margin_short']
            

            #Long
            if df.loc[i,"risk_long"] < 0.50 and df.loc[i,"risk_long"] > 0.2:
                df.loc[i,"state_long"] = 1
        
            elif df.loc[i,"risk_long"] < 0.2:                 
                df.loc[i,"state_long"] = 3
                if buy == True:
                    liquidated_pos.write("Your position has been liquidated !")
                    smart_contract.send_back_long()
                    buy = False
                    user.active = False
                    df1 = df1.append({'Entry Price':df.Price[df.index[0]],'Exit Price':df.Price[df.index[-1]], 'Quantity':cantidad, 'Direction': 'Long',
                                      'P&L': df.margin_long[df.index[-1]]-df.margin_long[df.index[0]],
                                      'Balance': df.Balance[df.index[-1]]}, ignore_index=True)
                    df1.to_csv('order_history.csv')
                    order_history.dataframe(df1)
                    
                else:
                    liquidated_pos.write("Your counterparty position has been liquidated, New one took the trade.")
                    entryprice_short = df.loc[df.index[-1], 'Price']
                    df.loc[df.index[-1],['margin_short', 'pnl_short', 'risk_short', 'state_short']] = [entryprice_short * cantidad / leverage, 0, 1, 0] # RESETEAMOS EL DF DE LA TRADE DE LA COUNTERPARTY
                    
            
            #Short
            if df.loc[i,"risk_short"] < 0.50 and df.loc[i,"risk_short"] > 0.2:
                df.loc[i,"state_short"] = 1
                    
            elif df.loc[i,"risk_short"] < 0.2:
                df.loc[i,"state_short"] = 3
                if sell == True:
                    print("Your position has been liquidated !")
                    liquidated_pos.write("Your position has been liquidated !")
                    smart_contract.send_back_short()
                    sell = False
                    user.active = False
                    df1 = df1.append({'Entry Price':df.Price[df.index[0]],'Exit Price':df.Price[df.index[-1]], 'Quantity':cantidad, 'Direction': 'Short',
                                      'P&L': df.margin_short[df.index[-1]]-df.margin_short[df.index[0]],
                                      'Balance': df.Balance[df.index[-1]]}, ignore_index=True)
                    df1.to_csv('order_history.csv')
                    order_history.dataframe(df1)
                else:
                    
                    liquidated_pos.write("Your counterparty position has been liquidated, New one took the trade.")
                    entryprice_long = df.loc[df.index[-1], 'Price']
                    print(f"Your counterparty position's has been liquidated!, new entryprice long: {entryprice_long}")
                    df.loc[df.index[-1],['margin_short', 'pnl_short', 'risk_short', 'state_short']] = [entryprice_long * cantidad / leverage, 0, 1, 0] # RESETEAMOS EL DF DE LA TRADE DE LA COUNTERPARTY
                    
            trade_df.dataframe(df)
            
            if df.margin_long[df.index[-1]] > 0 and df.margin_short[df.index[-1]] > 0: #
                fig = px.pie(df, values=[df.margin_long[df.index[-1]], df.margin_short[df.index[-1]]], names=['User Long Margin','User Short Margin'], title='Smart Contract Margin Balance')
                margin_plot.plotly_chart(fig)
                 
    
        #New orders so the order book keeps running
        new_buy_orders=create_orders(i, True)
        for order in range(3):
            order_book_b.loc[len(order_book_b)+i] = new_buy_orders[order]
        order_book_b = order_book_b.sort_values(by=['Price'], ascending=False).reset_index(drop=True)
        
        new_sell_orders=create_orders(i,False)
        for order in range(3):
            order_book_s.loc[len(order_book_s)+i] = new_sell_orders[order]
        order_book_s = order_book_s.sort_values(by=['Price']).reset_index(drop=True)
        
        # Displaying things in Streamlit 
        metric_slot.metric(label='Underlying Price', value=round(i,2), delta=round(i-subyacente.loc[subyacente.index[-2], 'price'],3))
        trades_slot.dataframe(trades)
        sell_df.dataframe(order_book_s.sort_values(by=['Price'], ascending=False).reset_index(drop=True)[:9])
        buy_df.dataframe(order_book_b[:9])
        
        if len(df1)>0: #Si existe el df de order history tomar el balance de ahi.
            user.usdt = df1.Balance[df1.index[-1]]
        balance_slot.write(f'User balance: ${round(user.usdt,2)}')
        
        print(' \n ================================ \n')
        
        yield


def event_loop(tareas):
    while tareas:
        actual = tareas.pop(0)
        try:
            next(actual)
            tareas.append(actual)
        except StopIteration:
            pass
        
event_loop([main()])







