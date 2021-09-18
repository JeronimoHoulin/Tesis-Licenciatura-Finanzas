import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

#Obtain last BTC price
btc = yf.download("BTC-USD",period="1m")
btc = btc['Close'][0]

#Create User class which has its own properties
class User:    
    def __init__(self, name, init_btc_balance):
        self.name = name
        self.btc_balance = init_btc_balance
        self.unrealised_pnl = 0
        self.dollar_balance = float(self.btc_balance*btc)+self.unrealised_pnl
        
    def settlement(self,index):        
        self.btc_balance = self.btc_balance+self.unrealised_pnl/btc_price[index]
        self.dollar_balance = self.btc_balance*btc_price[index]
    
    def show_stats(self):
        print("BTC amount: {}\nDollars: ${}".format(self.btc_balance, self.dollar_balance))
        
user_1 = User('Juan', 1)
user_2 = User('Jero', 1)

#Price path simulation by geometric brownian motion with drift
def brownian_motion(S0, u, rf, num_days, sigma):
    dt = 1/360
    price_series = [S0]
    for i in range(num_days):
        price_series.append(price_series[-1]*(1+u*dt + sigma * np.random.normal(0, 1) * np.sqrt(dt)))
    return price_series 

stock_price = brownian_motion(10, 0.1, 0.025, 30, 0.12)
btc_price = brownian_motion(btc, 0.1, 0.025, 30, 0.2)
#Graph of the price path 
def plot():
    fig, ax1 = plt.subplots()
    ax1.set_xlabel('Days')
    ax1.set_ylabel('Stock', color="red")
    ax1.plot(range(0,31),stock_price, color="red")
    
    ax2 = ax1.twinx()
    ax2.set_ylabel('Bitcoin', color="blue")
    ax2.plot(range(0,31), btc_price, color="blue")
    fig.tight_layout()
    plt.show()
plot()



#Let's suppose that user 1 goes long on 1000 stocks at $10 for 30 days. 
#Tot pos size: 1000*$10=$10.000. With 10:1 leverage he only needs 10% or $1000.
#For security if a client's account balance drops bellow 50% of the initial margin 
# his position will be automatically liquidated
def open_position(user_long, user_short, init_price, q, leverage):
    
    required_collateral = init_price*q*leverage
    print("Required collateral in btc {} \n ----".format(required_collateral/btc_price[0]))
    initialcap_long = user_long.dollar_balance
    initialcap_short = user_short.dollar_balance
    spread = init_price*0.01
    company_profit = 0
    #Check that users have enough collateral
    if user_long.dollar_balance < required_collateral:
        print("Not enough collateral to enter trade")
    elif user_short.dollar_balance < required_collateral:
        print("Not enough collateral to enter trade")
      
    else:
        company_profit += (spread*q)*2
        #This loop simulates the funcions that the smart contract would perform          
        for i in range(1, len(stock_price)):
            #Calculate unrealised pnl in function of the stock price
            user_long.unrealised_pnl = (stock_price[i]-(init_price+spread))*q
            user_short.unrealised_pnl = ((init_price+spread)-stock_price[i])*q
            
            #Distribute the payoffs in BTC and recalculate user balance
            user_long.settlement(i)
            user_short.settlement(i)
            
            #Check that users have enough collateral to maintain the position open
            if user_long.dollar_balance < 0.5*required_collateral:
                print("{}'s position was closed due to margin call\nat day {}".format(user_long.name, i))                     
                break
            elif user_short.dollar_balance < 0.5*required_collateral:
                print("{}'s position was closed due to margin call\nat day {}".format(user_short.name, i))
                break
        #Add the profit or loss to users account in BTC
        total_pnl_long = user_long.dollar_balance-initialcap_long
        print("User that went long realised PnL: {}".format(total_pnl_long))
        print("Hedge future PnL {}\n".format((btc_price[-1]-btc_price[0])*required_collateral/btc_price[0])) 
        total_pnl_short = user_short.dollar_balance-initialcap_short
        print("User that went short realised PnL: {}".format(total_pnl_short))
        print("Hedge future PnL {}\n".format((btc_price[0]-btc_price[-1])*required_collateral/btc_price[0])) 

open_position(user_1, user_2, 10, 10000, 0.1)        

#def hedge_future(btc_price):
    

user_1.show_stats()
user_2.show_stats()
#Reset the stats
user_1 = User('Juan', 1)
user_2 = User('Jero', 1)
    

