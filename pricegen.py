import yfinance as yf
import pandas as pd
import numpy as np
import time 

ticker = 'AAPL'
sub = yf.download(f"{ticker}",period="1m")['Close'][0]

def brownian_motion(df, u, rf, num_days, sigma):  
    dt = 1/360
    price = df.loc[df.index[-1]][0]*(1+u*dt + sigma * np.random.normal(0, 1) * np.sqrt(dt))
    df.loc[df.index[-1]+1] = price

price_series = pd.DataFrame(sub,columns=['price'], index=[0])
while True:
    brownian_motion(price_series, 0.1, 0.025, 1, 0.1)
    time.sleep(1)
    if len(price_series) > 50:
        price_series = price_series[-50:]
    price_series.to_csv('sub.csv')
