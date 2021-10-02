"""
Created on Sat Sep 18 09:49:34 2021
Jero & Juan
"""
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import random as rd
import string
import asyncio


# Definir su activo subyacente
#subyacente = "AAPL"

#subya = yf.download(f"{subyacente}",period="1m")['Close'][0]

def brownian_motion(S0, u, rf, num_days, sigma):  
    dt = 1/360
    price_series = [S0]
    for i in range(num_days):
        price_series.append(price_series[-1]*(1+u*dt + sigma * np.random.normal(0, 1) * np.sqrt(dt)))
    return price_series 

subyacente = brownian_motion(146, 0.1, 0.025, 90, 0.1)

# Definimos los agentes involucrados dado que conectaron sus billeteras virtuales
class user:    
    def __init__(self, name, wallet_id, usdt, active): 
        # Donde balance es el balance de stablecoins en la billetera de un usuario
        # Y la dirección es 1 para "LONG" y -1 para "SHORT"
        self.name = name
        self.wallet_id = wallet_id
        self.usdt = usdt
        self.active = active

# Estos fields van a venir de la interfaz        
user_long = user("Jero", "01234", 10000, True)
user_short = user("Juan","56789", 10000, True)     



# RISK MANAGEMENT TOOL (CENTRALIZED) Para los cálculos del margen de cada agente        


adress_gen = string.ascii_letters + string.digits



''' Order Book '''
def create_orders(buy=True, market_price=0):
    if buy:
        buy_orders = [subyacente[market_price]*(1-i/1500) for i in range(3)]
        buy_orders_size = [rd.randint(1, i) for i in range(100,10,-30)]
        address = [''.join(rd.choice(adress_gen) for i in range(10)) for j in range(3)]
        return [list(i) for i in zip(buy_orders, buy_orders_size, address)]
    else:
        sell_orders = [subyacente[market_price]*(1+i/1500) for i in range(3)]
        sell_orders_size = [rd.randint(1, i) for i in range(100,10,-30)]
        address = [''.join(rd.choice(adress_gen) for i in range(10)) for j in range(3)]
        return [list(i) for i in zip(sell_orders,sell_orders_size, address)]

trades = pd.DataFrame(columns=['Price','Size', 'Underlying Market Price'])

order_book_b = pd.DataFrame(create_orders(), columns=['Price', 'Size', 'Address']).sort_values(by=['Price'], ascending=False).reset_index(drop=True)
order_book_s = pd.DataFrame(create_orders(False), columns=['Price', 'Size', 'Address']).sort_values(by=['Price']).reset_index(drop=True)



#-----Entran los datos de la interfaz-----#
leverage, cantidad, entryprice_long, entryprice_short = 10, 1, subyacente[0], subyacente[0]



class user_order:
        self.leverage = leverage
        self.cantidad = cantidad
        self.direction = direction
        self.entry_price = entry_price              #User inputs... el active = true de user lo pondría aca.
        self.state = state 
        
user_order(10, 1, "long", subyacente[0], "sent") #sent / matched / closed









#Agrego la orden del usuario
order_book_b.loc[len(order_book_b)+1] = [entryprice_long,cantidad, user_long.wallet_id]
order_book_b = order_book_b.sort_values(by=['Price'], ascending=False).reset_index(drop=True)

#Devolver cuanto margen necesita poner cada usuario
init_margin_long =  entryprice_long * cantidad / leverage
init_margin_short = entryprice_short * cantidad / leverage

#Checkeo de si les dá el balance en USDT para entrar en el contrato
if init_margin_long > user_long.usdt:
    print("Long cannot enter position, margin need's more funds !")
elif init_margin_short > user_short.usdt:
    print("Short cannot enter position, margin need's more funds !")

df = pd.DataFrame({'Price':subyacente[0], 'margin_long':init_margin_long, 'margin_short':init_margin_short,
                  'pnl_long':0, 'pnl_short':0, 'state_long':np.nan, 'state_short':np.nan, 'risk_long':0, 'risk_short':0}, index=[0])

