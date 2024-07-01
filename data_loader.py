import os
import gspread
import pandas as pd
import yfinance as yf
from oauth2client.service_account import ServiceAccountCredentials

from data_preprocessor import TransactionDataPreprocessing


class DataLoader:
    
    def __init__(self):
        pass
        # self.transaction_data = None
        # self.sectors_data = None
        # self.daily_prices = None
    
    def get_daily_prices_data(self, tickers, start_time):
        """
        Get daily prices for a list of tickers from Yahoo Finance
        """
        daily_price = {}
        for t in tickers:
            ticker_price_history = yf.Ticker(t).history(period='1d', start=start_time, auto_adjust=False)
            ticker_price_history.index = pd.to_datetime(ticker_price_history.index).strftime('%Y-%m-%d')
            daily_price[t] = ticker_price_history.to_dict()['Close']
            
        return daily_price

    def get_transaction_data(self):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # Print current working directory
        print(f"Current working directory: {os.getcwd()}")

        # Check if the file exists
        if os.path.isfile('secrets/cred.json'):
            print("File 'secrets/cred.json' exists")
        else:
            print("File 'secrets/cred.json' does not exist")
        
        creds = ServiceAccountCredentials.from_json_keyfile_name('secrets/creds.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open("dividend_data").sheet1  # Open the first sheet
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        return df

    def get_sectors_data(self):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name('secrets/cred.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open("sectors").sheet1  # Open the first sheet
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        return df

    def run(self):
    # Fetch table data from Google Sheets
        transaction_data = self.get_transaction_data()
        transaction_preprocessor = TransactionDataPreprocessing(transaction_data)
        transaction_preprocessor.run()
        transaction_data = transaction_preprocessor.df.copy()
        sectors_data = self.get_sectors_data()
        daily_prices = self.get_daily_prices_data(transaction_data.ticker.unique(), transaction_data.date.min())
        
        return transaction_data, sectors_data, daily_prices