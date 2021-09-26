"""
Created on Sat Sep 18 09:49:34 2021
Jero & Juan
"""
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt


# Definir su activo subyacente
subyacente = "AAPL"

subya = yf.download(f"{subyacente}",period="1m")['Close'][0]

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

subyacente = brownian_motion(subya, u, rf, num_days, sigma)

def plot():
    fig, ax1 = plt.subplots()
    ax1.set_xlabel('Días')
    ax1.set_ylabel('Subyacente', color="blue")
    ax1.plot(range(0,num_days+1),subyacente, color="blue")
    
    fig.tight_layout()
    plt.show()
plot()



#Donde guardo mis rdos de la simulacion
sub = pd.DataFrame(subyacente, columns = ["Subyacente"])

# OPCIÓN 2: XXX


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
        
        self.unrealised_pnl = 0
        
user_long = user("Jero", "01234", 10000, 1, True, 100)
user_short = user("Juan","56789", 10000, -1, True, 100)      #Cambio de formato de leverage







#variables
user_long, user_short, subyacente, cantidad = user_long, user_short, subyacente, 1




#Oder book






entryprice_long = subya
entryprice_short = subya




# RISK MANAGEMENT TOOL (CENTRALIZED) Para los cálculos del margen de cada agente        
# DATOS INICIALES T = 0
#Crear el margin pool
margin_pool = (entryprice_long * cantidad) / user_long.leverage   +   (entryprice_short * cantidad) / user_short.leverage
print("\n \n Margin pool total:", round(margin_pool,2))

#Devolver cuanto margen necesita poner cada usuario
init_margin_long =  subya * cantidad / user_long.leverage
init_margin_short = subya * cantidad / user_short.leverage

#Checkeo de si les dá el balance en USDT para entrar en el contrato
if init_margin_long > user_long.usdt:
    print("Long cannot enter position, margin need's more funds !")
elif init_margin_short > user_short.usdt:
    print("Short cannot enter position, margin need's more funds !")
    




sub["margin_long"] = init_margin_long
sub["margin_short"] = init_margin_short


sub["Change ($)"] = sub['Subyacente']-sub['Subyacente'].shift(1)

sub["unreal_long"] = sub["Change ($)"]*cantidad
sub["unreal_short"] = -sub["Change ($)"]*cantidad

sub["margin_long1"] = sub["unreal_long"] + init_margin_long                                  #CAMBIO 1
sub["margin_short1"] = -sub["unreal_short"] + init_margin_short

sub["margin_long1"][0] = init_margin_long
sub["margin_short1"][0] = init_margin_short


sub["check"] = sub["margin_long"]+ sub["margin_short"]

# MARGIN CALLS dados = 50% call; 25% liquidation
sub["margin_state_long"] = 0
sub["margin_state_short"] = 0





long_add = 0
short_add = 0

for i in range(len(sub)):
    
    sub["long_risk"][i] = user_long.leverage * (((sub["Subyacente"][i] + long_add) / entryprice_long) -1)
    sub["short_risk"][i] = -user_short.leverage * (((sub["Subyacente"][i] - short_add) / entryprice_short) -1 )
    
    sub["longpnl"] = ((sub["Subyacente"] / entryprice_long) -1) * cantidad * entryprice_long
    sub["shortpnl"] = -((sub["Subyacente"] / entryprice_short) -1) * cantidad * entryprice_long
    
    
    #Sucesión de las cuentas de margen, el margen de hoy es el de ayer más lo que se agrgó y el unreal pnl:
    if i != 0:
        sub["margin_long"][i] =  sub["margin_long"][i-1] + long_add + sub["longpnl"][i] - sub["longpnl"][i-1]
        sub["margin_short"][i] =  sub["margin_short"][i-1] + short_add + sub["shortpnl"][i]- sub["shortpnl"][i-1]
        
        sub["margin_long1"][i] =  sub["margin_long1"][i-1] + long_add + sub["unreal_long"][i]
        sub["margin_short1"][i] =  sub["margin_short1"][i-1] + short_add + sub["unreal_short"][i]
        
    #Long
        # SI mi PNL POR leverage es menor a -0.8 ; CALL
    if sub["long_risk"][i] < -0.50 and sub["long_risk"] > -0.8:
    #if sub["margin_long"][i] < 0.5*init_margin_long and sub["margin_long"][i] > 0.25*init_margin_long:      ##agregado de otra condicion
        sub["margin_state_long"][i] = "Called"
        print(f"Hey, {user_long.name}, you just got a margin call ! Add more funds !")
        
        #Long agrega fondos
        long_ask = float(input("Add USDT to margin:"))
        
        if long_ask > user_long.usdt - init_margin_long:
            print("You don't have enough USDT in the wallet !")
            long_add += 0
        else:
            long_add += long_ask

        
    elif sub["long_risk"][i] < -0.8:                 #Cambios de esto: 0.25*init_margin_long + long_add
        sub["margin_state_long"][i] = "Liquidated"
        print("You'r position has been liquidated !")
        break
        
    
    elif sub["long_risk"][i] > -0.5:
         long_add += 0
        
    #Short
    
    if sub["short_risk"][i] < -0.50 and sub["short_risk"][i] > -0.8:
    #if sub["margin_short"][i] < 0.5*init_margin_short and sub["margin_short"][i] > 0.25*init_margin_long:
        sub["margin_state_short"][i] = "Called"
        print(f"Hey, {user_short.name}, you just got a margin call ! Add more funds !")
        
        #Short agrega fondos
        short_ask = float(input("Add USDT to margin:"))    
        
        if short_ask > user_short.usdt - init_margin_short:
            print("You don't have enough USDT in the wallet !")
            short_add += 0
        else:
            short_add += short_ask
            
    elif sub["short_risk"][i] < -0.8:
        sub["margin_state_short"][i] = "Liquidated"
        print("You'r position has been liquidated !")
        
        
    elif sub["short_risk"][i] > -0.5:
         short_add += 0

# IF SALIDO 
    
    

# Simulación del Smart Contract, dado el movimiento del subyacente. 


# Definir el wallet del smart contract
# AGARRA INFO DEL TOOL Y DEL USUARIO, Y HACE LA TRANSFERENCIA / SETTLEMENT.
# SOLO EJECUTA POR TEMA DE PESO DEL CÓDIGO
def smart_contract (user_long, user_short, ):
    
    #ARMA UN FONDO = margin pool (que tiene una wallet id)
    
    
    
