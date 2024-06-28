import requests
from datetime import datetime
import pandas as pd
import yfinance as yf

# headers and params used to bypass NASDAQ's anti-scraping mechanism in function __exchange2df
headers = {
    'authority': 'api.nasdaq.com',
    'accept': 'application/json, text/plain, */*',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
    'origin': 'https://www.nasdaq.com',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.nasdaq.com/',
    'accept-language': 'en-US,en;q=0.9',
}

def get_div_hist_per_stock(symbol:str):
    url = 'https://api.nasdaq.com/api/quote/' + symbol + '/dividends'
    params = {'assetclass' : 'stocks'}
    return __get_calendar_query(url, subcolumn=['dividends'], paramsin=params, symbolcol='exOrEffDate')

def __get_calendar_query(url:str, date:datetime = None, subcolumn:[str] = None, symbolcol:str = 'symbol', date_is_month:bool = False, paramsin=None):
    if paramsin is None:
        if date is None:
            if date_is_month:
                datestr = datetime.today().strftime('%Y-%m')
            else:
                datestr = datetime.today().strftime('%Y-%m-%d')
        else:
            if date_is_month:
                datestr = date.strftime('%Y-%m')
            else:
                datestr = date.strftime('%Y-%m-%d')

        params = {'date': datestr}
    else:
        params = paramsin
        
    response = requests.get(url, headers=headers, params=params)
    data = response.json()['data']
    if subcolumn is not None:
        for s in subcolumn:
           data = data[s]
    df = pd.DataFrame(data['rows'], columns=data['headers'])
    if len(df) > 0:
        df = df.set_index(symbolcol)
    return df

def _get_close_price(ticker):
    return yf.Ticker(ticker).history(period='1d').Close[0]