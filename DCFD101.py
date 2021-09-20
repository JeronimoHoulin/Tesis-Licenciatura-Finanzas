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

sub = yf.download(f"{subyacente}",period="1m")['Close'][0]

# OPCIÓN 1: Simulación del subyacente con Movimiento Browniano con drift.
def brownian_motion(S0, u, rf, num_days, sigma):  #efinimos sus variables
    dt = 1/360
    price_series = [S0]
    for i in range(num_days):
        price_series.append(price_series[-1]*(1+u*dt + sigma * np.random.normal(0, 1) * np.sqrt(dt)))
    return price_series 

subyacente = brownian_motion(sub, 0.1, 0.025, 30, 0.3)

def plot():
    fig, ax1 = plt.subplots()
    ax1.set_xlabel('Días')
    ax1.set_ylabel('Subyacente', color="blue")
    ax1.plot(range(0,31),subyacente, color="blue")
    
    fig.tight_layout()
    plt.show()
plot()



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
        
user_long = user("Jero", "01234", 10000, 1, True, 0.01)
user_short = user("Juan","56789", 10000, -1, True, 0.01)



#Donde guardo mis rdos de la simulacion
sub = pd.DataFrame(subyacente, columns = ["Subyacente"])



# RISK MANAGEMENT TOOL (CENTRALIZED) Para los cálculos del margen de cada agente
def tool (user_long, user_short, subyacente, cantidad): #DONDE CANTIDAD DE CONTRATOS TIENE QUE COINCIDIR
        
    # DATOS INICIALES T = 0
    #Crear el margin pool
    margin_pool = subyacente[0] * cantidad * ( user_short.leverage + user_long.leverage)
    print("\n \n Margin pool total:", round(margin_pool,2))
    
    #Devolver cuanto margen necesita poner cada usuario
    init_margin_long = user_long.leverage * subyacente[0] * cantidad
    init_margin_short = user_short.leverage * subyacente[0] * cantidad
    
    #Checkeo de si les dá el balance en USDT para entrar en el contrato
    if init_margin_long > user_long.usdt:
        print("Long cannot enter position, margin need's more funds !")
    elif init_margin_short > user_short.usdt:
        print("Short cannot enter position, margin need's more funds !")
        
    # ARRAYS SEGÚN MOVIMIENTOS DE SUBYACENTE
    #sub = pd.DataFrame(subyacente, columns = ["Subyacente"])
    sub["Change ($)"] = sub['Subyacente']-sub['Subyacente'].shift(1)
    
    sub["unreal_long"] = sub["Change ($)"]*cantidad
    sub["unreal_short"] = -sub["Change ($)"]*cantidad
    
    sub["margin_long"] = sub["unreal_long"] + init_margin_long                                  #CAMBIO 1
    sub["margin_short"] = -sub["unreal_short"] + init_margin_short
    
    sub["margin_long"][0] = init_margin_long
    sub["margin_short"][0] = init_margin_short
    
    # CHECKEO de que en todo momento el nivel de margen en el pool coincida con el margen de las dos cuentas
    # Tiene que ser en todo momento = 1460.6
    sub["check"] = sub["margin_long"]+ sub["margin_short"]
    
    
    # MARGIN CALLS dados = 50% call; 25% liquidation
    sub["margin_state_long"] = 0
    sub["margin_state_short"] = 0
    
    long_add = 0
    short_add = 0
    
    for i in range(len(sub)):
        
        #Sucesión de las cuentas de margen, el margen de hoy es el de ayer más lo que se agrgó y el unreal pnl:
        if i != 0:
            sub["margin_long"][i] =  sub["margin_long"][i-1] + long_add + sub["unreal_long"][i]
            sub["margin_short"][i] =  sub["margin_short"][i-1] + short_add + sub["unreal_short"][i]
            
        #Long
        
        if sub["margin_long"][i] < 0.5*init_margin_long:
            sub["margin_state_long"][i] = "Called"
            print(f"Hey, {user_long.name}, you just got a margin call ! Add more funds !")
            
            #Long agrega fondos
            long_add = int(input("Add USDT to margin:"))
            
            if long_add > user_long.usdt - init_margin_long:
                print("You don't have enough USDT in the wallet !")
                long_add = 0

            
        elif sub["margin_long"][i] < 0.25*(init_margin_long + long_add):
            sub["margin_state_long"][i] = "Liquidated"
            print("You'r position has been liquidated !")
            break
            
        
        elif sub["margin_long"][i] > 0.5*init_margin_long:
             long_add = 0
            
        #Short
            
        if sub["margin_short"][i] < 0.5*init_margin_short:
            sub["margin_state_short"][i] = "Called"
            print(f"Hey, {user_short.name}, you just got a margin call ! Add more funds !")
            
            #Short agrega fondos
            short_add = int(input("Add USDT to margin:"))            
            if short_add > user_short.usdt - init_margin_long:
                print("You don't have enough USDT in the wallet !")
                short_add = 0
                
        elif sub["margin_short"][i] < 0.25*(init_margin_short + short_add):
            sub["margin_state_short"][i] = "Liquidated"
            print("You'r position has been liquidated !")
            
            
        elif sub["margin_short"][i] > 0.5*init_margin_short:
             short_add = 0
    
    
    
tool(user_long, user_short, subyacente, 100)
"user_long, user_short, subyacente, cantidad = user_long, user_short, subyacente, 100"


# Simulación del Smart Contract, dado el movimiento del subyacente. 


# Definir el wallet del smart contract
# AGARRA INFO DEL TOOL Y DEL USUARIO, Y HACE LA TRANSFERENCIA / SETTLEMENT.
# SOLO EJECUTA POR TEMA DE PESO DEL CÓDIGO
def smart_contract ():


















































