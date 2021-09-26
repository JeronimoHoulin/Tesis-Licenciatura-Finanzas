"""
Created on Sat Sep 18 09:49:34 2021
Jero & Juan
"""
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt


# Definir su activo subyacente
#subyacente = "AAPL"

#subya = yf.download(f"{subyacente}",period="1m")['Close'][0]

# OPCIÓN 1: Simulación del subyacente con Movimiento Browniano con drift.
#VARIABLES
u = 0.1
rf = 0.025                                      
num_days = 80
sigma = 0.01

def brownian_motion(S0, u, rf, num_days, sigma):  
    dt = 1/360
    price_series = [S0]
    for i in range(num_days):
        price_series.append(price_series[-1]*(1+u*dt + sigma * np.random.normal(0, 1) * np.sqrt(dt)))
    return price_series 

subyacente = brownian_motion(146, u, rf, num_days, sigma)

# Definimos los agentes involucrados dado que conectaron sus billeteras virtuales
class user:    
    def __init__(self, name, wallet_id, usdt, direction, active, leverage): 
        # Donde balance es el balance de stablecoins en la billetera de un usuario
        # Y la dirección es 1 para "LONG" y -1 para "SHORT"
        self.name = name
        self.wallet_id = wallet_id
        self.usdt = usdt
        self.direction = direction
        self.active = active
        self.leverage = leverage
        
user_long = user("Jero", "01234", 10000, 1, True, 10)
user_short = user("Juan","56789", 10000, -1, True, 100)     

cantidad, entryprice_long, entryprice_short = 1, subyacente[0], subyacente[0]

# RISK MANAGEMENT TOOL (CENTRALIZED) Para los cálculos del margen de cada agente        

#Devolver cuanto margen necesita poner cada usuario
init_margin_long =  entryprice_long * cantidad / user_long.leverage
init_margin_short = entryprice_short * cantidad / user_short.leverage

#Checkeo de si les dá el balance en USDT para entrar en el contrato
if init_margin_long > user_long.usdt:
    print("Long cannot enter position, margin need's more funds !")
elif init_margin_short > user_short.usdt:
    print("Short cannot enter position, margin need's more funds !")


long_add = 0
short_add = 0

df = pd.DataFrame({'Price':subyacente[0], 'margin_long':init_margin_long, 'margin_short':init_margin_short,
                  'pnl_long':0, 'pnl_short':0, 'state_long':np.nan, 'state_short':np.nan, 'risk_long':0, 'risk_short':0}, index=[0])



i = 1
while df.loc[i-1,'state_long'] != 'Liquidated' and df.loc[i-1,'state_short'] != 'Liquidated':
    df.loc[i,'Price'] = subyacente[i]
    
    df.loc[i,"risk_long"] = user_long.leverage * (((df.loc[i,"Price"] + long_add) / entryprice_long) -1)
    df.loc[i,"risk_short"] = -user_short.leverage * (((df.loc[i,"Price"] - short_add) / entryprice_short) -1)
    
    df.loc[i,"pnl_long"] = ((df.loc[i,"Price"] / entryprice_long) -1) * cantidad * entryprice_long
    df.loc[i,"pnl_short"] = -((df.loc[i,"Price"] / entryprice_short) -1) * cantidad * entryprice_long
    
    df.loc[i,'margin_long'] = df.loc[i, 'pnl_long']+df.loc[0,'margin_long'] + long_add
    df.loc[i,'margin_short'] = df.loc[i, 'pnl_short']+df.loc[0,'margin_short'] + short_add

    
    #Long
        # SI mi PNL POR leverage es menor a -0.8 ; CALL
    if df.loc[i,"risk_long"] < -0.50 and df.loc[i,"risk_long"] > -0.8:
    #if sub["margin_long"][i] < 0.5*init_margin_long and sub["margin_long"][i] > 0.25*init_margin_long:      ##agregado de otra condicion
        df.loc[i,"margin_state_long"] = "Called"
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
    #if sub["margin_short"][i] < 0.5*init_margin_short and sub["margin_short"][i] > 0.25*init_margin_long:
        df.loc[i,"state_short"] = "Called"
        print(df)
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
         
    if i >= len(subyacente)-1:
        break     
    i += 1

# IF SALIDO 
    
    

# Simulación del Smart Contract, dado el movimiento del subyacente. 


# Definir el wallet del smart contract
# AGARRA INFO DEL TOOL Y DEL USUARIO, Y HACE LA TRANSFERENCIA / SETTLEMENT.
# SOLO EJECUTA POR TEMA DE PESO DEL CÓDIGO
def smart_contract (user_long, user_short, ):
    
    #ARMA UN FONDO = margin pool (que tiene una wallet id)
    
    
    