trade_num = 0
long_add = 0
short_add = 0
#while df.loc[i-1,'state_long'] != 'Liquidated' and df.loc[i-1,'state_short'] != 'Liquidated':
for i in range(1,len(subyacente)):
    
    while max(order_book_b['Price']) >= min(order_book_s['Price']):
        if order_book_b['Price'][0] >= order_book_s['Price'][0]:
            trade_num += 1 
            price = order_book_b['Price'][0]
            size = min(order_book_b['Size'][0], order_book_s['Size'][0])
            trades.loc[trade_num]=[price, size, subyacente[i]]
            print(f'{size} matched at {round(price,2)}')
            
            order_book_b['Size'][0] -= size 
            order_book_s['Size'][0] -= size 
            
            if order_book_b['Size'][0] == 0:
                order_book_b = order_book_b.drop(0).reset_index(drop=True)
                
            if order_book_s['Size'][0] == 0:
                order_book_s = order_book_s.drop(0).reset_index(drop=True)

    ###
    if user_long.wallet_id not in order_book_b:
        df.loc[i,'Price'] = trades['Price'][len(trades)] #Suponiendo q gabo. (en todo el script long=GABO)
        
        df.loc[i,"risk_long"] = leverage * (((df.loc[i,"Price"] + long_add) / entryprice_long) -1)
        df.loc[i,"risk_short"] = -leverage * (((df.loc[i,"Price"] - short_add) / entryprice_short) -1)
        
        df.loc[i,"pnl_long"] = ((df.loc[i,"Price"] / entryprice_long) -1) * cantidad * entryprice_long
        df.loc[i,"pnl_short"] = -((df.loc[i,"Price"] / entryprice_short) -1) * cantidad * entryprice_long
        
        df.loc[i,'margin_long'] = df.loc[i, 'pnl_long']+df.loc[0,'margin_long'] + long_add
        df.loc[i,'margin_short'] = df.loc[i, 'pnl_short']+df.loc[0,'margin_short'] + short_add
    
        
        #Long
        if df.loc[i,"risk_long"] < -0.50 and df.loc[i,"risk_long"] > -0.8:
            df.loc[i,"state_long"] = "Called"
            print(df)
            print(f"Hey, {user_long.name}, you just got a margin call ! Add more funds !")
            
            #Long agrega fondos
            long_ask = float(input("Add USDT to margin:"))
            
            if long_ask > user_long.usdt - init_margin_long:
                print("You don't have enough USDT in the wallet !")
                long_add += 0
            else:
                long_add += long_ask
    
            
        elif df.loc[i,"risk_long"] < -0.8:                 
            df.loc[i,"state_long"] = "Liquidated"
            print("Your position has been liquidated !")
            
            
        elif df.loc[i,"risk_long"] > -0.5:
             long_add += 0
            
        #Short
        if df.loc[i,"risk_short"] < -0.50 and df.loc[i,"risk_short"] > -0.8:
            df.loc[i,"state_short"] = "Called"
            print(f"Hey, {user_short.name}, you just got a margin call ! Add more funds !")
            
            #Short agrega fondos
            short_ask = float(input("Add USDT to margin:"))    
            
            if short_ask > user_short.usdt - init_margin_short:
                print("You don't have enough USDT in the wallet !")
                short_add += 0
            else:
                short_add += short_ask
                
        elif df.loc[i,"risk_short"] < -0.8:
            df.loc[i,"state_short"] = "Liquidated"
            print("Your position has been liquidated !")
            
        elif df.loc[i,"risk_long"] > -0.5:
             short_add += 0
 
    #New orders so the order book keeps running
    new_buy_orders=create_orders(market_price=i)
    for order in range(3):
        order_book_b.loc[len(order_book_b)+i] = new_buy_orders[order]
    order_book_b = order_book_b.sort_values(by=['Price'], ascending=False).reset_index(drop=True)
    
    new_sell_orders=create_orders(False,market_price=i)
    for order in range(3):
        order_book_s.loc[len(order_book_s)+i] = new_sell_orders[order]
    order_book_s = order_book_s.sort_values(by=['Price']).reset_index(drop=True)

    #User Inputs; ODERS
    
    






#Smart contract
def smart_contract(user_order):  #necesitamos la variable de user order..
    
    if user_order.state = closed:
        
        
        
    
    
    
    

    
